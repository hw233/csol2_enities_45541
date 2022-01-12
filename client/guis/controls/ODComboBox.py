# -*- coding: gb18030 -*-
#
# $Id: ComboBox.py,v 1.34 2008-08-26 02:12:45 huangyongwei Exp $

"""
implement ownerdraw combobox component
2009.02.07: modified by huangyongwei
"""

"""
composing :
	GUI.Window
		btnDown( GUI.Simple or GUI.Window )
		box( GUI.Window ) : 如果 box 作为 pyBox 传入，则这个可以没有
			-- lbView ( GUI.Text )
"""

import weakref
from AbstractTemplates import AbstractClass
from guis import *
from guis.common.ODListWindow import ODListWindow
from Control import Control
from BaseInput import BaseInput
from TextBox import TextBox
from StaticText import StaticText
from Button import Button


# --------------------------------------------------------------------
# implement combobox class
# --------------------------------------------------------------------
class ODComboBox( Control ) :
	def __init__( self, comboBox = None, clsBox = None, pyBinder = None ) :
		Control.__init__( self, comboBox, pyBinder )
		self.__initialize( comboBox, clsBox )
		self.__selIndex = -1

		self.readOnly = True

	def __initialize( self, comboBox, clsBox ) :
		if clsBox is None :
			self.pyBox_ = InputBox( comboBox.box, self )
		elif not issubclass( clsBox, IBox ) :
			raise TypeError( "box for combobox must implement IBox interface!" )
		elif not issubclass( clsBox, Control ) :
			raise TypeError( "box for combobox must inherit from Control!" )
		else :
			self.pyBox_ = clsBox( comboBox.box, self )
		self.pyBox_.h_dockStyle = "HFILL"
		self.pyBox_.onKeyDown.bind( self.onKeyDown_ )
		self.pyBox_.onLMouseDown.bind( self.onViewBoxLMouseDown_ )
		self.pyBox_.onTabIn.bind( self.onTabIn_ )
		self.pyBox_.onTabOut.bind( self.__onBoxTabOut )

		self.pyComboList_ = ComboList( self )
		self.pyComboList_.onViewItemInitialized.bind( self.onViewItemInitialized_ )
		self.pyComboList_.onDrawItem.bind( self.onDrawItem_ )
		self.pyComboList_.onItemSelectChanged.bind( self.pyBox_.onItemPreSelectChanged_ )
		self.pyComboList_.onItemLClick.bind( self.onItemLClick_ )
		self.pyComboList_.onItemRClick.bind( self.onItemRClick_ )
		self.pyComboList_.onItemMouseEnter.bind( self.onItemMouseEnter_ )
		self.pyComboList_.onItemMouseLeave.bind( self.onItemMouseLeave_ )
		self.pyComboList_.width = self.width

		self.pyBtnDown_ = Button( comboBox.btnDown )
		self.pyBtnDown_.setStatesMapping( UIState.MODE_R2C2 )
		self.pyBtnDown_.h_dockStyle = "RIGHT"
		self.pyBtnDown_.onLClick.bind( self.__onBtnDownClick )

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_ODComboBox :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		产生事件
		"""
		Control.generateEvents_( self )
		self.__onViewItemInitialized = self.createEvent_( "onViewItemInitialized" )		# 可视选项初始化时被触发
		self.__onDrawItem = self.createEvent_( "onDrawItem" )							# 选项重画时被触发
		self.__onItemSelectChanged = self.createEvent_( "onItemSelectChanged" )			# 选项选中时被触发
		self.__onItemLClick = self.createEvent_( "onItemLClick" )						# 鼠标左键点击选项时被触发
		self.__onItemRClick = self.createEvent_( "onItemRClick" )						# 鼠标右键点击选项时被触发
		self.__onItemMouseEnter = self.createEvent_( "onItemMouseEnter" )				# 鼠标进入选项是被触发
		self.__onItemMouseLeave = self.createEvent_( "onItemMouseLeave" )				# 鼠离开选项是被触发
		self.__onBeforeDropDown = self.createEvent_( "onBeforeDropDown" )				# 打开选项列表前被触发
		self.__onAfterDropDown = self.createEvent_( "onAfterDropDown" )					# 打开选项列表后被触发
		self.__onBeforeCollapsed = self.createEvent_( "onBeforeCollapsed" )				# 关闭选项列表前被触发
		self.__onAfterCollapsed = self.createEvent_( "onAfterCollapsed" )				# 关闭选项列表后被触发

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

	@property
	def onBeforeDropDown( self ) :								# 展开选项列表前被触发
		return self.__onBeforeDropDown

	@property
	def onAfterDropDown( self ) :								# 展开选项列表后被触发
		return self.__onAfterDropDown

	@property
	def onBeforeCollapsed( self ) :								# 合拢选项列表前被触发
		return self.__onBeforeCollapsed

	@property
	def onAfterCollapsed( self ) :								# 合拢选项列表后被触发
		return self.__onAfterCollapsed


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __locateComboList( self ) :
		"""
		设置列表位置
		"""
		if not self.visible : return
		self.pyComboList_.left = self.leftToScreen
		scHeight = BigWorld.screenHeight()
		height = self.pyComboList_.height
		bottom = self.bottomToScreen
		if bottom + height <= scHeight :
			self.pyComboList_.top = bottom
		else :
			self.pyComboList_.bottom = self.topToScreen

	# -------------------------------------------------
	def __selectItem( self, index, updateView ) :
		"""
		选中指定索引选项
		updateView 指示，如果 box 中的内容跟选中选项不一致的话，是否设置为一致
		"""
		if index != self.pyComboList_.selIndex :
			self.pyComboList_.selIndex = index
		if self.__selIndex != index :
			self.__selIndex = index
			if updateView and self.viewItem != self.selItem :		# 只有 readonly 为 False 时，才会造成这两个不一致
				self.pyBox_.onItemSelectChanged_( index )
			self.onItemSelectChanged_( index )
		elif updateView and self.viewItem != self.selItem :			# 只有 readonly 为 False 时，才会造成这两个不一致
			self.pyBox_.onItemSelectChanged_( index )

	# -------------------------------------------------
	def __onBtnDownClick( self ) :
		"""
		下拉按钮被点击时触发
		"""
		if self.isDropped :
			self.collapse( False, False )
		else :
			self.dropDown()

	# -------------------------------------------------
	def __onBoxTabOut( self ) :
		"""
		焦点撤离 Box 时被触发
		"""
		self.onTabOut_()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		"""
		按键按下时被调用（打开列表或焦点在 Box 上时被调用）
		"""
		if self.pyComboList_.onComboKeyDown_( key, mods ) :
			return True
		return self.onKeyDown( key, mods )

	def onViewBoxLMouseDown_( self ) :
		"""
		左键在 Box 上按下时被触发
		"""
		if self.readOnly :							# 如果只读
			self.__onBtnDownClick()					# 则，点击输入框时，显示选项列表

	def onTabOut_( self ) :
		"""
		失去焦点时被调用( 仅仅是 box 失去焦点也会被调用 )
		"""
		Control.onTabOut_( self )
		if self.isDropped :
			self.collapse( False, False )

	# -------------------------------------------------
	def onViewItemInitialized_( self, pyViewItem ) :
		"""
		当一个可视选项初始化完毕是被调用
		"""
		self.onViewItemInitialized( pyViewItem )

	def onDrawItem_( self, pyViewItem ) :
		"""
		某个选项重画时被触发
		"""
		self.onDrawItem( pyViewItem )

	def onItemSelectChanged_( self, index ) :
		"""
		选中选项时被调用
		"""
		self.onItemSelectChanged( index )

	def onItemLClick_( self, index ) :
		"""
		某个选项被鼠标左键点击时触发
		"""
		self.collapse( True, True )
		self.onItemLClick( index )

	def onItemRClick_( self, index ) :
		"""
		某个选项被鼠标右键点击时触发
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

	# ---------------------------------------
	def onBeforeDropDown_( self ) :
		"""
		显示选项列表前被调用
		"""
		self.pyBox_.onBeforeDropDown_()
		self.onBeforeDropDown()

	def onAfterDropDown_( self ) :
		"""
		显示选项列表后被调用
		"""
		self.pyBox_.onAfterDropDown_()
		self.onAfterDropDown()

	def onBeforeCollapsed_( self ) :
		"""
		关闭选项列表前被调用
		"""
		self.pyBox_.onBeforeCollapsed_()
		self.onBeforeCollapsed()

	def onAfterCollapsed_( self ) :
		"""
		关闭选项列表后被调用
		"""
		self.pyBox_.onAfterCollapsed_()
		self.onAfterCollapsed()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isMouseHit( self ) :
		"""
		指出鼠标是否落在控件身上
		"""
		if self.pyBox_.isMouseHit() :
			return True
		if self.pyBtnDown_.isMouseHit() :
			return True
		return False

	# -------------------------------------------------
	def addItem( self, item ) :
		"""
		添加一个选项
		"""
		self.pyComboList_.addItem( item )
		self.__locateComboList()
		self.__selectItem( self.pyComboList_.selIndex, False )

	def addItems( self, items ) :
		"""
		添加一组选项
		"""
		self.pyComboList_.addItems( items )
		self.__locateComboList()
		self.__selectItem( self.pyComboList_.selIndex, False )

	def removeItem( self, item ) :
		"""
		删除指定选项
		"""
		self.pyComboList_.removeItem( item )
		self.__locateComboList()
		self.__selectItem( self.pyComboList_.selIndex, False )

	def removeItemOfIndex( self, index ) :
		"""
		删除指定索引处选项
		"""
		self.pyComboList_.removeItemOfIndex( index )
		self.__locateComboList()
		self.__selectItem( self.pyComboList_.selIndex, False )

	def clearItems( self ) :
		"""
		清除所有选项
		"""
		self.pyComboList_.clearItems()
		self.__selectItem( self.pyComboList_.selIndex, False )

	def updateItem( self, index, item ) :
		"""
		更新指定选项
		"""
		updateView = self.viewItem == self.selItem
		self.pyComboList_.updateItem( index, item )
		if index == self.__selIndex and updateView :
			self.__selectItem( self.pyComboList_.selIndex, True )

	# ---------------------------------------
	def getItem( self, index ) :
		"""
		获取指定索引处的选项
		"""
		return self.pyComboList_.getItem( index )

	# -------------------------------------------------
	def sort( self, cmp = None, key = None, reverse = False ) :
		"""
		排序所有选项
		"""
		self.pyComboList_.sort( cmp, key, reverse )
		self.__selectItem( self.pyComboList_.selIndex, False )

	# -------------------------------------------------
	def isOverView( self ) :
		"""
		选项总数量是否超出可视选项数量
		"""
		return self.itemCount > self.viewCount

	# ---------------------------------------
	def abandonRedraw( self ) :
		"""
		使选项暂时不会重画（必须与 insistRedraw 配套出现）
		"""
		self.pyComboList_.abandonRedraw()

	def insistRedraw( self ) :
		"""
		恢复选项重画（必须与 abandonRedraw 配套出现，在 abandonRedraw 之后调用）
		"""
		self.pyComboList_.insistRedraw()

	# -------------------------------------------------
	def upSelect( self ) :
		"""
		选中当前选中选项的前一个选项
		"""
		if self.itemCount == 0 :
			return
		if self.__selIndex <= 0 :
			self.selIndex = self.itemCount - 1
		else :
			self.selIndex -= 1

	def downSelect( self ) :
		"""
		选中当前选中选项的后一个选项
		"""
		if self.itemCount == 0 :
			return
		if self.__selIndex >= self.itemCount :
			self.selIndex = 0
		else :
			self.selIndex += 1

	def selectItemViaKey( self, fnItemKey ) :
		"""
		选中以 key 返回的指定选项，如果选中成功则返回 True，否则返回 False
		@type				fnItemKey : callable object
		@param				fnItemKey : 选 key 回调，包含两个参数：index－－选项索引；item－－选项。
		"""
		if self.pyComboList_.selectItemViaKey( fnItemKey ) :
			self.__selectItem( self.pyComboList_.selIndex, True )

	# -------------------------------------------------
	def dropDown( self ) :
		"""
		下拉（显示）选项列表
		"""
		if self.isDropped : return
		self.onBeforeDropDown_()
		if self.itemCount == 0 : return
		self.__locateComboList()
		self.pyComboList_.show()
		if self.readOnly :
			self.tabStop = True
		self.onAfterDropDown_()

	def collapse( self, confirmSelect = False, updateView = False ) :
		"""
		折叠（隐藏）选项列表
		@type			confirmSelect : bool
		@param			confirmSelect : 是否确认选中列表中选中的选项
		@type			updateView	  : bool
		@param			updateView	  : 如果 box 中的内容跟选中项不同时，是否更新 box 中的内容（只有 readOnly == False 时才有用）
		"""
		if not self.isDropped : return
		index = self.__selIndex
		if confirmSelect :
			index = self.pyComboList_.selIndex
		self.__selectItem( index, updateView )			# 恢复为展开前的选中选项
		self.onBeforeCollapsed_()						# 触发合拢列表事件
		self.pyComboList_.hide()
		self.onAfterCollapsed_()
		if self.readOnly :								# 如果是只读
			self.tabStop = False						# 则，撤销焦点


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getSelIndex( self ) :
		return self.__selIndex

	def _setSelIndex( self, index ) :
		self.__selectItem( index, True )

	def _getSelItem( self ) :
		if self.__selIndex < 0 : return None
		return self.items[self.__selIndex]

	def _setSelItem( self, item ) :
		self.pyComboList_.selItem = item
		self.__selectItem( self.pyComboList_.selIndex, True )

	# ---------------------------------------
	def _getFont( self ) :
		return self.pyComboList_.font

	def _setFont( self, font ) :
		self.pyComboList_.font = font

	# ---------------------------------------
	def _getTabStop( self ) :
		if self.readOnly :
			if self.isDropped :
				return Control._getTabStop( self )
			return False
		return self.pyBox_.tabStop

	def _setTabStop( self, tabStop ) :
		if self.readOnly :
			Control._setTabStop( self, tabStop )
		else :
			self.pyBox_.tabStop = tabStop

	def _setReadOnly( self, readOnly ) :
		self.pyBox_.readOnly = readOnly
		if readOnly and self.isDropped :
			Control._setTabStop( self, True )
		if readOnly :
			if self.viewItem != self.selItem :						# 改为只读后，如果 box 中的文本跟选中文本不一致
				self.pyBox_.onItemSelectChanged_( self.selIndex )	# 则通知 box 更改文本

	def _setItemHeight( self, height ) :
		self.pyComboList_._setItemHeight( height )

	# -------------------------------------------------
	def _setAutoSelect( self, autoSelect ) :
		self.pyComboList_.autoSelect = autoSelect

	# -------------------------------------------------
	def _setWidth( self, width ) :
		Control._setWidth( self, width )
		self.pyComboList_.width = width


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyViewItems = property( lambda self : self.pyComboList_.pyViewItems )						# list of ODListPanel.ViewItem: 获取所有可视选项
	selIndex = property( _getSelIndex, _setSelIndex )											# int 当前选中的选项索引
	selItem = property( _getSelItem, _setSelItem )												# 类型为 addItem 时传入的选项类型，当前选中的选项
	font = property( _getFont, _setFont )														# str: 字体]
	width = property( Control._getWidth, _setWidth )											# float: 宽度
	tabStop = property( _getTabStop, _setTabStop )												# bool: 获取/设置输入焦点

	# 输入框属性
	pyBox = property( lambda self : self.pyBox_ )												# IBox: 获取 ComboBox 的 Box 部分，公开这部分实为非明智之举，但为了方便，暂时这样
	viewItem = property( lambda self : self.pyBox_.getViewItem_(), \
		lambda self, v : self.pyBox_.setViewItem_( v ) )										# 类型为 addItem 时传入的选项类型，获取/设置选中选项

	readOnly = property( lambda self : self.pyBox_.readOnly, _setReadOnly )						# bool: 是否是只读

	# 下拉列表属性
	ownerDraw = property( lambda self : self.pyComboList_.ownerDraw, \
		lambda self, v : self.pyComboList_._setOwnerDraw( v ) )									# bool: 是否开启自画选项功能
	isDropped = property( lambda self : self.pyComboList_.visible )								# bool: 是否处于下拉状态
	items = property( lambda self : self.pyComboList_.items )									# list: 获取所有选项
	itemHeight = property( lambda self : self.pyComboList_.itemHeight, _setItemHeight )			# float: 获取/设置选项高度
	itemCount = property( lambda self : self.pyComboList_.itemCount )							# int: 获取选项数量
	viewCount = property( lambda self : self.pyComboList_.viewCount, \
		lambda self, v : self.pyComboList_._setViewCount( v ) )									# int: 获取可视选项数量( 必须大于或等于 2 )
	perScrollCount = property( lambda self : self.pyComboList_.perScrollCount, \
		lambda self, v : self.pyComboList_._setPerScrollCount( v ) )							# int: 获取/设置鼠标滚轮滑动一下滚动的选项数量
	autoSelect = property( lambda self : self.pyComboList_.autoSelect, _setAutoSelect )			# bool: 任何时候是否自动选择一项
	itemCommonForeColor = property( lambda self : self.pyComboList_.itemCommonForeColor, \
		lambda self, v : self.pyComboList_._setItemCommonForeColor( v ) )						# tuple: 获取/设置普通状态下选项的前景色
	itemCommonBackColor = property( lambda self : self.pyComboList_.itemCommonBackColor, \
		lambda self, v : self.pyComboList_._getItemCommonBackColor( v ) )						# tuple: 获取/设置普通状态下选项的背景色
	itemHighlightForeColor = property( lambda self : self.pyComboList_.itemHighlightForeColor, \
		lambda self, v : self.pyComboList_._setItemHighlightForeColor( v ) )					# tuple: 获取/设置高亮状态下选项的前景色
	itemHighlightBackColor = property( lambda self : self.pyComboList_.itemHighlightBackColor,\
		lambda self, v : self.pyComboList_._setItemHighlightBackColor( v ) )					# tuple: 获取/设置高亮状态下选项的前景色
	itemSelectedForeColor = property( lambda self : self.pyComboList_.itemSelectedForeColor, \
		lambda self, v : self.pyComboList_._setItemSelectForeColor( v ) )						# tuple: 获取/设置选中状态下选项的前景色
	itemSelectedBackColor = property( lambda self : self.pyComboList_.itemSelectedBackColor, \
		lambda self, v : self.pyComboList_._setItemSelectBackColor( v ) )						# tuple: 获取/设置选中状态下选项的前景色
	itemDisableForeColor = property( lambda self : self.pyComboList_.itemDisableForeColor, \
		lambda self, v : self.pyComboList_._setItemDisableForeColor( v ) )						# tuple: 获取/设置无效状态下选项的前景色
	itemDisableBackColor = property( lambda self : self.pyComboList_.itemDisableBackColor, \
		lambda self, v : self.pyComboList_._setItemDisableBackColor( v ) )						# tuple: 获取/设置无效状态下选项的前景色


