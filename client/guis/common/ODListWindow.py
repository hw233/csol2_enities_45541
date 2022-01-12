# -*- coding: gb18030 -*-
#
# $Id: ODListWindow.py,v 1.60 2008-09-04 01:00:31 huangyongwei Exp $

"""
imlement ownerdraw list window class

2009/03/17: writen by huangyongwei
"""

import weakref
from guis import *
from guis.util import copyGuiTree
from FlexExWindow import HVFlexExWindow
from PyGUI import PyGUI
from RootGUI import RootGUI
from guis.controls.ODListPanel import ODListPanel

"""
composing :
	sbBox( GUI.Window )				# 带滚动条
		-- l ( GUI.Simple )
		-- r ( GUI.Simple )
		-- t ( GUI.Simple )
		-- b ( GUI.Simple )
		-- lt ( GUI.Simple )
		-- rt ( GUI.Simple )
		-- lb ( GUI.Simple )
		-- rb ( GUI.Simple )
		-- splitter
		-- clipPanel ( GUI.Window )
		-- scrollBar ( GUI.Window )
			-- just likes HScrollBar
"""

class ODListWindow( HVFlexExWindow ) :
	__cg_wnd			= None
	__cc_view_count		= 6

	def __init__( self, wnd = None, pyBinder = None ) :
		if ODListWindow.__cg_wnd is None :
			ODListWindow.__cg_wnd = GUI.load( "guis_v2/common/odlistwindow/wnd.gui" )
		if wnd is None :
			wnd = copyGuiTree( ODListWindow.__cg_wnd )
			uiFixer.firstLoadFix( wnd )
		HVFlexExWindow.__init__( self, wnd )
		self.moveFocus = False													# 不可以用鼠标拖动
		self.posZSegment = ZSegs.L2												# 处于第二层 UI
		self.activable_ = False													# 不可以被激活
		self.escHide_ 		 = True												# 可以用 ESC 键隐藏
		self.addToMgr( "comboBoxListMenu" )

		self.__pyBinder = None
		if pyBinder : self.__pyBinder = weakref.ref( pyBinder )

		splitter = wnd.elements['splitter']
		self.__spRight = wnd.width - splitter.position.x						# 分割条左边到窗口右边的距离
		self.__spHightShort = wnd.height - splitter.size.y						# 分割条比窗口短多少
		self.__sbarRight = wnd.width - s_util.getGuiLeft( wnd.sbar )			# 滚动条左边到窗口右边的距离
		self.__sbarHeightShort = wnd.height - wnd.sbar.height					# 滚动条比窗口短多少
		self.__viewCount = 6													# 可视选项数量
		self.__initialize( wnd )

	def __initialize( self, wnd ) :
		self.pyListPanel_ = ODListPanel( wnd.clipPanel, wnd.sbar )				# 选项列表板面
		self.pyListPanel_.h_dockStyle = "HFILL"
		self.pyListPanel_.onViewItemInitialized.bind( self.onViewItemInitialized_ )
		self.pyListPanel_.onDrawItem.bind( self.onDrawItem_ )
		self.pyListPanel_.onItemSelectChanged.bind( self.onItemSelectChanged_ )
		self.pyListPanel_.onItemLClick.bind( self.onItemLClick_ )
		self.pyListPanel_.onItemRClick.bind( self.onItemRClick_ )
		self.pyListPanel_.onItemMouseEnter.bind( self.onItemMouseEnter_ )
		self.pyListPanel_.onItemMouseLeave.bind( self.onItemMouseLeave_ )
		self.pySBar_ = self.pyListPanel_.pySBar

		self.__hideScrollBar()
		self.viewCount = self.__cc_view_count									# 默认显示 6 个选项

	def __del__( self ) :
		HVFlexExWindow.__del__( self )
		if Debug.output_del_ComboBox :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		产生事件
		"""
		HVFlexExWindow.generateEvents_( self )
		self.__onViewItemInitialized = self.createEvent_( "onViewItemInitialized" )		# 初始化可视选项时被触发
		self.__onDrawItem = self.createEvent_( "onDrawItem" )							# 重画选项时被触发
		self.__onItemSelectChanged = self.createEvent_( "onItemSelectChanged" )			# 某个选项被选中时触发
		self.__onItemLClick = self.createEvent_( "onItemLClick" )						# 鼠标左键点击时被触发
		self.__onItemRClick = self.createEvent_( "onItemRClick" )						# 鼠标右键点击时被触发
		self.__onItemMouseEnter = self.createEvent_( "onItemMouseEnter" )				# 鼠标进入选项是被触发
		self.__onItemMouseLeave = self.createEvent_( "onItemMouseLeave" )				# 鼠离开选项是被触发

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
	def onItemLClick( self ) :									# 左键点击某选项时被触发
		return self.__onItemLClick

	@property
	def onItemRClick( self ) :									# 右键点击某选项时被触发
		return self.__onItemRClick

	@property
	def onItemMouseEnter( self ) :								# 鼠标进入选项时被
		return self.__onItemMouseEnter

	@property
	def onItemMouseLeave( self ) :								# 鼠标离开选项时被
		return self.__onItemMouseLeave


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __setPanelHeight( self, itemCount = None ) :
		"""
		设置板面高度（注意：有可能重画部分或全部选项）
		"""
		if itemCount is None :
			itemCount = self.itemCount
		count = min( itemCount, self.__viewCount )
		panelHeight = count * self.itemHeight
		height = panelHeight + 2 * self.pyListPanel_.top
		HVFlexExWindow._setHeight( self, height )
		self.pyListPanel_.height = panelHeight
		self.pySBar_.height = height - self.__sbarHeightShort
		self.txelems["splitter"].size.y = height - self.__spHightShort
		self.txelems["sbar_bg"].size.y = panelHeight

	def __showScrollBar( self ) :
		"""
		显示滚动条
		"""
		self.pySBar_.visible = True
		splitter = self.txelems['splitter']
		splitter.visible = True
		sbar_bg = self.txelems['sbar_bg']
		sbar_bg.visible = True
		self.pyListPanel_.width = splitter.position.x - self.pyListPanel_.left + 3

	def __hideScrollBar( self ) :
		"""
		隐藏滚动条
		"""
		self.pySBar_.visible = False
		self.txelems['splitter'].visible = False
		self.txelems['sbar_bg'].visible = False
		self.pyListPanel_.width = self.width - 2 * self.pyListPanel_.left + 3

	def __setScrollState( self ) :
		"""
		设置滚动条状态
		"""
		if self.isOverView() :
			self.__showScrollBar()
		else :
			self.__hideScrollBar()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onViewItemInitialized_( self, pyViewItem ) :
		"""
		当一个可视选项初始化完毕时被调用
		"""
		self.onViewItemInitialized( pyViewItem )

	def onDrawItem_( self, pyViewItem ) :
		"""
		当一个选项需要重画时被调用
		"""
		self.onDrawItem( pyViewItem )

	def onItemSelectChanged_( self, index ) :
		"""
		当一个选项被选中时调用
		"""
		self.onItemSelectChanged( index )

	def onItemLClick_( self, index ) :
		"""
		当一个选项被鼠左键标点击时调用
		"""
		self.onItemLClick( index )

	def onItemRClick_( self, index ) :
		"""
		当一个选项被鼠标右键点击时调用
		"""
		self.onItemRClick( index )

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
	def onActivated( self ) :
		"""
		当窗口激活时被调用
		"""
		RootGUI.onActivated( self )
		self.pyListPanel_.tabStop = True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isOverView( self ) :
		"""
		选项总数量是否超出可视选项数量
		"""
		return self.itemCount > self.viewCount

	# -------------------------------------------------
	def abandonRedraw( self ) :
		"""
		使选项暂时不会重画（必须与 insistRedraw 配套出现）
		"""
		self.pyListPanel_.abandonRedraw()

	def insistRedraw( self ) :
		"""
		恢复选项重画（必须与 abandonRedraw 配套出现，在 abandonRedraw 之后调用）
		"""
		self.pyListPanel_.insistRedraw()

	# -------------------------------------------------
	def addItem( self, item ) :
		"""
		添加一个选项
		"""
		itemCount = self.itemCount
		if itemCount == self.__viewCount :
			self.pyListPanel_.abandonRedraw()				# 添加选项时不要重画选项
			self.pyListPanel_.addItem( item )
			self.pyListPanel_.insistRedraw()				# 恢复重画选项
			self.__setScrollState()							# 这里会重画所有选项
		elif itemCount < self.__viewCount :					# 当选项总数量小于可视选项时
			self.pyListPanel_.abandonRedraw()				#使选项暂时不会重画
			self.__setPanelHeight( itemCount + 1 )			# 根据选项总数实时设置板面高度
			self.pyListPanel_.insistRedraw()				# 恢复重画选项
			self.pyListPanel_.addItem( item )
		else :												# 如果选项总数大于可视选项数
			self.pyListPanel_.addItem( item )
		self.pySBar_.value = 0

	def addItems( self, items ) :
		"""
		添加一组选项
		"""
		addCount = len( items )
		if not addCount : return
		itemCount = self.itemCount
		newCount = itemCount + addCount
		if newCount <= self.__viewCount :					# 总选项数小于可视选项数
			self.pyListPanel_.abandonRedraw()				# 删除选项时，不要重画选项
			self.__setPanelHeight( newCount )				# 根据选项总数实时设置板面高度
			self.pyListPanel_.insistRedraw()				# 恢复重画选项
			self.pyListPanel_.addItems( items )
		elif itemCount <= self.__viewCount :				# 总选项数大于可视选项数，但是添加之前的选项数小于可视选项数
			self.pyListPanel_.abandonRedraw()				# 删除选项时，不要重画选项
			if itemCount < self.__viewCount :
				self.__setPanelHeight( newCount )			# 根据选项总数实时设置板面高度
			self.pyListPanel_.addItems( items )
			self.pyListPanel_.insistRedraw()				# 恢复重画选项
			self.__setScrollState()							# 这里设置滚动条是否可见时，会重画所有选项
		else :												# 添加之前，选项数就大于可视选项数
			self.pyListPanel_.addItems( items )
		self.pySBar_.value = 0

	def removeItem( self, item ) :
		"""
		删除一个选项
		"""
		if item not in self.pyListPanel_.items :
			raise ValueError( "item %s is not exist!" % str( item ) )
		index = self.pyListPanel_.items.index( item )
		self.removeItemOfIndex( index )

	def removeItemOfIndex( self, index ) :
		"""
		删除指定索引处的选项
		"""
		itemCount = self.itemCount
		if index < 0 or index >= itemCount :
			raise IndexError( "index %i out of range!" % index )
		if itemCount <= 1 :
			self.hide()

		if itemCount == self.__viewCount + 1 :
			self.pyListPanel_.abandonRedraw()				# 不要重画选项
			self.pyListPanel_.removeItemOfIndex( index )
			self.pyListPanel_.insistRedraw()				# 恢复重画选项
			self.__setScrollState()
		elif itemCount <= self.__viewCount :
			self.pyListPanel_.abandonRedraw()				# 不要重画选项
			self.pyListPanel_.removeItemOfIndex( index )
			self.__setPanelHeight( itemCount - 1 )			# 根据选项总数实时设置板面高度
			self.pyListPanel_.insistRedraw()				# 恢复重画选项
		else :
			self.pyListPanel_.removeItemOfIndex( index )

	def clearItems( self ) :
		"""
		清除所有选项
		"""
		self.hide()
		self.pyListPanel_.clearItems()
		self.__setScrollState()

	def updateItem( self, index, item ) :
		"""
		更新指定选项
		"""
		self.pyListPanel_.updateItem( index, item )

	# ---------------------------------------
	def getItem( self, index ) :
		"""
		获取指定索引的选项
		"""
		return self.pyListPanel_.getItem( index )

	# -------------------------------------------------
	def upSelect( self ) :
		"""
		选中当前选中选项的前一个选项
		"""
		self.pyListPanel_.upSelect()

	def downSelect( self ) :
		"""
		选中当前选中选项的后一个选项
		"""
		self.pyListPanel_.downSelect()

	# -------------------------------------------------
	def sort( self, cmp = None, key = None, reverse = False ) :
		"""
		排列所有选项
		"""
		self.pyListPanel_.sort( cmp, key, reverse )

	# -------------------------------------------------
	def show( self ) :
		if self.itemCount == 0 :
			return False
		self.pyListPanel_.resetState()
		HVFlexExWindow.show( self )
		return True


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getBinder( self ) :
		if self.__pyBinder is None :
			return None
		return self.__pyBinder()

	def _getViewCount( self ) :
		return self.__viewCount

	def _setViewCount( self, count ) :
		self.__viewCount = max( 2, count )
		self.__setPanelHeight()

	def _setOwnerDraw( self, ownerdraw ) :
		self.pyListPanel_._setOwnerDraw( ownerdraw )

	# -------------------------------------------------
	def _setItemHeight( self, height ) :
		assert height > 0, "item height must more then 0!"
		self.pyListPanel_.abandonRedraw()
		self.__setPanelHeight()
		self.pyListPanel_.insistRedraw()
		self.pyListPanel_.itemHeight = height

	# ---------------------------------------
	def _setWidth( self, width ) :
		HVFlexExWindow._setWidth( self, width )
		splitter = self.txelems["splitter"]
		splitter.position.x = self.width - self.__spRight 
		sbar_bg = self.txelems["sbar_bg"]
		sbar_bg.position.x = self.width - self.__spRight 
		self.pySBar_.left = self.width - self.__sbarRight + 1


	# ----------------------------------------------------------------
	# proeprties
	# ----------------------------------------------------------------
	pyBinder = property( _getBinder )
	ownerDraw = property( lambda self : self.pyListPanel_.ownerDraw, _setOwnerDraw )			# bool: 是否开启自画选项功能
	items = property( lambda self : self.pyListPanel_.items )									# list: 获取所有选项
	itemCount = property( lambda self : self.pyListPanel_.itemCount )							# int: 获取选项数量
	viewCount = property( _getViewCount, _setViewCount )										# int: 获取可视选项数量( 必须大于或等于 2 )
	perScrollCount = property( lambda self : self.pyListPanel_.perScrollCount, \
		lambda self, v : self.pyListPanel_._setPerScrollCount( v ) )							# int: 获取/设置鼠标滚轮滑动一下滚动的选项数量
	autoSelect = property( lambda self : self.pyListPanel_.autoSelect, \
		lambda self, v : self.pyListPanel_._setAutoSelect( v ) )								# bool: 任何时候是否自动选择一项
	selItem = property( lambda self : self.pyListPanel_.selItem, \
		lambda self, v : self.pyListPanel_._setSelItem( v ) )									# 类型根据用户传入的选项而定: 获取/设置当前选中的选项
	selIndex = property( lambda self : self.pyListPanel_.selIndex, \
		lambda self, v : self.pyListPanel_._setSelIndex( v ) )									# int: 获取/设置当前选中的索引
	pyViewItems = property( lambda self : self.pyListPanel_.pyViewItems )						# list of ODListPanel.ViewItem: 获取所有可视选项

	font = property( lambda self : self.pyListPanel_.font, \
		lambda self, v : self.pyListPanel_._setFont( v ) )										# str: 获取/设置选项字体
	itemCommonForeColor = property( lambda self : self.pyListPanel_.itemCommonForeColor, \
		lambda self, v : self.pyListPanel_._setItemCommonForeColor( v ) )						# tuple: 获取/设置普通状态下选项的前景色
	itemCommonBackColor = property( lambda self : self.pyListPanel_.itemCommonBackColor, \
		lambda self, v : self.pyListPanel_._getItemCommonBackColor( v ) )						# tuple: 获取/设置普通状态下选项的背景色
	itemHighlightForeColor = property( lambda self : self.pyListPanel_.itemHighlightForeColor, \
		lambda self, v : self.pyListPanel_._setItemHighlightForeColor( v ) )					# tuple: 获取/设置高亮状态下选项的前景色
	itemHighlightBackColor = property( lambda self : self.pyListPanel_.itemHighlightBackColor,\
		lambda self, v : self.pyListPanel_._setItemHighlightBackColor( v ) )					# tuple: 获取/设置高亮状态下选项的前景色
	itemSelectedForeColor = property( lambda self : self.pyListPanel_.itemSelectedForeColor, \
		lambda self, v : self.pyListPanel_._setItemSelectForeColor( v ) )						# tuple: 获取/设置选中状态下选项的前景色
	itemSelectedBackColor = property( lambda self : self.pyListPanel_.itemSelectedBackColor, \
		lambda self, v : self.pyListPanel_._setItemSelectBackColor( v ) )						# tuple: 获取/设置选中状态下选项的前景色
	itemDisableForeColor = property( lambda self : self.pyListPanel_.itemDisableForeColor, \
		lambda self, v : self.pyListPanel_._setItemDisableForeColor( v ) )						# tuple: 获取/设置无效状态下选项的前景色
	itemDisableBackColor = property( lambda self : self.pyListPanel_.itemDisableBackColor, \
		lambda self, v : self.pyListPanel_._setItemDisableBackColor( v ) )						# tuple: 获取/设置无效状态下选项的前景色

	tabStop = property( lambda self : self.pyListPanel_.tabStop, \
		lambda self, v : self.pyListPanel_._setTabStop( v ) )									# bool: 获取/设置焦点

	itemHeight = property( lambda self : self.pyListPanel_.itemHeight, _setItemHeight )			# float: 获取/设置选项高度
	width = property( HVFlexExWindow._getWidth, _setWidth )										# float: 获取/设置宽度
	height = property( HVFlexExWindow._getHeight )												# float: 将高度设置为只读
