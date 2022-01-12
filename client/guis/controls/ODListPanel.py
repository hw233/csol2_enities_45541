# -*- coding: gb18030 -*-
#
# $Id: ListPanel.py,v 1.36 2008-08-25 07:06:18 huangyongwei Exp $

"""
implement list items panel calss
2009/01/20 : writen by huangyongwei
"""

"""
composing :
	WindowsGUIComponent
	scroll bar
"""

import math
import weakref
import Font
from guis import *
from guis.UIFixer import hfUILoader
from guis.controls.Control import Control
from guis.controls.ClipPanel import VClipPanel
from guis.controls.ScrollBar import VScrollBar
from guis.controls.StaticText import StaticText
from guis.tooluis.fulltext.FullText import FullText

class ODListPanel( VClipPanel ) :
	def __init__( self, panel, scrollBar, pyBinder = None ) :
		VClipPanel.__init__( self, panel, pyBinder )
		self.pySBar = VScrollBar( scrollBar )
		self.pySBar.scrollScale = 1
		self.pySBar.onScroll.bind( self.onScroll_ )

		self.__items = []						# 选项列表
		self.__pyViewItems = []					# 可视选项
		self.__itemHeight = 18.0				# 选项高度
		self.__ownerDraw = False				# 是否由用户重画
		self.__font = Font.defFont				# 选项默认字体

		self.__selectable = True				# 选项是否可被选中
		self.__selIndex = None					# 当前选中选项的索引
		self.__autoSelect = True				# 是否需要自动选择（为 True 时：如果删除了某个选中选项，则会自动选中它后面的选项）
		self.__mouseUpSelect = False			# 鼠标提起时选中选项
		self.__rMouseSelect = False				# 是否允许鼠标右键选中选项（功能与左键一样）
		self.__perScrollCount = 1				# 鼠标滚轮滚动一下时，实际滚动的选项数量
		
		self.__sbarState = ScrollBarST.AUTO								# 默认自动显示滚动条
		self.__isRedraw = True					# 是否会实时重画

		self.__initialize()

	def __del__( self ) :
		VClipPanel.__del__( self )
		if Debug.output_del_ODListPanel :
			INFO_MSG( str( self ) )

	def __initialize( self ) :
		self.mouseScrollFocus = True
		self.__itemForeColors = {}										# 选项默认的前景色
		self.__itemForeColors[UIState.COMMON] = 255, 255, 255, 255
		self.__itemForeColors[UIState.HIGHLIGHT] = 255, 255, 255, 255
		self.__itemForeColors[UIState.SELECTED] = 10, 255, 10, 255
		self.__itemForeColors[UIState.DISABLE] = 128, 128, 128, 255

		self.__itemBackColors = {}										# 选项默认的背景色
		self.__itemBackColors[UIState.COMMON] = 255, 255, 255, 0
		self.__itemBackColors[UIState.HIGHLIGHT] = 10, 36, 106, 255
		self.__itemBackColors[UIState.SELECTED] = 34, 61, 69, 255
		self.__itemBackColors[UIState.DISABLE] = 255, 255, 255, 0

		self.__updateScrollBar()										# 更新滚动条所能表达的内容


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		产生事件
		"""
		Control.generateEvents_( self )
		self.__onItemLClick = self.createEvent_( "onItemLClick" )						# 左键点击某选项时被触发
		self.__onItemRClick = self.createEvent_( "onItemRClick" )						# 右键点击某选项时被触发
		self.__onItemLDBClick = self.createEvent_( "onItemLDBClick" )					# 鼠标左键双击时被触发
		self.__onViewItemInitialized = self.createEvent_( "onViewItemInitialized" )		# 可视选项初始化时被触发
		self.__onDrawItem = self.createEvent_( "onDrawItem" )							# 选项需要重画时被触发
		self.__onItemSelectChanged = self.createEvent_( "onItemSelectChanged" )			# 选项需要重画时被触发
		self.__onItemMouseEnter = self.createEvent_( "onItemMouseEnter" )				# 鼠标进入选项是被触发
		self.__onItemMouseLeave = self.createEvent_( "onItemMouseLeave" )				# 鼠离开选项是被触发

	@property
	def onItemLClick( self ) :									# 左键点击某选项时被触发
		return self.__onItemLClick

	@property
	def onItemRClick( self ) :									# 右键点击某选项时被触发
		return self.__onItemRClick

	@property
	def onItemLDBClick( self ) :								# 鼠标左键双击时被触发
		return self.__onItemLDBClick

	@property
	def onViewItemInitialized( self ) :
		return self.__onViewItemInitialized						# 可视选项初始化时被触发

	@property
	def onDrawItem( self ) :									# 选项需要重画时被触发
		return self.__onDrawItem

	@property
	def onItemSelectChanged( self ) :							# 某个选项选中时被触发
		return self.__onItemSelectChanged

	@property
	def onItemMouseEnter( self ) :								# 鼠标进入选项时被
		return self.__onItemMouseEnter

	@property
	def onItemMouseLeave( self ) :								# 鼠标离开选项时被
		return self.__onItemMouseLeave


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __addViewItem( self, index ) :
		"""
		增加一个可视选项
		"""
		totalCount = int( math.ceil( self.height / self.__itemHeight ) )	# 版面上能够看到的最多选项数
		currCount = self.viewCount											# 当前的可视选项数量
		if currCount >= totalCount : return									# 如果当前可视选项数量已经达到最大，则不再添加
		pyViewItem = self.getViewItem_()
		self.addPyChild( pyViewItem )
		pyViewItem.width = self.width
		pyViewItem.height = self.__itemHeight
		pyViewItem.top = currCount * self.__itemHeight
		self.__pyViewItems.append( pyViewItem )
		pyViewItem.rebind_( index )
		self.onViewItemInitialized_( pyViewItem )
		self.onDrawItem_( pyViewItem )

	# -------------------------------------------------
	def __getHideHieight( self ) :
		"""
		获取所有隐藏内容的高度
		"""
		totleHeight = self.__itemHeight * self.itemCount
		return totleHeight - self.height

	def __getViewItem( self, index ) :
		"""
		获取指定索引对应的可视选项
		"""
		if self.viewCount :
			firstViewIdx = self.__pyViewItems[0].itemIndex
			lastViewIdx = self.__pyViewItems[-1].itemIndex
			if firstViewIdx <= index <= lastViewIdx :
				rindex = index - firstViewIdx
				return self.__pyViewItems[rindex]
		return None

	# -------------------------------------------------
	def __calcGap( self ) :
		"""
		如果版面高度并不恰好等于所有可视选项高度时
		需要通过版面的 scroll 属性来处理高出的缺口
		"""
		itemCount = self.itemCount
		if itemCount == 0 :
			self.maxScroll = 0
		else :
			pyLastViewItem = self.__pyViewItems[-1]
			gap = pyLastViewItem.bottom - self.height
			self.maxScroll = max( gap, 0 )

	def __updateScrollBar( self ) :
		"""
		更新滚动条
		"""
		viewHeight = self.height
		if viewHeight <= 0 : return
		totleHeight = self.itemCount * self.__itemHeight
		self.pySBar.scrollScale = totleHeight / viewHeight
		if totleHeight > viewHeight :
			hideHeight = totleHeight - viewHeight
			self.pySBar.perScroll = self.__itemHeight / hideHeight
		if self.__sbarState == ScrollBarST.AUTO:
			self.pySBar.visible = totleHeight - viewHeight - self.pySBar.perScroll / 10.0 > 0
		self.__calcGap()

	def __scrollTo( self, index ) :
		"""
		滚动到指定索引处，如果实际上滚动条并不需要滚动，则返回 False
		"""
		viewCount = self.viewCount
		if not viewCount : return False

		hideHeight = self.__getHideHieight()						# 不可见的选项总高度
		if hideHeight <= 0 :										# 全部选项都可见
			self.scroll = 0
			return False

		scrolled = True
		firstViewIdx = self.__pyViewItems[0].itemIndex
		lastViewIdx = self.__pyViewItems[-1].itemIndex
		if index < firstViewIdx :									# 如果 指定要滚动到的选项 隐藏在版面前面
			count = max( 0, index )
			hideTop = count * self.__itemHeight						# 上部分不可见选项的高度
			self.pySBar.value = hideTop / hideHeight				# 让指定索引选项作为第一个可视选项
		elif index > lastViewIdx :									# 如果 指定要滚动到的选项 隐藏在版面后面
			count = firstViewIdx + ( index - lastViewIdx )
			hideTop = count * self.__itemHeight						# 上部分不可见选项的高度
			self.pySBar.value = hideTop / hideHeight				# 让指定索引选项作为第一个可视选项
		else :
			scrolled = False

		firstViewIdx = self.__pyViewItems[0].itemIndex
		lastViewIdx = self.__pyViewItems[-1].itemIndex
		if index == firstViewIdx :									# 指定索引选项是第一个选项
			self.scroll = 0.0										# 则滚动版面，让选中选项作为第一个可视选项并全部可见
		elif index == lastViewIdx :									# 指定索引选项是最后一个选项
			self.scroll = self.maxScroll							# 则滚动版面，让选中选项作为最后一个可视选项并全部可见
		return scrolled

	# -------------------------------------------------
	def __redrawAllViewItems( self, firstViewIdx ) :
		"""
		重画所有选项，firstViewIdx 是第一个可视选项对应的选项索引
		"""
		for pyViewItem in self.__pyViewItems :
			pyViewItem.rebind_( firstViewIdx )
			self.onDrawItem_( pyViewItem )
			firstViewIdx += 1

	def __selectItem( self, index ) :
		"""
		选中指定索引选项（注意：不会触发选项选中事件），如果选择成功，则返回 True，否则返回 False
		"""
		oldSelIndex = self.__selIndex								# 记录下旧的选中索引
		self.__selIndex = index
		if index < 0 :												# 如果负索引
			pyOldSelViewItem = self.__getViewItem( oldSelIndex )	# 则取消当前选中的选项
			if pyOldSelViewItem :
				self.onDrawItem_( pyOldSelViewItem )				# 则通知重画旧的选中选项
		if not self.__scrollTo( index ) :							# 滚动到新选中的选项处( 无需滚动，则不需要重画 )
			pyNewSelViewItem = self.__getViewItem( index )
			if pyNewSelViewItem :
				self.onDrawItem_( pyNewSelViewItem )				# 通知重画新选中的选项

			pyOldSelViewItem = self.__getViewItem( oldSelIndex )	# 获取之前选中的选项所对应的可视选项
			if pyOldSelViewItem :									# 如果还可见
				self.onDrawItem_( pyOldSelViewItem )				# 则通知重画旧的选中选项

	def __autoSelectItem( self ) :
		"""
		自动选择一个选项
		"""
		if not self.__autoSelect :
			self.__selIndex = -1
		elif self.itemCount == 0 :
			self.__selIndex = -1
		elif self.__selIndex < 0 :
			self.__selIndex = 0
		elif self.__selIndex >= self.itemCount :
			self.__selIndex -= 1


	# ----------------------------------------------------------------
	# friend methods of ViewItem
	# ----------------------------------------------------------------
	def onViewItemLMouseDown_( self, pyViewItem, mods ) :
		"""
		鼠标左键在某个选项上按下时被调用
		"""
		self.tabStop = True
		if self.__selectable and not self.__mouseUpSelect :
			self.selIndex = pyViewItem.itemIndex
		return Control.onLMouseDown_( self, mods )

	def onViewItemLMouseUp_( self, pyViewItem, mods ) :
		"""
		鼠标左键在某选项上提起时被调用
		"""
		if self.__selectable and self.__mouseUpSelect :
			self.selIndex = pyViewItem.itemIndex
		return Control.onLMouseUp_( self, mods )

	def onViewItemLClick_( self, pyViewItem, mods ) :
		"""
		当左键点击可视选项时被调用
		"""
		self.onItemLClick( pyViewItem.itemIndex )
		return Control.onLClick_( self, mods )

	def onViewItemRMouseDown_( self, pyViewItem, mods ) :
		"""
		当鼠标右键点在可视选项上按下时被调用
		"""
		self.tabStop = True
		if self.__selectable and self.__rMouseSelect and \
			not self.__mouseUpSelect :
				self.selIndex = pyViewItem.itemIndex		# 则选中鼠标击中的选项
		return Control.onRMouseDown_( self, mods )

	def onViewItemRMouseUp_( self, pyViewItem, mods ) :
		"""
		当鼠标右键在可视选项上提起时被调用时
		"""
		if self.__selectable and self.__mouseUpSelect and \
			self.__rMouseSelect :							# 如果允许自动选中，并且是右键提起
				self.selIndex = pyViewItem.itemIndex		# 则选中鼠标击中的选项
		return Control.onRMouseUp_( self, mods )

	def onViewItemRClick_( self, pyViewItem, mods ) :
		"""
		当鼠标在可视选项中右击时被调用
		"""
		self.onItemRClick( pyViewItem.itemIndex )
		return Control.onRClick_( self, mods )

	def onViewItemLDBClick_( self, pyViewItem, mods ) :
		"""
		当鼠标在可视选项中双击时被调用
		"""
		self.onItemLDBClick( pyViewItem.itemIndex )
		return Control.onLDBClick_( self, mods )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def getViewItem_( self ) :
		"""
		获取一个 ViewItem
		可以通过重写该方法实现应用一个自定义的 ViewItem，但该自定义 ViewItem 必须继承于本模块的 ViewItem
		"""
		return ViewItem( self )

	# -------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		if self.tabStop :
			if key == KEY_UPARROW and mods == 0 :
				self.upSelect()
			elif key == KEY_DOWNARROW and mods == 0 :
				self.downSelect()
		return Control.onKeyDown_( self, key, mods )

	# ---------------------------------------
	def onLMouseDown_( self, mods ) :
		return False

	def onLMouseUp_( self, mods ) :
		return False

	def onRMouseDown_( self, mods ) :
		return False

	def onRMouseUp_( self, mods ) :
		return False

	# ---------------------------------------
	def onMouseScroll_( self, dz ) :
		"""
		当鼠标滚轮滚动时被调用
		"""
		if dz > 0 :
			self.pySBar.decScroll( self.__perScrollCount )
		else :
			self.pySBar.incScroll( self.__perScrollCount )
		return True

	# -------------------------------------------------
	def onScroll_( self, value ) :
		"""
		滚动条滚动时被触发
		"""
		hideHeight = self.__getHideHieight()						# 隐藏部分内容的总高度
		hideTop = hideHeight * value								# 按照滚动值，初步计算上半部分隐藏内容的高度
		firstViewIdx = int( round( hideTop / self.__itemHeight ) )	# 第一个可视选项在选项列表中的索引
		maxFirstViewCount = self.itemCount - self.viewCount
		firstViewIdx = min( firstViewIdx,  maxFirstViewCount )
		self.__redrawAllViewItems( firstViewIdx )					# 通知重画所有可视选项
		if hideHeight <= 0.0 :										# 版面可以显示完所有选项
			self.scroll = 0
		else :
			perScroll = 1.0 / hideHeight
			if value < perScroll / 2 :								# 已经滚动到了最前面
				self.scroll = 0
			elif value > 1 - perScroll / 2 :						# 已经滚动到了最后面
				self.scroll = self.maxScroll

	# -------------------------------------------------
	def onViewItemInitialized_( self, pyViewItem ) :
		"""
		当一个可视选项初始化时被调用
		"""
		if self.__ownerDraw :
			self.onViewItemInitialized( pyViewItem )
		else :
			pyViewItem.addDefaultText_()

	def onDrawItem_( self, pyViewItem  ) :
		"""
		可视选项需要重画时被调用
		"""
		if not self.__isRedraw : return								# 暂时不会重画
		if self.__ownerDraw : 										# 如果设置为自画
			if self.onViewItemInitialized.count() :					# 是否绑定了可视选项初始化事件（没绑定则不通知重画）
				self.onDrawItem( pyViewItem )						# 触发重画事件
			else :
				ERROR_MSG( "if 'ownerDraw' is True, 'onViewItemInitialized' must be bound!" )
		else :
			pyViewItem.updateDefaultText_()

	def onItemSelectChanged_( self, index ) :
		"""
		当前选中选项改变时被调用
		"""
		self.onItemSelectChanged( index )

	def onItemMouseEnter_( self, pyViewItem ) :
		"""
		当鼠标进入选项时被调用
		"""
		self.onItemMouseEnter( pyViewItem )

	def onItemMouseLeave_( self, pyViewItem ) :
		"""
		当鼠标离开选项时被调用
		"""
		self.onItemMouseLeave( pyViewItem )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEventBinded( self, eventName, event ) :
		"""
		有事件绑定时被触发
		"""
		if eventName == "onViewItemInitialized" :
			for pyViewItem in self.__pyViewItems :
				self.onViewItemInitialized_( pyViewItem )
		elif eventName == "onDrawItem" :
			for pyViewItem in self.__pyViewItems :
				self.onDrawItem_( pyViewItem )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def abandonRedraw( self ) :
		"""
		使选项暂时不会重画（必须与 insistRedraw 配套出现，只适合单线程）
		"""
		self.__isRedraw = False

	def insistRedraw( self ) :
		"""
		回复选项重画（必须与 abandonRedraw 配套出现，在 abandonRedraw 之后调用）
		"""
		self.__isRedraw = True

	# -------------------------------------------------
	def addItem( self, item ) :
		"""
		添加一个选项
		"""
		assert item is not None, "item must not be None type"
		index = self.itemCount
		self.__items.append( item )
		if self.__autoSelect and self.__selIndex < 0 :
			self.__selIndex = 0
		self.__addViewItem( index )
		self.__updateScrollBar()

	def removeItem( self, item ) :
		"""
		删除一个选项
		"""
		if item not in self.__items :
			raise ValueError( "item %s is not exist!" % str( item ) )
		index = self.__items.index( item )
		self.removeItemOfIndex( index )

	def removeItemOfIndex( self, index ) :
		"""
		删除指定索引选项
		"""
		itemCount = self.itemCount
		if index < 0 or index >= itemCount :
			raise IndexError( "index %i out of range!" % index )
		firstViewIdx = self.__pyViewItems[0].itemIndex
		lastViewIdx = self.__pyViewItems[-1].itemIndex
		viewCount = self.viewCount
		redrawStart = 0												# 可视选项中，需要重画的选项的起始索引
		dec = False													# 重画可视选项时，是否需要作“减一”操作（滚动条往上滚动一格）
		if itemCount <= viewCount :									# 版面可以放下所有可视选项
			pyViewItem = self.__getViewItem( index )				# 要删除选项的对应可视选项
			redrawStart = self.__pyViewItems.index( pyViewItem )
			pyViewItem = self.__pyViewItems.pop()					# 删除一个可视选项
			self.delPyChild( pyViewItem )
			viewCount -= 1
		elif index < firstViewIdx :									# 要删除的选项隐藏在版面的上面
			dec = True												# 则，所有可视选项往前挪
		elif lastViewIdx == itemCount - 1 :							# 如果滚动到最后一个选项处
			dec = True												# 则，所有可视选项往前挪
		elif index > lastViewIdx :									# 要删除的选项隐藏在版面下面
			redrawStart = lastViewIdx
		elif index >= firstViewIdx :								# 要删除的选项可见
			pyViewItem = self.__getViewItem( index )				# 要删除选项的对应可视选项
			redrawStart = self.__pyViewItems.index( pyViewItem )

		oldSelIndex = self.__selIndex
		self.__items.pop( index )									# 删除指定索引选项
		if index == self.__selIndex :								# 如果删除的选项为当前选中的选项
			self.__autoSelectItem()									# 自动选择一个选项
		elif index < self.__selIndex :								# 如果删除的选项在选中选项的前面
			self.__selIndex = max( -1, self.__selIndex - 1 )		# 则选中选项往回滚一项

		for idx in xrange( redrawStart, viewCount ) :
			pyViewItem = self.__pyViewItems[idx]
			if dec :
				newItemIndex = pyViewItem.itemIndex - 1
				pyViewItem.rebind_( newItemIndex )
			self.onDrawItem_( pyViewItem )
		self.__updateScrollBar()									# 更新滚动条

		if oldSelIndex == index :									# 如果删除的选项是当前选中的选项
			self.onItemSelectChanged_( self.__selIndex )			# 则，触发选项改变事件

	def addItems( self, items ) :
		"""
		添加一组选项
		"""
		if isDebuged :
			assert None not in items, "item must not be None type"
		if not len( items ) :
			return
		for item in items :
			index = self.itemCount
			self.__items.append( item )
			self.__addViewItem( index )
		if self.__autoSelect and self.__selIndex < 0 :
			self.__selIndex = 0
		self.__updateScrollBar()

	def clearItems( self ) :
		"""
		清除所有选项
		"""
		self.__pyViewItems = []
		self.__items = []
		self.__selIndex = -1
		self.__updateScrollBar()
		self.onItemSelectChanged_( -1 )

	def updateItem( self, index, item ) :
		"""
		更新指定选项
		"""
		itemCount = self.itemCount
		if index < 0 or index >= itemCount :
			raise IndexError( "index %i out of range!" % index )
		self.__items[index] = item
		if len( self.__pyViewItems ) :
			firstViewIdx = self.__pyViewItems[0].itemIndex
			lastViewIdx = self.__pyViewItems[-1].itemIndex
			if firstViewIdx <= index <= lastViewIdx :
				pyViewItem = self.__pyViewItems[index - firstViewIdx]
				self.onDrawItem_( pyViewItem )

	# ---------------------------------------
	def getItem( self, index ) :
		"""
		获得指定索引号的选项
		"""
		return  self.__items[index]

	# -------------------------------------------------
	def upSelect( self ) :
		"""
		选中当前选中选项的前一个选项
		"""
		itemCount = self.itemCount
		selIndex = self.selIndex
		self.selIndex = ( selIndex - 1 ) % itemCount

	def downSelect( self ) :
		"""
		选中当前选中选项的后一个选项
		"""
		itemCount = self.itemCount
		selIndex = self.selIndex
		self.selIndex = ( selIndex + 1 ) % itemCount

	# -------------------------------------------------
	def sort( self, cmp = None, key = None, reverse = False ) :
		"""
		排列所有选项( 排序后，原来选中选项将被取消选中状态 )
		"""
		selItem = self.selItem
		self.__items.sort( cmp, key, reverse )
		self.__redrawAllViewItems( 0 )
		if selItem is not None :						# 排序后，原来选中选项的索引将会改变
			selIndex = self.__items.index( selItem )	# 找出原来选中选项在新顺序中的索引
			self.__selectItem( selIndex )				# 重新选中该索引

	# -------------------------------------------------
	def resetState( self ) :
		"""
		恢复默认状态
		"""
		for pyViewItem in self.__pyViewItems :
			pyViewItem.resetState()


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getOwnerDraw( self ) :
		return self.__ownerDraw

	def _setOwnerDraw( self, ownerDraw ) :
		self.__ownerDraw = ownerDraw
		if ownerDraw :
			for pyViewItem in self.__pyViewItems :
				pyViewItem.clearDefaultText_()
				self.onViewItemInitialized_( pyViewItem )
				self.onDrawItem_( pyViewItem )
		else :
			for pyViewItem in self.__pyViewItems :
				pyViewItem.addDefaultText_()
				self.onDrawItem_( pyViewItem )

	def _getItemHeight( self ) :
		return self.__itemHeight

	def _setItemHeight( self, height ) :
		assert height > 0, "item height must more then 0!"
		self.__itemHeight = height
		if self.viewCount == 0 : return
		# 以下是通知所有可视选项重画
		firstViewIdx = self.__pyViewItems[0].itemIndex
		viewCount = int( math.ceil( self.height / self.__itemHeight ) )
		viewCount = min( self.itemCount, viewCount )
		self.__pyViewItems = []
		for idx in xrange( viewCount ) :
			self.__addViewItem( firstViewIdx )
			firstViewIdx += 1
		self.__updateScrollBar()									# 更新滚动条所能表达的内容

	# -------------------------------------------------
	def _getItems( self ) :
		return self.__items[:]

	# -------------------------------------------------
	def _getSelectable( self ) :
		return self.__selectable

	def _setSelectable( self, selectable ) :
		if self.__selectable == selectable :
			return
		self.__selectable = selectable
		selIndex = self.__selIndex
		self.__selIndex = -1
		pyViewItem = self.__getViewItem( selIndex )
		if pyViewItem :
			self.onDrawItem_( pyViewItem )
		if selectable and self.__autoSelect \
			and self.itemCount :									# 自动选择一个选项
				self.__selIndex = 0
				self.onItemSelectChanged_( 0 )

	# ---------------------------------------
	def _getAutoSelect( self ) :
		return self.__autoSelect

	def _setAutoSelect( self, autoSelect ) :
		self.__autoSelect = autoSelect
		if self.__selectable and autoSelect :						# 自动选择一个选项
			if self.__selIndex < 0 and self.itemCount :
				self.__selIndex = 0
				self.onItemSelectChanged_( 0 )

	# ---------------------------------------
	def _getMouseUpSelect( self ) :
		return self.__mouseUpSelect

	def _setMouseUpSelect( self, mouseUpSelect ) :
		self.__mouseUpSelect = mouseUpSelect

	# ---------------------------------------
	def _getRMouseSelect( self ) :
		return self.__rMouseSelect

	def _setRMouseSelect( self, rMouseSelect ) :
		self.__rMouseSelect = rMouseSelect

	# -------------------------------------------------
	def _getSelIndex( self ) :
		return self.__selIndex

	def _setSelIndex( self, index ) :
		if not self.__selectable : return
		if index > self.itemCount :
			raise IndexError( "index %i is out of range!" % index )
		if index == self.__selIndex : return
		self.__selectItem( index )
		self.onItemSelectChanged_( index )

	def _getSelItem( self ) :
		if self.__selIndex >= 0 :
			return self.__items[self.__selIndex]
		return  None

	def _setSelItem( self, item ) :
		if not self.__selectable : return
		self.selIndex = self.__items.index( item )

	# ---------------------------------------
	def _getItemCount( self ) :
		return len( self.__items )

	def _getViewCount( self ) :
		return len( self.__pyViewItems )

	# ---------------------------------------
	def _getPerScrollCount( self ) :
		return self.__perScrollCount

	def _setPerScrollCount( self, count ) :
		self.__perScrollCount = max( 1, count )

	# -------------------------------------------------
	def _getFont( self ) :
		return self.__font

	def _setFont( self, font ) :
		self.__font = font
		for pyViewItem in self.__pyViewItems :
			self.onDrawItem_( pyViewItem )

	# ---------------------------------------
	def _getItemCommonForeColor( self ) :
		return self.__itemForeColors[UIState.COMMON]

	def _setItemCommonForeColor( self, color ) :
		self.__itemForeColors[UIState.COMMON] = color
		for pyViewItem in self.__pyViewItems :
			self.onDrawItem_( pyViewItem )

	def _getItemCommonBackColor( self ) :
		return self.__itemBackColors[UIState.COMMON]

	def _setItemCommonBackColor( self, color ) :
		self.__itemBackColors[UIState.COMMON] = color
		for pyViewItem in self.__pyViewItems :
			self.onDrawItem_( pyViewItem )

	# ---------------------------------------
	def _getItemHighlightForeColor( self ) :
		return self.__itemForeColors[UIState.HIGHLIGHT]

	def _setItemHighlightForeColor( self, color ) :
		self.__itemForeColors[UIState.HIGHLIGHT] = color
		for pyViewItem in self.__pyViewItems :
			if not pyViewItem.height : continue
			self.onDrawItem_( pyViewItem )
			break

	def _getItemHighlightBackColor( self ) :
		return self.__itemBackColors[UIState.HIGHLIGHT]

	def _setItemHighlightBackColor( self, color ) :
		self.__itemBackColors[UIState.HIGHLIGHT] = color
		for pyViewItem in self.__pyViewItems :
			if not pyViewItem.height : continue
			self.onDrawItem_( pyViewItem )
			break

	# ---------------------------------------
	def _getItemSelectedForeColor( self ) :
		return self.__itemForeColors[UIState.SELECTED]

	def _setItemSelectedForeColor( self, color ) :
		self.__itemForeColors[UIState.SELECTED] = color
		for pyViewItem in self.__pyViewItems :
			if not pyViewItem.selected : continue
			self.onDrawItem_( pyViewItem )
			break

	def _getItemSelectedBackColor( self ) :
		return self.__itemBackColors[UIState.SELECTED]

	def _setItemSelectedBackColor( self, color ) :
		self.__itemBackColors[UIState.SELECTED] = color
		for pyViewItem in self.__pyViewItems :
			if not pyViewItem.selected : continue
			self.onDrawItem_( pyViewItem )
			break

	# ---------------------------------------
	def _getItemDisableForeColor( self ) :
		return self.__itemForeColors[UIState.DISABLE]

	def _setItemDisableForeColor( self, color ) :
		self.__itemForeColors[UIState.DISABLE] = color

	def _getItemDisableBackColor( self ) :
		return self.__itemBackColors[UIState.DISABLE]

	def _setItemDisableBackColor( self, color ) :
		self.__itemBackColors[UIState.DISABLE] = color

	# -------------------------------------------------
	def _setWidth( self, width ) :
		Control._setWidth( self, width )
		width = self.width
		for pyViewItem in self.__pyViewItems :
			pyViewItem.width = width
			self.onDrawItem_( pyViewItem )

	def _setHeight( self, height ) :
		Control._setHeight( self, height )
		itemCount = self.itemCount
		if itemCount == 0 : return
		firstViewIdx = self.__pyViewItems[0].itemIndex
		lastViewIdx = self.__pyViewItems[-1].itemIndex
		viewCount = int( math.ceil( self.height / self.__itemHeight ) )
		viewCount = min( itemCount, viewCount )
		currCount = self.viewCount
		if viewCount < currCount :											# 减少版面长度
			self.__pyViewItems = self.__pyViewItems[:viewCount]				# 去掉多余部分可见选项
			self.__updateScrollBar()
			hideCount = self.itemCount - self.viewCount
			if hideCount > 0 :
				self.pySBar.onScroll.unbind( self.onScroll_ )				# 取消滚动绑定，以免触发滚动回调，从而在回调中做不必要的重画
				firstViewIdx = self.__pyViewItems[0].itemIndex
				self.pySBar.value = float( firstViewIdx ) / hideCount		# 回复原来的滚动位置
				self.pySBar.onScroll.bind( self.onScroll_ )
		elif viewCount > currCount :										# 增加版面长度
			addCount = viewCount - currCount
			addedStart = lastViewIdx + 1									# 要增加的第一个可视选项对应的选项索引
			if lastViewIdx + addCount >= itemCount :						# 如果已经滚动到最后，则需要重画所有可视选项
				addedStart = itemCount - addCount
				firstViewIdx = addedStart - currCount		 				# 第一个可视选项的位置
				self.__redrawAllViewItems( firstViewIdx )					# 重画所有选项
			for idx in xrange( addCount ) :									# 增加可视选项
				self.__addViewItem( addedStart + idx )
			self.__updateScrollBar()
		else :
			self.__updateScrollBar()

	def _getSBarState( self ) :
		return self.__sbarState

	def _setSBarState( self, state ) :
		self.__sbarState = state
		if state == ScrollBarST.SHOW :
			self.pySBar.visible = True
		elif state == ScrollBarST.HIDE :
			self.pySBar.visible = False
		elif state == ScrollBarST.AUTO :
			self.pySBar.visible = False
		

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyViewItems = property( lambda self : self.__pyViewItems[:] )								# list of ViewItem : 获取所有可视选项
	ownerDraw = property( _getOwnerDraw, _setOwnerDraw )										# bool: 获取/设置是否自画
	itemHeight = property( _getItemHeight, _setItemHeight )										# float: 获取/设置选项高度
	items = property( _getItems )																# list: 获取所有选项
	selectable = property( _getSelectable, _setSelectable )										# bool: 获取/设置是否允许选中选项
	autoSelect = property( _getAutoSelect, _setAutoSelect )										# bool: 获取/设置是否自动选中一个选项
	mouseUpSelect = property ( _getMouseUpSelect, _setMouseUpSelect )							# bool: 获取/设置是否是鼠标提起时选中选项（selectable 为 True 时才有用）
	rMouseSelect = property( _getRMouseSelect, _setRMouseSelect )								# bool: 获取/设置鼠标右键点击选项时，是否选中选项
	selIndex = property( _getSelIndex, _setSelIndex )											# int: 获取/设置当前选中的选项索引
	selItem = property( _getSelItem, _setSelItem )												# 类型根据添加的选项而定，获取/设置选中选项
	itemCount = property( _getItemCount )														# int: 获取选项总数量
	viewCount = property( _getViewCount )														# int: 获取可视的选项数量
	perScrollCount = property( _getPerScrollCount, _setPerScrollCount )							# int: 获取/设置鼠标滚轮滑动一下滚动的选项数量

	font = property( _getFont, _setFont )														# str: 获取/设置选项字体
	itemCommonForeColor = property( _getItemCommonForeColor, _setItemCommonForeColor )			# tuple: 获取/设置普通状态下选项的前景色
	itemCommonBackColor = property( _getItemCommonBackColor, _getItemCommonBackColor )			# tuple: 获取/设置普通状态下选项的背景色
	itemHighlightForeColor = property( _getItemHighlightForeColor, _setItemHighlightForeColor )	# tuple: 获取/设置高亮状态下选项的前景色
	itemHighlightBackColor = property( _getItemHighlightBackColor, _setItemHighlightBackColor )	# tuple: 获取/设置高亮状态下选项的前景色
	itemSelectedForeColor = property( _getItemSelectedForeColor, _setItemSelectedForeColor )	# tuple: 获取/设置选中状态下选项的前景色
	itemSelectedBackColor = property( _getItemSelectedBackColor, _setItemSelectedBackColor )	# tuple: 获取/设置选中状态下选项的前景色
	itemDisableForeColor = property( _getItemDisableForeColor, _setItemDisableForeColor )		# tuple: 获取/设置无效状态下选项的前景色
	itemDisableBackColor = property( _getItemDisableBackColor, _setItemDisableBackColor )		# tuple: 获取/设置无效状态下选项的前景色

	width = property( Control._getWidth, _setWidth )											# float: 获取/设置板面宽度
	height = property( Control._getHeight, _setHeight )											# float: 获取/设置板面高度
	sbarState = property( _getSBarState, _setSBarState )					# defined: uidefine.ScrollBarST.SHOW, ScrollBarST.SHOW, ScrollBarST.HIDE


# --------------------------------------------------------------------
# implement inner item class
# --------------------------------------------------------------------
class ViewItem( Control ) :
	def __init__( self, pyPanel, item = None, pyBinder = None ) :
		if item is None :
			item = hfUILoader.load( "guis/controls/odlistpanel/viewitem.gui" )
		Control.__init__( self, item, pyBinder )
		self.__pyPanel = pyPanel
		self.focus = True
		self.crossFocus = True

		self.__itemIndex = 0
		self.__pyText = None
		self.__selected = False
		self.__highlight = False

	def __del__( self ) :
		if Debug.output_del_ODListPanel :
			INFO_MSG( self )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def rebind_( self, index ) :
		"""
		重新绑定一个列表选项
		"""
		self.__itemIndex = index
		if self.__pyText :
			listItem = self.listItem
			self.__pyText.text = listItem
			if FullText.pyBinder == self :
				FullText.show( self, self.__pyText, False )

	# -------------------------------------------------
	def addDefaultText_( self ) :
		"""
		创建一个默认的选项文本标签( 初始化 ViewItem 时被调用 )
		"""
		if self.__pyText : return
		self.clearChildren()
		staticText = hfUILoader.load( "guis/controls/odlistpanel/itemtext.gui" )
		self.__pyText = StaticText( staticText )
		self.__pyText.text = self.listItem
		self.addPyChild( self.__pyText )
		self.__pyText.r_left = uiFixer.toFixedX( self.__pyText.r_left )
		self.__pyText.middle = self.height / 2

	def updateDefaultText_( self ) :
		"""
		添加默认的选项文本（重画时被调用）
		"""
		if not self.__pyText : return
		listItem = self.listItem
		if not isinstance( listItem, basestring ) :						# 是否是合法的默认选项
			return
		pyPanel = self.pyPanel
		self.__pyText.font = pyPanel.font
		if self.selected :
			self.__pyText.color = pyPanel.itemSelectedForeColor			# 选中状态下的前景色
			self.color = pyPanel.itemSelectedBackColor					# 选中状态下的背景色
		elif self.highlight :
			self.__pyText.color = pyPanel.itemHighlightForeColor		# 高亮状态下的前景色
			self.color = pyPanel.itemHighlightBackColor				# 高亮状态下的背景色
		else :
			self.__pyText.color = pyPanel.itemCommonForeColor
			self.color = pyPanel.itemCommonBackColor

	def clearDefaultText_( self ) :
		"""
		清除默认信息
		"""
		if self.__pyText :
			self.delPyChild( self.__pyText )
			self.__pyText = None

	# -------------------------------------------------
	def onLMouseDown_( self, mods ) :
		return self.pyPanel.onViewItemLMouseDown_( self, mods )

	def onLMouseUp_( self, mods ) :
		return self.pyPanel.onViewItemLMouseUp_( self, mods )

	def onLClick_( self, mods ) :
		return self.pyPanel.onViewItemLClick_( self, mods )

	def onRMouseDown_( self, mods ) :
		return self.pyPanel.onViewItemRMouseDown_( self, mods )

	def onRMouseUp_( self, mods ) :
		return self.pyPanel.onViewItemRMouseUp_( self, mods )

	def onRClick_( self, mods ) :
		return self.pyPanel.onViewItemRClick_( self, mods )

	def onLDBClick_( self, mods ) :
		return self.pyPanel.onViewItemLDBClick_( self, mods )

	def onMouseEnter_( self ) :
		self.__highlight = True
		pyPanel = self.pyPanel
		pyPanel.onDrawItem_( self )
		pyPanel.onItemMouseEnter_( self )
		if self.__pyText and self.__pyText.width > self.width :
			FullText.show( self, self.__pyText )
		return True

	def onMouseLeave_( self ) :
		self.__highlight = False
		pyPanel = self.pyPanel
		pyPanel.onDrawItem_( self )
		pyPanel.onItemMouseLeave_( self )
		if self.__pyText :
			FullText.hide()
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def resetState( self ) :
		"""
		恢复默认状态
		"""
		if self.__highlight :
			self.__highlight = False
			self.pyPanel.onDrawItem_( self )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getItemIndex( self ) :
		return self.__itemIndex

	def _getListItem( self ) :
		return self.pyPanel.getItem( self.__itemIndex )

	def _getSelected( self ) :
		return self.__itemIndex == self.pyPanel.selIndex

	def _getHighlight( self ) :
		return self.__highlight
	
	def _getPyText( self ):
		return self.__pyText
	
	def _setPyText( self, pyText ):
		if not self.__pyText:
			self.__pyText = pyText

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyPanel = property( lambda self : self.__pyPanel ) 		# 获取所属的列表版面
	itemIndex = property( _getItemIndex )					# 获取对应选项在列表版面中的索引
	listItem = property( _getListItem )						# 获取对应的列表选项
	selected = property( _getSelected )						# 获取该选项是否是被选中选项
	highlight = property( _getHighlight )					# 获取改选项是否处于高亮状态
	pyText = property( _getPyText, _setPyText )			# 获取文本控件