# --------------------------------------------------------------------
# implement combo viewer for comobox
# 注意：设 ComboBox 为 IBox 的友元类
# --------------------------------------------------------------------
class IBox( AbstractClass ) :
	__abstract_methods = set()

	def __init__( self, pyCombo ) :
		self.__pyCombo = weakref.ref( pyCombo )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onBeforeDropDown_( self ) :
		"""
		显示选项列表前被调用
		"""
		pass

	def onAfterDropDown_( self ) :
		"""
		显示选项列表后被调用
		"""
		pass

	def onBeforeCollapsed_( self ) :
		"""
		关闭选项列表前被调用
		"""
		pass

	def onAfterCollapsed_( self ) :
		"""
		关闭选项列表后被调用
		"""
		pass

	# -------------------------------------------------
	def getExposedAttr_( self, name ) :
		"""
		通过重写该方法可以把 Box 的属性转换为 ComboBox 的属性
		"""
		raise AttributeError( "ComboBox has no attribute '%s'." % name )

	def setExposedAttr_( self, name, value ) :
		"""
		通过重写该方法可以把 Box 的属性转换为 ComboBox 的属性
		"""
		raise AttributeError( "ComboBox has no attribute '%s'." % name )

	def getViewItem_ ( self ) :
		"""
		获取当前 Box 中的内容（如果 readOnly 为 True，则它等于 selItem ）
		"""
		pass

	def setViewItem_( self, viewItem ) :
		"""
		设置当前 Box 中的内容（如果 readOnly 为 True，则它应该引起一个
		"""
		raise AttributeError( "can't set attribute" )

	# -------------------------------------------------
	def onItemPreSelectChanged_( self, index ) :
		"""
		打开选项列表预选择时被调用
		"""
		pass

	def onItemSelectChanged_( self, index ) :
		"""
		某个选项确认被选中后调用
		"""
		pass


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getComboBox( self ) :
		return self.__pyCombo()

	def _getComboList( self ) :
		return self.__pyCombo().pyComboList_

	# -------------------------------------------------
	def _getReadOnly( self ) :
		return False

	def _setReadOnly( self, readOnly ) :
		pass


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyComboList_ = property( _getComboList )
	pyComboBox = property( _getComboBox )
	readOnly = property( _getReadOnly, _setReadOnly )					# 如果子类可输入，则必须重写该属性


	# ----------------------------------------------------------------
	# add as abstract method
	# ----------------------------------------------------------------
	__abstract_methods.add( getViewItem_ )
	__abstract_methods.add( setViewItem_ )
	__abstract_methods.add( onItemSelectChanged_ )


