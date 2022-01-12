# -*- coding: gb18030 -*-
#
# $Id: ListPanel.py,v 1.36 2008-08-25 07:06:18 huangyongwei Exp $

"""
implement pages panel calss
2009/04/25 : writen by huangyongwei
"""

"""
composing :
	WindowsGUIComponent							# 选项版面
	control bar : GUI.Window					# 控制版面
		-- btnDec    : GUI.Window/GUI.Simple	# 往回翻页按钮
		-- btnInc    : GUI.Window/GUI.Simple	# 向前翻页按钮
		-- stPgIndex : GUI.Text					# 页码标签
"""

from guis import *
from Control import Control
from Button import Button
from StaticText import StaticText


class ODPagesPanel( Control ) :
	def __init__( self, panel, ctrlBar, pyBinder = None ) :
		Control.__init__( self, panel, pyBinder )
		self.__items = []										# 选项列表
		self.__pyViewItems = []									# 可视选项列表
		self.__viewRows = 1										# 可视选项行数
		self.__viewCols = 1										# 可视选项列数
		self.__pgIndex = 0										# 当前页码
		self.__isRedraw = True									# 需要重画时，是否马上重画

		self.__selectable = False								# 选项是否可以被选中
		self.__selIndex = -1									# 当前选中的选项索引
		self.__nOrder = False									# 是否采用“N”字顺序排列选项
		self.__rMouseSelect = False

		self.__initialize( panel, ctrlBar )

	def __del__( self ) :
		if Debug.output_del_ODPagesPanel :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		产生控件事件
		"""
		Control.generateEvents_( self )
		self.__onItemMouseEnter = self.createEvent_( "onItemMouseEnter" )				# 鼠标进入选项被触发
		self.__onItemMouseLeave = self.createEvent_( "onItemMouseLeave" )				# 鼠标离开选项被触发
		self.__onItemLMouseDown = self.createEvent_( "onItemLMouseDown" )				# 鼠标在选项上按下左键时被触发
		self.__onItemLMouseUp = self.createEvent_( "onItemLMouseUp" )					# 鼠标在选项上按下右键时被触发
		self.__onItemRMouseDown = self.createEvent_( "onItemRMouseDown" )				# 鼠标在选项上按下左键时被触发
		self.__onItemRMouseUp = self.createEvent_( "onItemRMouseUp" )					# 鼠标在选项上按下右键时被触发
		self.__onItemLClick = self.createEvent_( "onItemLClick" )						# 鼠标在选项上点击左键时被触发
		self.__onItemRClick = self.createEvent_( "onItemRClick" )						# 鼠标在选项上点击右键时被触发
		self.__onViewItemInitialized = self.createEvent_( "onViewItemInitialized" )		# 当初始化一个可视选项时被触发
		self.__onDrawItem = self.createEvent_( "onDrawItem" )							# 重画选项通知
		self.__onItemSelectChanged = self.createEvent_( "onItemSelectChanged" )			# 当选项被选中时触发
		self.__onItemLDBClick = self.createEvent_( "onItemLDBClick" )				# 当选项双击时触发
		

	@property
	def onItemMouseEnter( self ) :
		return self.__onItemMouseEnter

	@property
	def onItemMouseLeave( self ) :
		return self.__onItemMouseLeave

	@property
	def onItemLMouseDown( self ) :
		return self.__onItemLMouseDown

	@property
	def onItemLMouseUp( self ) :
		return self.__onItemLMouseUp

	@property
	def onItemRMouseDown( self ) :
		return self.__onItemRMouseDown

	@property
	def onItemRMouseUp( self ) :
		return self.__onItemRMouseUp

	@property
	def onItemLClick( self ) :
		return self.__onItemLClick

	@property
	def onItemRClick( self ) :
		return self.__onItemRClick

	@property
	def onViewItemInitialized( self ) :
		return self.__onViewItemInitialized

	@property
	def onDrawItem( self ) :
		return self.__onDrawItem

	@property
	def onItemSelectChanged( self ) :
		return self.__onItemSelectChanged
		
	@property
	def onItemLDBClick( self ):
		return self.__onItemLDBClick

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, panel, ctrlBar ) :
		self.pyBtnDec = Button( ctrlBar.btnDec )						# 往前翻页按钮
		self.pyBtnDec.setStatesMapping( UIState.MODE_R2C2 )
		self.pyBtnDec.onLClick.bind( self.onBtnDecClick_ )

		self.pyBtnInc = Button( ctrlBar.btnInc )						# 往后翻页按钮
		self.pyBtnInc.setStatesMapping( UIState.MODE_R2C2 )
		self.pyBtnInc.onLClick.bind( self.onBtnIncClick_ )

		self.pySTIndex_ = StaticText( ctrlBar.stPgIndex )				# 显示索引的标签

		self.viewSize = ( 1, 1 )										# 初始化为一行一列
		self.__resetPageIndex( 0 )

	# -------------------------------------------------
	def __resetPageIndex( self, index ) :
		"""
		设置页索引
		"""
		self.__pgIndex = index
		self.pySTIndex_.text = "%d/%d"%( index + 1, self.maxPageIndex + 1 )
		if index == 0 :
			self.pyBtnDec.enable = False
		else :
			self.pyBtnDec.enable = True
		if index == self.maxPageIndex :
			self.pyBtnInc.enable = False
		else :
			self.pyBtnInc.enable = True

	# ---------------------------------------
	def __redrawItems( self, first ) :
		"""
		重画从指定索引开始的选项，first 为要重画的第一个选项索引
		"""
		start = self.__pgIndex * self.viewCount							# 第一个可视选项对应的选项索引
		end = start + self.viewCount									# 最后一个可视选项对应的选项索引
		for idx in xrange( first, end ) :
			pyViewItem = self.__pyViewItems[idx - start]
			pyViewItem.rebind_( idx )
			self.onDrawItem_( pyViewItem )

	def __locateViewItem( self, pyViewItem, index ) :
		"""
		设置可视选项的位置
		"""
		viewRows, viewCols = self.__viewRows, self.__viewCols
		itemWidth, itemHeight = pyViewItem.size
		if self.__nOrder :
			left = itemWidth * ( index / viewRows )
			top = itemHeight * ( index % viewRows )
		else :
			left = itemWidth * ( index % viewCols )
			top = itemHeight * ( index / viewCols )
		pyViewItem.pos = left, top

	def __relocateAllViewItems( self ) :
		"""
		重新排列所有选项位置
		"""
		for idx, pyViewItem in enumerate( self.__pyViewItems ) :
			self.__locateViewItem( pyViewItem, idx )

	def __resizeAllViewItems( self ) :
		"""
		重画所有选项
		"""
		viewRows, viewCols = self.__viewRows, self.__viewCols
		itemWidth = self.width / viewCols								# 选项宽度
		itemHeight = self.height / viewRows								# 选项高度
		for idx, pyViewItem in enumerate( self.__pyViewItems ) :
			pyViewItem.size = itemWidth, itemHeight
			self.__locateViewItem( pyViewItem, idx )
			self.onDrawItem_( pyViewItem )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onBtnDecClick_( self ) :
		"""
		往前翻页按钮被点击时触发
		"""
		self.pageIndex -= 1

	def onBtnIncClick_( self ) :
		"""
		向后翻页按钮被点击时触发
		"""
		self.pageIndex += 1

	# -------------------------------------------------
	def onItemMouseEnter_( self, pyViewItem ) :
		"""
		当鼠标进入选项时被调用
		"""
		self.onDrawItem_( pyViewItem )
		self.onItemMouseEnter( pyViewItem )

	def onItemMouseLeave_( self, pyViewItem ) :
		"""
		当鼠标离开选项时被调用
		"""
		self.onDrawItem_( pyViewItem )
		self.onItemMouseLeave( pyViewItem )

	# ---------------------------------------
	def onItemLMouseDown_( self, pyViewItem, mods ) :
		"""
		当鼠标在选项上按下时被调用
		"""
		if self.__selectable :
			index = pyViewItem.itemIndex
			if index < self.itemCount :
				self.selIndex = index
		self.onItemLMouseDown( pyViewItem )

	def onItemLMouseUp_( self, pyViewItem, mods ) :
		"""
		当鼠标在选项上提起时被调用
		"""
		self.onItemLMouseUp( pyViewItem )

	def onItemRMouseDown_( self, pyViewItem, mods ) :
		"""
		当鼠标在选项上按下时被调用
		"""
		self.onItemRMouseDown( pyViewItem )

	def onItemRMouseUp_( self, pyViewItem, mods ) :
		"""
		当鼠标在选项上提起时被调用
		"""
		self.onItemRMouseUp( pyViewItem )

	# ---------------------------------------
	def onItemLClick_( self, pyViewItem, mods ) :
		"""
		当鼠标在选项上左键点击时被调用
		"""
		self.onItemLClick( pyViewItem )

	def onItemRClick_( self, pyViewItem, mods ) :
		"""
		当鼠标右键在选项上点击时被调用
		"""
		if self.__selectable and self.__rMouseSelect :		#右键点击时选中，和ODListPanel不同，这里不分按下提起
			self.selIndex = pyViewItem.itemIndex
		self.onItemRClick( pyViewItem )
	
	def onItemLDBClick_( self, pyViewItem, mods ):
		"""
		鼠标左键双击触发
		"""
		self.onItemLDBClick( pyViewItem )

	# ---------------------------------------
	def onViewItemInitialized_( self, pyViewItem ) :
		"""
		当一个可视选项初始化完毕时被调用
		"""
		self.onViewItemInitialized( pyViewItem )

	def onDrawItem_( self, pyViewItem ) :
		"""
		可视选项需要重画时被调用
		"""
		if not self.__isRedraw : return
		onDrawItem = self.onDrawItem
		if self.onViewItemInitialized.count() :
			self.onDrawItem( pyViewItem )

	def onItemSelectChanged_( self, index ) :
		"""
		某个选项被选中时调用
		"""
		start = self.__pgIndex * self.viewCount							# 第一个可视选项对应的选项索引
		end = start + self.viewCount									# 最后一个可视选项对应的选项索引
		if start <= index < end :
			self.onDrawItem( self.__pyViewItems[index - start] )
		self.onItemSelectChanged( index )


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
		assert item is not None, "item must not be None type!"
		index = self.itemCount											# 新添加选项的索引
		viewCount = self.viewCount										# 可视选项数量
		firstViewIndex = self.__pgIndex * viewCount						# 第一个可视选项对应的选项索引
		lastViewIndex = firstViewIndex + viewCount - 1					# 最后一个可视选项对应的选项索引
		self.__items.append( item )
		if firstViewIndex <= index <= lastViewIndex :					# 如果新添加的选项可视
			pyViewItem = self.__pyViewItems[index - firstViewIndex]		# 获取新添加选项对应的可视选项
			pyViewItem.rebind_( index )									# 设置该可视选项指向新添加的选项
			self.onDrawItem_( pyViewItem )								# 重画新添加选项
		self.__resetPageIndex( self.__pgIndex )
		
	# -------------------------------------------------
	def insterItem( self, index, item ) :
		"""
		添加一个选项至第一项
		"""
		assert item is not None, "item must not be None type!"
		viewCount = self.viewCount										# 可视选项数量
		firstViewIndex = self.__pgIndex * viewCount						# 第一个可视选项对应的选项索引
		lastViewIndex = firstViewIndex + viewCount - 1					# 最后一个可视选项对应的选项索引
		self.__items.insert( index, item )
		for i,v in enumerate( self.__pyViewItems ):
			v.rebind_( firstViewIndex + i )
			self.onDrawItem_( v ) 
		self.__resetPageIndex( self.__pgIndex )
#		self.__resizeAllViewItems()

	def removeItem( self, item ) :
		"""
		删除一个选项
		"""
		if item not in self.__items :
			raise ValueError( "item %s is not exist!" % str( item ) )
		self.removeItemOfIndex( self.__items.index( item ) )

	def removeItemOfIndex( self, index ) :
		"""
		删除指定索引选项
		"""
		if index < 0 or index >= self.itemCount :
			raise IndexError( "list index out of range!" )
		self.__items.pop( index )
		maxPgIndex = max( 0, ( self.itemCount - 1 ) / self.viewCount )	# 删除一个选项后最大的页索引

		oldSelIndex = self.__selIndex
		itemCount = self.itemCount										# 剩余选项总数
		if index < self.__selIndex :									# 如果删除的选项索引小于当前选中的选项索引
			self.__selIndex -= 1										# 则，选中索引减一( 即原来选中选项往前移了一个位置 )
		elif index == self.__selIndex :									# 如果删除的是当前选中选项
			if index == itemCount :										# 并且是最后一个选项
				self.__selIndex -= 1									# 则选中选项往前移动一个位置

		if self.__pgIndex > maxPgIndex :								# 如果删除一个选项后，翻页需要往回缩
			self.pageIndex = maxPgIndex 								# 则，将当前选中页置为最大页( 设置翻页时，全部可视选项已经得到重画 )
		else :
			self.__redrawItems( index )									# 重画在删除选项后面的所有选项

		if index == oldSelIndex :										# 如果删除的选项是当前选中选项
			self.onItemSelectChanged_( self.__selIndex )				# 则，触发选项改变事件
		self.__resetPageIndex( self.__pgIndex )

	def addItems( self, items ) :
		"""
		添加一组选项
		"""
		for item in items :
			self.addItem( item )

	def clearItems( self ) :
		"""
		清除所有选项
		"""
		self.__items = []
		for pyViewItem in self.__pyViewItems :
			pyViewItem.rebind_( -1 )
			self.onDrawItem_( pyViewItem )

		if self.__selIndex >= 0 :
			self.__selIndex = -1
			self.onItemSelectChanged_( -1 )
		self.__resetPageIndex( 0 )

	def updateItem( self, index, item ) :
		"""
		更新指定选项
		"""
		assert item is not None, "item must not be None type!"
		if index < 0 or index >= self.itemCount :
			raise IndexError( "list index out of range!" )
		self.__items[index] = item
		first, last = self.viewScope
		if first <= index <= last :
			pyViewItem = self.__pyViewItems[index - first]		# 要更新的选项所对应的可视选项
			self.onDrawItem_( pyViewItem )
			
	def queryItem( self, item ):
		"""
		查询选项属于第几页第几个 
		"""
		pageIndex = -1
		itemIndex = -1
		totalIndex = -1
		
		for index,xitem in enumerate( self.items ):
			if item == xitem:
				totalIndex  = index
		if totalIndex >= 0:
			pageIndex = totalIndex / len( self.pyViewItems )
			itemIndex = totalIndex % len( self.pyViewItems ) 
		return ( pageIndex, itemIndex )

	# -------------------------------------------------
	def pageUp( self, count = 1 ) :
		"""
		向前翻指定的页数
		"""
		self.pageIndex -= count

	def pageDown( self, count = 1 ) :
		"""
		向下翻指定的页数
		"""
		self.pageIndex += count

	# -------------------------------------------------
	def sort( self, cmp = None, key = None, reverse = False ) :
		"""
		排列所有选项( 排序后，原来选中选项将被取消选中状态 )
		"""
		self.__items.sort( cmp, key, reverse )
		self.__resetPageIndex( 0 )
		self.__redrawItems( 0 )

	def separateSort( self, cmp = None, key = None, reverse = False ) :
		"""
		分开每页各自按指定规则排序( 排序后，原来选中选项将被取消选中状态 )
		"""
		if not len( self.__items ) :
			return
		pgCount = self.maxPageIndex + 1
		viewCount = self.viewCount
		newItems = []
		for pgIdx in xrange( pgCount ) :
			start = pgIdx * viewCount
			end = start + viewCount
			items = self.__items[start:end]
			items.sort( cmp, key, reverse )
			newItems += items
		self.__items = newItems
		self.__selIndex = -1
		self.__redrawItems( self.viewScope[0] )

	# -------------------------------------------------
	def resetState( self ) :
		"""
		恢复默认状态( 当所属窗口关闭时，应该调用该方法 )
		"""
		for pyViewItem in self.__pyViewItems :
			pyViewItem.resetState()


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setNOrder( self, nOrder ) :
		if self.__nOrder == nOrder :
			return
		self.__nOrder = nOrder
		self.__relocateAllViewItems()

	# ---------------------------------------
	def _getViewSize( self ) :
		return self.__viewRows, self.__viewCols

	def _setViewSize( self, size ) :
		self.__viewRows = viewRows = max( 1, size[0] )					# 可视行数
		self.__viewCols = viewCols = max( 1, size[1] )					# 可视列数
		itemWidth = self.width / viewCols								# 选项宽度
		itemHeight = self.height / viewRows								# 选项高度

		oldCount = len( self.__pyViewItems )							# 原来的可视选项总数
		newCount = self.__viewRows * self.__viewCols					# 新的可视选项总数
		if oldCount > newCount :										# 可视可视选项数量减少了
			self.__pyViewItems = self.__pyViewItems[:newCount]			# 则，忽略多余的

		self.__resetPageIndex( 0 )										# 修改为显示第一页
		for idx in xrange( newCount ) :
			if idx < oldCount :
				pyViewItem = self.__pyViewItems[idx]
				pyViewItem.size = itemWidth, itemHeight
				self.__locateViewItem( pyViewItem, idx )
			else :														# 可视选项不存在
				pyViewItem = ViewItem( self )
				self.addPyChild( pyViewItem )
				self.__pyViewItems.append( pyViewItem )
				pyViewItem.size = itemWidth, itemHeight
				self.__locateViewItem( pyViewItem, idx )
				self.onViewItemInitialized_( pyViewItem )
			self.onDrawItem_( pyViewItem )

	# -------------------------------------------------
	def _getPageIndex( self ) :
		return self.__pgIndex

	def _setPageIndex( self, index ) :
		viewCount = self.viewCount
		maxIndex = ( self.itemCount - 1 ) / viewCount
		oldIndex = self.__pgIndex
		index = max( 0, min( index, maxIndex ) )
		self.__resetPageIndex( index )
		if oldIndex != index :
			self.__redrawItems( index * viewCount )

	def _getMaxPageIndex( self ) :
		return max( 0, self.itemCount - 1 ) / self.viewCount

	# -------------------------------------------------
	def _getViewScope( self ) :
		itemCount = self.itemCount
		if itemCount == 0 :
			return ( -1, -1 )
		viewCount = self.viewCount
		first = self.__pgIndex * viewCount					# 第一个可视选项的对应索引
		last = first + viewCount - 1						# 最后一个可视选项对应的索引
		last = min( last, self.itemCount - 1 )				# 最后一个有效可视选项对应的索引
		return first, last

	# -------------------------------------------------
	def _getSelectable( self ) :
		return self.__selectable

	def _setSelectable( self, selectable ) :
		if self.__selectable == selectable :
			return
		self.__selectable = selectable
		if selectable : return
		selIndex = self.__selIndex
		self.__selIndex = -1										# 设置为没选中选项
		first, last = self.viewScope								# 可视选项的索引范围
		if first <= selIndex <= last :								# 如果之前的选中选项为可视选项
			pyViewItem = self.__pyViewItems[selIndex - first]		# 找出该选项
			self.onDrawItem_( pyViewItem )							# 并重画
		if selIndex > 0 :											# 之前有选中选项
			self.onItemSelectChanged_( -1 )							# 触发选中选项改变事件

	def _getSelIndex( self ) :
		return self.__selIndex

	def _setSelIndex( self, index ) :
		if not self.__selectable : return							# 不可选中选项
		if index >= self.itemCount :
			raise IndexError( "error index!" )
		oldSelIndex = self.__selIndex								# 旧的选中选项
		if index == oldSelIndex : return							# 指定选项已经处于选中状态
		self.__selIndex = index
		first, last = self.viewScope								# 可视选项的索引范围
		if first <= oldSelIndex <= last :							# 旧的选中选项是否可视
			pyViewItem = self.__pyViewItems[oldSelIndex - first]	# 旧选中选项对应的可视选项
			self.onDrawItem_( pyViewItem )
		if first <= index <= last :									# 新的选中选项是否可视
			pyViewItem = self.__pyViewItems[index - first]			# 新选项对应的可视选项
			self.onDrawItem_( pyViewItem )
		self.onItemSelectChanged_( index )							# 触发选项选中事件

	def _getSelItem( self ) :
		if self.__selIndex >= 0 :
			return self.__items[self.__selIndex]
		return None

	def _setSelItem( self, item ) :
		if not self.__selectable : return
		self._setSelIndex( self.__items.index( item ) )

	# -------------------------------------------------
	def _setWidth( self, width ) :
		Control._setWidth( self, width )
		self.__resizeAllViewItems()

	def _setHeight( self, height ) :
		Controls._setHeight( self, height )
		self.__resizeAllViewItems()
		
	# ---------------------------------------
	def _getRMouseSelect( self ) :
		return self.__rMouseSelect

	def _setRMouseSelect( self, rMouseSelect ) :
		self.__rMouseSelect = rMouseSelect


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyViewItems = property( lambda self : self.__pyViewItems[:] )					# list of ViewItem : 获取所有可视选项
	nOrder = property( lambda self : self.__nOrder, _setNOrder )					# bool: 是否以“N”字顺序排列选项
	viewSize = property( _getViewSize, _setViewSize )								# tuple: 可视（行,列）数
	viewCount = property( lambda self : self.__viewRows * self.__viewCols )			# int: 可视选项数（== viewSize[0] * viewSize[1]）
	items = property( lambda self : self.__items[:] )								# list: 所有选项
	itemCount = property( lambda self : len( self.__items ) )						# int: 选项总数
	pageIndex = property( _getPageIndex, _setPageIndex )							# int: 获取/设置页索引
	maxPageIndex = property( _getMaxPageIndex )										# int: 获取最大页码
	viewScope = property( _getViewScope )											# tuple: 可视选项索引范围:( 第一个可视选项对应的索引，最后一个有效选项对应的选项索引)

	selectable = property( _getSelectable, _setSelectable )							# bool: 选项是否可被选中
	selIndex = property( _getSelIndex, _setSelIndex )								# int: 当前选中的选项索引
	selItem = property( _getSelItem, _setSelItem )									# all types: 当前选中的选项（注意：如果有多个相同选项，则选中的是顺序第一个）

	width = property( Control._getWidth, _setWidth )								# float: 获取/设置版面宽度
	height = property( Control._getHeight, _setHeight )								# float: 获取/设置版面高度
	rMouseSelect = property( _getRMouseSelect, _setRMouseSelect )					# bool: 获取/设置鼠标右键点击选项时，是否选中选项

# --------------------------------------------------------------------
# implement view item class for panel
# --------------------------------------------------------------------
class ViewItem( Control ) :
	def __init__( self, pyPanel ) :
		item = GUI.load( "guis/controls/odpagespanel/viewitem.gui" )				# 只有一个 UI，因此不需要 firstLoadFix
		Control.__init__( self, item, pyPanel )
		self.__itemIndex = -1
		self.__highlight = False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def rebind_( self, index ) :
		"""
		重新绑定一个列表选项
		"""
		self.__itemIndex = index

	# -------------------------------------------------
	def onMouseEnter_( self ) :
		self.__highlight = True
		self.pyBinder.onItemMouseEnter_( self )
		return True

	def onMouseLeave_( self ) :
		self.__highlight = False
		self.pyBinder.onItemMouseLeave_( self )
		return True

	# ---------------------------------------
	def onLMouseDown_( self, mods ) :
		self.pyBinder.onItemLMouseDown_( self, mods )
		return True

	def onLMouseUp_( self, mods ) :
		self.pyBinder.onItemLMouseUp_( self, mods )
		return True

	def onRMouseDown_( self, mods ) :
		self.pyBinder.onItemRMouseDown_( self, mods )
		return True

	def onRMouseUp_( self, mods ) :
		self.pyBinder.onItemRMouseUp_( self, mods )
		return True

	# ---------------------------------------
	def onLClick_( self, mods ) :
		self.pyBinder.onItemLClick_( self, mods )
		return True

	def onRClick_( self, mods ) :
		self.pyBinder.onItemRClick_( self, mods )
		return True
	
	def onLDBClick_( self, mods ):
		self.pyBinder.onItemLDBClick_( self, mods)
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
			self.pyBinder.onDrawItem_( self )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getPageItem( self ) :
		if self.__itemIndex < 0 : return None
		items = self.pyBinder.items
		if self.__itemIndex < len( items ) :
			return items[self.__itemIndex]
		return None

	# ---------------------------------------
	def _getSelected( self ) :
		return self.__itemIndex != -1 and \
		self.__itemIndex == self.pyBinder.selIndex


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	itemIndex = property( lambda self : self.__itemIndex )				# 对应的选项索引
	pageItem = property( _getPageItem )									# 对应的选项
	selected = property( _getSelected )									# 获取该选项是否是被选中选项
	highlight = property( lambda self : self.__highlight )				# 获取该选项是否处于高亮状态