# --------------------------------------------------------------------
# implement text box in combox
# --------------------------------------------------------------------
class InputBox( IBox, TextBox ) :
	__cc_exposed_attrs = set( [
		"text",											# 当前文本
		"maxLength",									# 允许输入的最大字符数
		] )												# 需要公开作为 ComboBox 属性的属性

	def __init__( self, box, pyCombo ) :
		self.pyLBView_ = StaticText( box.lbView )						# 文本标签
		self.pyLBView_.h_dockStyle = self.pyLBView_.h_anchor			# 这里本来不能这么设置的，只是碰巧 h_dockStyle 与 h_anchor 的值
																		# 在靠左、居中、靠右上刚好都为："LEFT"、"CENTER"、"RIGHT"
		TextBox.__init__( self, box )
		IBox.__init__( self, pyCombo )
		self.pyLBView_.text = ""
		middle = self.pyLBView_.middle
		self.pyLText_.middle = middle
		self.pyRText_.middle = middle									# 设置 textbox 中的文本标签与 ComboBox 文本的高度一致
		self.foreColor = self.pyLBView_.color							# 设置 textbox 的前景色与 ComboBox 文本的颜色一致
		self.font = self.pyLBView_.font									# 设置 textbox 的字体与 ComboBox 文本的字体一致

		self.__followSelCBID = 0										# 输入文本时，跟随选中列表选项的 callback ID

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_ComboBox :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __selectStartswithInput( self ) :
		"""
		选中以 box 中输入的文本开头的选项
		"""
		if self.readOnly : return								# 只有在非只读时，才会存在文本框中的文本与选项文本不一致的问题
		if self.text == "" : return								# 空文本不计算
		pyComboList_ = self.pyComboList_
		text = self.text
		if text == "" :
			pyComboList_.selIndex = -1
			return
		items = []
		for index, item in enumerate( pyComboList_.items ) :	# 获取列表中所有以 Box 中文本开头的选项
			if item.startswith( text  ) :
				items.append( ( index, item ) )
		if len( items ) == 0 :									# 如果没有与 Box 中文本开头的选项
			pyComboList_.selIndex = -1							# 则预不选中任何选项
		else :													# 否则
			items.sort( key = lambda item : item[1] )			# 选中列表中第一个选项
			pyComboList_.selIndex = items[0][0]


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onBeforeDropDown_( self ) :
		"""
		显示选项列表前被调用
		"""
		self.__selectStartswithInput()

	# -------------------------------------------------
	def getExposedAttr_( self, name ) :
		"""
		通过重写该方法可以把 Box 的属性转换为 ComboBox 的属性
		"""
		if name in self.__cc_exposed_attrs :
			return getattr( self, name )
		return IBox.getExposedAttr_( self, name )

	def setExposedAttr_( self, name, value ) :
		"""
		通过重写该方法可以把 Box 的属性转换为 ComboBox 的属性
		"""
		if name in self.__cc_exposed_attrs :
			setattr( self, name, value )
		IBox.setExposedAttr_( self, name, value )

	def getViewItem_ ( self ) :
		"""
		获取当前 Box 中的内容（如果 readOnly 为 True，则它等于 selItem ）
		"""
		return self.text

	def setViewItem_( self, viewItem ) :
		"""
		设置当前 Box 中的内容（如果 readOnly 为 True，则它应该引起一个
		"""
		if not self.readOnly :
			self.text = viewItem
		else :
			IBox.setViewItem_( self, viewItem )

	# -------------------------------------------------
	def onTextChanged_( self ) :
		"""
		文本改变时被调用，设置 combobox 的文本与 textbox 的文本一致
		"""
		TextBox.onTextChanged_( self )
		self.pyLBView_.text = TextBox._getText( self )
		if not self.pyComboBox.isDropped : return
		BigWorld.cancelCallback( self.__followSelCBID )
		self.__followSelCBID = BigWorld.callback( 0.3, self.__selectStartswithInput )

	def onItemSelectChanged_( self, index ) :
		"""
		选项改变时被调用
		"""
		pyCombo = self.pyComboBox
		if not pyCombo.ownerDraw :
			self.text = "" if index < 0 else pyCombo.items[index]

	# -------------------------------------------------
	def onTabIn_( self ) :
		"""
		获得焦点时被调用
		"""
		TextBox.onTabIn_( self )
		self.pyLBView_.visible = False
		self.pyLText_.visible = True
		self.pyRText_.visible = True

	def onTabOut_( self ) :
		"""
		撤离焦点时被调用
		"""
		self.pyLBView_.visible = True
		self.pyLText_.visible = False
		self.pyRText_.visible = False
		TextBox.onTabOut_( self )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getText( self ) :
		return self.pyLBView_.text

	def _setText( self, text ) :
		self.pyLBView_.text = text
		TextBox._setText( self, text )

	# ---------------------------------------
	def _getFont( self ) :
		return self.pyLBView_.font

	def _setFont( self, font ) :
		self.pyLBView_.font = font
		TextBox._setFont( self, font )

	# ---------------------------------------
	def _setForeColor( self, color ) :
		self.pyLBView_.color = color
		TextBox._setForeColor( self, color )

	# ---------------------------------------
	def _setReadOnly( self, readOnly ) :
		TextBox._setReadOnly( self, readOnly )
		if readOnly :
			self.pyLText_.visible = False
			self.pyRText_.visible = False
			self.pyLBView_.visible = True

	# -------------------------------------------------
	def _setWidth( self, width ) :
		self.pyLBView_.text = self.pyLBView_.text
		if self.pyLBView_.h_anchor == "CENTER" :
			self.pyLBView_.left += ( width - self.width ) / 2
		elif self.pyLBView_.h_anchor == "RIGHT" :
			self.pyLBView_.left += width - self.width
		TextBox._setWidth( self, width )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )									# 获取/设置文本
	font = property( TextBox._getFont, _setFont )							# 获取/设置字体
	foreColor = property( TextBox._getForeColor, _setForeColor )			# 获取/设置前景色
	readOnly = property( TextBox._getReadOnly, _setReadOnly )				# 获取/设置是否只读
	width = property( TextBox._getWidth, _setWidth )						# 获取/设置宽度



# --------------------------------------------------------------------
# implement item list for combobox
# --------------------------------------------------------------------
class ComboList( ODListWindow ) :
	def __init__( self, pyCombo ) :
		ODListWindow.__init__( self, pyBinder = pyCombo )
		self.addToMgr( "comboList" )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __confirmSelect( self ) :
		"""
		确认让组合框选中当前列表中的选中选项
		"""
		self.pyBinder.collapse( True, True )

	def __cancelSelect( self ) :
		"""
		取消列表中当前选中的选项
		"""
		self.selIndex = self.pyBinder.selIndex
		self.pyBinder.collapse( False, False )

	# -------------------------------------------------
	def __onLastKeyDown( self, key, down ) :
		if ( key == KEY_LEFTMOUSE or key == KEY_RIGHTMOUSE ) and \
			not self.isMouseHit() and not self.pyBinder.isMouseHit() :
				self.pyBinder.collapse(  False, False )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onComboKeyDown_( self, key, mods ) :
		"""
		接收按键消息
		"""
		if self.visible :										# 可见状态下
			if mods != 0 : return False
			if key == KEY_UPARROW :								# 向上选择
				self.upSelect()
				return True
			elif key == KEY_DOWNARROW :							# 向下选择
				self.downSelect()
				return True
			elif key == KEY_RETURN or key == KEY_NUMPADENTER :	# 确认让组合框选中当前列表中的选中选项
				if self.selIndex < 0 :
					self.__cancelSelect()
				else :
					self.__confirmSelect()
				return True
			elif key == KEY_ESCAPE :							# 取消列表中当前选中的选项
				self.__cancelSelect()
				return True
		else :													# 不可见状态下
			if mods != 0 : return
			if key == KEY_UPARROW or key == KEY_DOWNARROW :
				self.pyBinder.dropDown()
				return True
		return False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def selectItemViaKey( self, fnItemKey ) :
		"""
		选中以 key 返回的指定选项，如果选中成功则返回 True，否则返回 False
		"""
		for index, item in enumerate( self.items ) :
			if fnItemKey( index, item ) :
				self.selIndex = index
				return True
		return False

	# -------------------------------------------------
	def show( self ) :
		self.__tmpSelIndex = self.selIndex
		ODListWindow.show( self )
		LastKeyDownEvent.attach( self.__onLastKeyDown )

	def hide( self ) :
		self.__tmpSelIndex = -1
		ODListWindow.hide( self )
		LastKeyDownEvent.detach( self.__onLastKeyDown )
