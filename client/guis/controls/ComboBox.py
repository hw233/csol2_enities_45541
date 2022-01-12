# -*- coding: gb18030 -*-
#
# $Id: ComboBox.py,v 1.34 2008-08-26 02:12:45 huangyongwei Exp $

"""
implement combobox component

2006.07.20: writen by huangyongwei
2008.04.17: modified by huangyongwei: 添加 ComboList
"""
"""
composing :
	GUI.Window
		downBtn( GUI.Simple or GUI.Window )
		textBox( GUI.Window )
			-- lbText ( GUI.Text )
"""

import weakref
from guis import *
from guis.UIFixer import hfUILoader
from guis.common.FlexWindow import HVFlexWindow as FlexWindow
from Control import Control
from TextBox import TextBox
from StaticText import StaticText
from Button import Button
from ListPanel import ListPanel
from ListItem import ListItem
from ListItem import SingleColListItem


# --------------------------------------------------------------------
# implement combobox class
# --------------------------------------------------------------------
class ComboBox( Control ) :
	def __init__( self, comboBox = None ) :
		Control.__init__( self, comboBox )
		self.__initialize( comboBox )

		self.__pySelItem = None												# 当前选中的选项实例

	def subclass( self, comboBox ) :
		Control.subclass( self, comboBox )
		self.__initialize( comboBox )

	def __del__( self ) :
		self.pyListPanel_.dispose()
		Control.__del__( self )
		if Debug.output_del_ComboBox :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, comboBox ) :
		if comboBox is None : return
		self.pyBox_ = Box( self, comboBox.textBox )							# 选中文本框
		self.pyBox_.h_dockStyle = "HFILL"

		self.pyDownBtn_ = Button( comboBox.downBtn )						# 下拉按钮
		self.pyDownBtn_.h_dockStyle = "RIGHT"
		self.pyDownBtn_.setStatesMapping( UIState.MODE_R2C2 )
		self.pyDownBtn_.onLMouseDown.bind( self.__toggleDropDown )

		self.pyListPanel_ = self.createListMenu_()							# 下拉列表
		self.pyListPanel_.setWidth__( self.width )
		self.pyListPanel_.visible = False

		self.canTabIn = True												# 是否可以获得焦点，获得焦点意味着允许输入
		self.readOnly = True												# 如果该属性为 True，则不可以输入
		self.autoSelect = True												# 当没有选中项时，是否自动选择一个靠近的选项


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		Control.generateEvents_( self )
		self.__onDropDown = self.createEvent_( "onDropDown" )					# 当显示下拉列表时被触发
		self.__onCollapsed = self.createEvent_( "onCollapsed" )					# 当收起下拉类别时被触发
		self.__onItemLClick = self.createEvent_( "onItemLClick" )				# 当某个选项被点击时被调用
		self.__onItemSelectChanged = self.createEvent_( "onItemSelectChanged" )	# 改变当前选项时被调用
		self.__onTextChanged = self.createEvent_( "onItemSelectChanged" )		# 文本改变时被调用

	@property
	def onDropDown( self ) :
		"""
		当显示下拉列表时被触发
		"""
		return self.__onDropDown

	@property
	def onCollapsed( self ) :
		"""
		当收起下拉类别时被触发
		"""
		return self.__onCollapsed

	# -------------------------------------------------
	@property
	def onItemLClick( self ) :
		"""
		当某个选项被点击时被调用
		"""
		return self.__onItemLClick

	@property
	def onItemSelectChanged( self ) :
		"""
		改变当前选项时被调用
		"""
		return self.__onItemSelectChanged

	@property
	def onTextChanged( self ) :
		"""
		输入框中的文本改变时被调用
		"""
		return self.__onTextChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __locateListMenu( self ) :
		"""
		设置下拉列表的位置
		"""
		self.pyListPanel_.left = self.leftToScreen
		self.pyListPanel_.top = self.bottomToScreen
		if self.pyListPanel_.r_bottomToScreen < -1 :
			self.pyListPanel_.bottom = self.topToScreen + 2			# 加 2 是因为贴图误差

	def __selectItem( self, pyItem ) :
		"""
		选中一个选项
		"""
		isSameItem = self.__pySelItem == pyItem
		self.__pySelItem = pyItem
		if not isSameItem :
			self.onItemSelectChanged( pyItem )
		text = getattr( pyItem, "text", None )
		if text is not None : self.pyBox_.text = text

	# -------------------------------------------------
	def __toggleDropDown( self ) :
		"""
		下拉/收起下拉列表
		"""
		if self.isDropDown :
			self.collapse()
		else :
			self.dropDown()


	# ----------------------------------------------------------------
	# friend methods
	# ----------------------------------------------------------------
	# -------------------------------------------------
	# friend of box
	# -------------------------------------------------
	def onBoxLMouseDown__( self ) :
		"""
		当鼠标点击 box 时被调用
		"""
		if self.pyBox_.readOnly :
			self.__toggleDropDown()
		else :
			self.pyListPanel_.hide()
			self.tabStop = True


	# -------------------------------------------------
	# frient of list menut
	# -------------------------------------------------
	def onItemLClick__( self, pyItem ) :
		"""
		当某个选项被点击时被调用
		"""
		self.collapse()
		if self.__pySelItem != pyItem :
			self.__selectItem( pyItem )
		self.onItemLClick( pyItem )

	def onItemSelectChanged__( self, pyItem ) :
		"""
		当某个选项被选中时，被调用
		"""
		if self.isDropDown :
			if not self.readOnly :
				self.tabStop = True
		else :
			self.__selectItem( pyItem )
		self.onItemSelectChanged_( pyItem )

	def onDropDown__( self ) :
		"""
		显示下拉列表时被调用
		"""
		rds.uiHandlerMgr.castUI( self )
		self.onDropDown()

	def onCollapsed__( self ) :
		"""
		隐藏下拉列表时被调用
		"""
		rds.uiHandlerMgr.uncastUI( self )
		self.onCollapsed()

	# -------------------------------------------------
	# frient of combo item
	# -------------------------------------------------
	def onItemTextChanged__( self, pyItem ) :
		"""
		某个子选项的文本改变时被调用
		"""
		if pyItem == self.pySelItem :
			self.pyBox_.text = pyItem.text


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def createListMenu_( self ) :
		"""
		创建下拉列表，可以通过重写该函数来设置下拉列表的外观
		"""
		return ComboList( self )

	def onItemSelectChanged_( self, pyItem ) :
		"""
		当一个选项被预选中时，该函数被调用，如果你的 Item 没有 text 属性，你可以重写该方法来设置预选中的内容
		"""
		if pyItem is None : return
		if hasattr( pyItem, "text" ) :
			self.pyBox_.text = pyItem.text
		else :
			WARNING_MSG( "the comboitem instance of %s is not contain 'text' property!" % pyItem.__class__ )

	# -------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		if self.isDropDown :											# 如果处于下拉状态
			if key == KEY_UPARROW :
				self.pyListPanel_.upSelect()
			elif key == KEY_DOWNARROW :
				self.pyListPanel_.downSelect()
			elif key == KEY_ESCAPE :
				self.cancelDrop()										# 隐藏下拉列表并取消选择
			elif key == KEY_RETURN or key == KEY_NUMPADENTER :
				self.collapse()											# 隐藏下拉列表接受选择
			return True
		if self.tabStop :												# 获得焦点并且没有处于下拉状态
			res = False
			if key == KEY_UPARROW or key == KEY_DOWNARROW :
				self.dropDown()
			else :
				res = self.pyBox_.onKeyDown__( key, mods )
			return Control.onKeyDown_( self, key, mods ) or res
		return Control.onKeyDown_( self, key, mods )

	def onKeyUp_( self, key, mods ) :
		if self.isDropDown : return False								# 处于下拉时取消消息的屏蔽，并且不发送事件
		return Control.onKeyUp_( self, key, mods )

	# -------------------------------------------------
	def onLMouseDown_( self, mods ) :
		if self.isDropDown :
			if not self.pyListPanel_.isMouseHit() and \
				not self.pyBox_.isMouseHit() and \
				not self.pyDownBtn_.isMouseHit() :
					self.collapse()
			return False												# 处于下拉时取消消息的屏蔽，并且不发送事件
		return Control.onLMouseDown_( self, mods )

	def onRMouseDown_( self, mods ) :
		if self.isDropDown :
			if not self.pyListPanel_.isMouseHit() and \
				not self.pyBox_.isMouseHit() and \
				not self.pyDownBtn_.isMouseHit() :
					self.collapse()
			return False												# 处于下拉时取消消息的屏蔽，并且不发送事件
		return Control.onRMouseDown_( self, mods )

	def onLMouseUp_( self, mods ) :
		if self.isDropDown : return False								# 处于下拉时取消消息的屏蔽，并且不发送事件
		return Control.onLMouseUp_( self, mods )

	def onRMouseUp_( self, mods ) :
		if self.isDropDown : return False								# 处于下拉时取消消息的屏蔽，并且不发送事件
		return Control.onRMouseUp_( self, mods )

	# -------------------------------------------------
	def onLClick_( self, mods ) :
		if self.isDropDown : return False								# 处于下拉时取消消息的屏蔽，并且不发送事件
		return Control.onLClick_( self, mods )

	# -------------------------------------------------
	def onTabIn_( self ) :
		Control.onTabIn_( self )
		if self.readOnly : return
		self.pyBox_.tabStop = True

	def onTabOut_( self ) :
		Control.onTabOut_( self )
		self.pyBox_.tabStop = False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addItem( self, pyItem ) :
		"""
		添加一个选项
		"""
		pySelItem = self.pyListPanel_.pySelItem
		self.pyListPanel_.addItem( pyItem )
		self.__locateListMenu()
		if pySelItem != self.pyListPanel_.pySelItem :			# 如果 autoSelect 为 True，在添加选项之前如果没有选中的选项
			self.__selectItem( self.pyListPanel_.pySelItem )	# 但添加选项后却自动选择了一个选项，则需要这样做（有点愚蠢，但有效）

	def addItems( self, pyItems ) :
		"""
		添加一组选项
		"""
		pySelItem = self.pyListPanel_.pySelItem
		self.pyListPanel_.addItems( pyItems )
		if pySelItem != self.pyListPanel_.pySelItem :
			self.__selectItem( self.pyListPanel_.pySelItem )

	def removeItem( self, pyItem ) :
		"""
		删除一个选项
		"""
		self.pyListPanel_.removeItem( pyItem )
		self.__locateListMenu()									# 如果下拉列表是往上伸展的，则需要重新设置它的位置
		if pyItem == self.__pySelItem :
			self.__selectItem( self.pyListPanel_.pySelItem )

	def clearItems( self ) :
		"""
		清除所有选项
		"""
		self.pyListPanel_.clearItems()
		self.__selectItem( None )
		self.pyBox_.text = ""

	# -------------------------------------------------
	def getSameTextItem( self, text ) :
		"""
		获取文本相同的第一个选项，没有找到则返回 None
		"""
		for pyItem in self.pyItems :
			if pyItem.text == text :
				return pyItem
		return None

	# -------------------------------------------------
	def upSelect( self ) :
		"""
		选择当前选项的上一个选项
		"""
		self.pyListPanel_.upSelect()

	def downSelect( self ) :
		"""
		选择当前选项的下一个选项
		"""
		self.pyListPanel_.downSelect()

	# -------------------------------------------------
	def notifyInput( self, text ) :
		"""
		给输入法调用，用以输入文本
		"""
		self.pyBox_.notifyInput( text )

	# -------------------------------------------------
	def dropDown( self ) :
		"""
		下拉（显示）选项列表
		"""
		if self.itemCount == 0 : return
		if self.isDropDown : return
		self.__locateListMenu()
		self.pyListPanel_.show()

	def collapse( self ) :
		"""
		折叠（隐藏）列表，并将当前列表中选中的选项作为 ComboBox 的选中选项
		"""
		if not self.isDropDown : return
		self.__selectItem( self.pyListPanel_.pySelItem )
		if not self.readOnly :
			self.pyBox_.selectAll()
		self.pyListPanel_.hide()

	def cancelDrop( self ) :
		"""
		折叠（隐藏）列表，但不将当前列表中选中的选项作为 ComboBox 的选中选项
		"""
		if not self.isDropDown : return
		self.pyListPanel_.pySelItem = self.__pySelItem
		self.pyListPanel_.hide()

	def moveCursorTo( self, idx ) :
		"""
		移动光标到指定地方
		"""
		self.pyBox_.moveCursorTo( idx )

	def select( self, start, end ) :
		"""
		选中指定文本
		"""
		self.pyBox_.select( start, end )

	# -------------------------------------------------
	def sort( self, cmp = None, key = None, reverse = False ) :
		"""
		排序所有选项
		"""
		self.pyListPanel_.sort( cmp, key, reverse )


	# ----------------------------------------------------------------
	# proeprty methods
	# ----------------------------------------------------------------
	def _getText( self ) :
		return self.pyBox_.text

	def _setText( self, text ) :
		if not self.readOnly :
			self.pyBox_.text = text

	# ---------------------------------------
	def _getFont( self ) :
		return self.pyBox_.font

	def _setFont( self, font ) :
		self.pyBox_.font = font

	def _getFontSize( self ) :
		return self.pyBox_.fontSize

	def _setFontSize( self, fontSize ) :
		self.pyBox_.fontSize = fontSize

	# ---------------------------------------
	def _getForeColor( self ) :
		return self.pyBox_.foreColor

	def _setForeColor( self, color ) :
		self.pyBox_.foreColor = color

	# ---------------------------------------
	def _getMaxLength( self ) :
		return self.pyBox_.maxLength

	def _setMaxLength( self, length ) :
		self.pyBox_.maxLength = length

	# -------------------------------------------------
	def _getItems( self ) :
		return self.pyListPanel_.pyItems

	def _getItemCount( self ) :
		return self.pyListPanel_.itemCount

	# -------------------------------------------------
	def _getSelItem( self ) :
		if self.__pySelItem in self.pyItems :
			return self.__pySelItem
		self.__pySelItem = None
		return None

	def _setSelItem( self, pyItem ) :
		if pyItem is None and self.__pySelItem :
			self.__pySelItem.selected = False
			self.__pySelItem = None
		else :
			pyItem.selected = True

	# ---------------------------------------
	def _getSelIndex( self ) :
		if self.__pySelItem in self.pyItems :
			return self.pyItems.index( self.__pySelItem )
		return -1

	def _setSelIndex( self, index ) :
		self.pyListPanel_.selIndex = index

	# -------------------------------------------------
	def _getViewCount( self ) :
		return self.pyListPanel_.viewCount

	def _setViewCount( self, count ) :
		self.pyListPanel_.viewCount = count

	# -------------------------------------------------
	def _getAutoSelect( self ) :
		return self.pyListPanel_.autoSelect

	def _setAutoSelect( self, auto ) :
		self.pyListPanel_.autoSelect = auto

	# -------------------------------------------------
	def _getReadOnly( self ) :
		return self.pyBox_.readOnly

	def _setReadOnly( self, readOnly ) :
		self.pyBox_.readOnly = readOnly
		if readOnly and self.tabStop :
			self.tabStop = False

	# -------------------------------------------------
	def _getIsDropDown( self ) :
		if self.pyListPanel_.itemCount == 0 :
			return False
		return self.pyListPanel_.rvisible

	# -------------------------------------------------
	def _setWidth( self, width ) :
		Control._setWidth( self, width )
		self.pyListPanel_.setWidth__( width )


	# ----------------------------------------------------------------
	# proeprties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )								# 获取/设置当前选择选项的文本
	font = property( _getFont, _setFont )								# 获取/设置字体
	fontSize = property( _getFontSize, _setFontSize )							# 获取/设置字体大小
	foreColor = property( _getForeColor, _setForeColor )				# 获取/设置前景色
	maxLength = property( _getMaxLength, _setMaxLength )				# 获取设置允许输入的最大文本

	pyItems = property( _getItems )										# 获取所有选项
	itemCount = property( _getItemCount )								# 获取选项的总数量
	pySelItem = property( _getSelItem, _setSelItem )					# 获取当前选中的选项实例
	selIndex = property( _getSelIndex, _setSelIndex )					# 获取/设置当前选中选项在列表中的索引
	viewCount = property( _getViewCount, _setViewCount )				# 获取/设置列中选项的可视数量
	autoSelect = property( _getAutoSelect, _setAutoSelect )				# 获取/设置是否在任何时候自动选择一个选项
	readOnly = property( _getReadOnly, _setReadOnly )					# 获取/设置是否只读（不允许手工输入，默认为 True）
	isDropDown = property( _getIsDropDown )								# 获取当前是否处于下拉状态

	width = property( Control._getWidth, _setWidth )					# 获取/设置宽度


# --------------------------------------------------------------------
# implement text box in combox
# --------------------------------------------------------------------
class Box( TextBox ) :
	def __init__( self, pyBinder, box ) :
		self.__pyText = StaticText( box.lbText )						# 文本标签
		self.__pyText.h_dockStyle = self.__pyText.h_anchor				# 这里本来不能这么设置的，只是碰巧 h_dockStyle 与 h_anchor 的值
																		# 在靠左、居中、靠右上刚好都为："LEFT"、"CENTER"、"RIGHT"
		TextBox.__init__( self, box, pyBinder )

		self.pyLText_.top = self.pyRText_.top = self.__pyText.top		# 设置 textbox 中的文本标签与 ComboBox 文本的高度一致
		self.foreColor = self.__pyText.color							# 设置 textbox 的前景色与 ComboBox 文本的颜色一致
		self.font = self.__pyText.font									# 设置 textbox 的字体与 ComboBox 文本的字体一致

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_ComboBox :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		"""
		鼠标点击时被调用
		"""
		self.pyBinder.onBoxLMouseDown__()
		if self.tabStop :
			TextBox.onLMouseDown_( self, mods )
		return True

	def onTextChanged_( self ) :
		"""
		文本改变时被调用，设置 combobox 的文本与 textbox 的文本一致
		"""
		TextBox.onTextChanged_( self )
		self.__pyText.text = TextBox._getText( self )
		pyBinder = self.pyBinder
		if pyBinder : pyBinder.onTextChanged()


	# ----------------------------------------------------------------
	# friend methods
	# ----------------------------------------------------------------
	def onKeyDown__( self, key, mods ) :
		return self.onKeyDown_( key, mods )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getText( self ) :
		return self.__pyText.text

	def _setText( self, text ) :
		self.__pyText.text = text
		if self.pyCursor_.capped( self ) :
			TextBox._setText( self, text )

	# ---------------------------------------
	def _getFont( self ) :
		return self.__pyText.font

	def _setFont( self, font ) :
		self.__pyText.font = font
		TextBox._setFont( self, font )

	def _getFontSize( self ) :
		return self.__pyText.fontSize

	def _setFontSize( self, fontSize ) :
		self.__pyText.fontSize = fontSize
		TextBox._setFontSize( self, fontSize )

	# ---------------------------------------
	def _setForeColor( self, color ) :
		self.__pyText.color = color
		TextBox._setForeColor( self, color )

	# ---------------------------------------
	def _setReadOnly( self, readOnly ) :
		TextBox._setReadOnly( self, readOnly )
		if readOnly :
			self.pyBinder.tabStop = False
			self.pyLText_.visible = False
			self.pyRText_.visible = False

	# -------------------------------------------------
	def _getTabStop( self ) :
		return self.pyBinder.tabStop

	def _setTabStop( self, tabStop ) :
		if tabStop :
			if self.readOnly : return
			self.pyLText_.visible = self.pyRText_.visible = True
			self.__pyText.visible = False
			self.showCursor_()
		else :
			TextBox.hideCursor_( self )
			self.pyLText_.visible = self.pyRText_.visible = False
			self.__pyText.visible = True

	# -------------------------------------------------
	def _setWidth( self, width ) :
		self.__pyText.text = self.__pyText.text
		if self.__pyText.h_anchor == "CENTER" :
			self.__pyText.left += ( width - self.width ) / 2
		elif self.__pyText.h_anchor == "RIGHT" :
			self.__pyText.left += width - self.width
		TextBox._setWidth( self, width )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )								# 获取/设置文本
	font = property( TextBox._getFont, _setFont )						# 获取/设置字体
	fontSize = property( _getFontSize, _setFontSize )								# 获取/设置字体大小
	foreColor = property( TextBox._getForeColor, _setForeColor )		# 获取/设置前景色
	readOnly = property( TextBox._getReadOnly, _setReadOnly )			# 获取/设置是否只读

	tabStop = property( _getTabStop, _setTabStop )						# 获取/设置输入焦点

	width = property( TextBox._getWidth, _setWidth )					# 获取/设置宽度



# --------------------------------------------------------------------
# implement listment class in combobox
# --------------------------------------------------------------------
class ComboList( FlexWindow, Control ) :
	__cc_sbar_panel  = "guis/controls/combobox/panel/spanel.gui"		# 带滚动条的板面
	__cc_nobar_panel = "guis/controls/combobox/panel/npanel.gui"		# 不带滚动条的板面

	def __init__( self, pyBinder, spanel = None, npanel = None ) :
		panel = hfUILoader.load( self.__cc_sbar_panel )
		FlexWindow.__init__( self, panel )
		Control.__init__( self, panel, pyBinder )
		self.moveFocus = False															# 不可以用鼠标拖动
		self.posZSegment = ZSegs.L2														# 处于第二层 UI
		self.activable_ = False															# 不可以被激活
		self.escHide_ = True															# 可以用 ESC 键隐藏

		self.__pyListPanel = ListPanel( panel.clipPanel, panel.scrollBar )				# item 版面
		self.__pyListPanel.selectable = True											# 可以选中某项
		self.__pyListPanel.mouseUpSelect = True
		self.__pyListPanel.onItemLClick.bind( self.__onItemLClick )
		self.__pyListPanel.onItemSelectChanged.bind( self.__onItemSelectChanged )
		self.__pyScrollBar = self.__pyListPanel.pySBar									# 滚动条
		self.__pyScrollBar.h_dockStyle = "RIGHT"
		self.__pyScrollBar.v_dockStyle = "VFILL"

		self.__viewCount = 6															# 可视选项数量
		self.__hideScroll()																# 默认隐藏滚动条

		self.addToMgr( "comboBoxListMenu" )


	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_ComboBox :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __rewidthItem( self, pyItem ) :
		"""
		根据列表的宽度设置某个选项的宽度
		"""
		pyItem.width = self.__pyListPanel.width

	def __rewidthItems( self ) :
		"""
		根据列表的宽度设置所有选项的宽度
		"""
		for pyItem in self.pyItems :
			self.__rewidthItem( pyItem )

	def __reheight( self ) :
		"""
		设置列表版面的高度
		"""
		itemCount = self.itemCount
		viewCount = self.viewCount
		if itemCount == 0 : return									# 没有选项
		if self.isOverView() :										# 选项数量超出可视选项数量
			itemsHeight = self.pyItems[viewCount - 1].bottom		# 则高度计算到可视选项数量为止
			bg = hfUILoader.load( self.__cc_sbar_panel )			# 带滚动条背景
		else :														# 否则
			itemsHeight = self.getItem( -1 ).bottom					# 按选项数量实际高度设置列表高度
			bg = hfUILoader.load( self.__cc_nobar_panel )			# 不带滚动条背景
		self.__pyListPanel.pos = s_util.getGuiPos( bg.clipPanel )
		self.__pyListPanel.height = itemsHeight
		space = bg.height - bg.clipPanel.height
		height = itemsHeight + space
		FlexWindow._setHeight( self, height )						# 重新设置版面的高度
		sbSpace = bg.height - bg.scrollBar.height
		self.__pyScrollBar.height = height - sbSpace				# 重新设置滚动条的高度

	# ---------------------------------------
	def __copyFrame( self, srcPanel ) :
		"""
		复制版面贴图
		"""
		self.pyRT_.texture = srcPanel.rt.textureName
		self.pyR_.texture = srcPanel.r.textureName
		self.pyRB_.texture = srcPanel.rb.textureName
		cpRight = s_util.getGuiRight( srcPanel.clipPanel )
		space = srcPanel.width - cpRight
		self.__pyListPanel.width = self.width - self.__pyListPanel.left - space

	def __showScroll( self ) :
		"""
		显示滚动条
		"""
		self.__pyScrollBar.visible = True
		sbarPanel = hfUILoader.load( self.__cc_sbar_panel )
		self.__copyFrame( sbarPanel )
		self.__rewidthItems()

	def __hideScroll( self ) :
		"""
		隐藏滚动条
		"""
		self.__pyScrollBar.visible = False
		nobarPanel = hfUILoader.load( self.__cc_nobar_panel )
		self.__copyFrame( nobarPanel )
		self.__rewidthItems()

	# -------------------------------------------------
	def __onItemLClick( self, pyItem ) :
		"""
		当一个选项被点击时被调用
		"""
		self.pyBinder.onItemLClick__( pyItem )

	def __onItemSelectChanged( self, pyItem ) :
		"""
		当一个选项被选中时被调用
		"""
		self.pyBinder.onItemSelectChanged__( pyItem )


	# ----------------------------------------------------------------
	# friend methods
	# ----------------------------------------------------------------
	def setWidth__( self, width ) :
		"""
		根据 comboBox  设置宽度
		"""
		self.__pyListPanel.width += width - self.width
		FlexWindow._setWidth( self, width )
		self.__rewidthItems()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self ) :
		if self.itemCount == 0 : return
		FlexWindow.show( self )
		self.pyBinder.onDropDown__()

	def hide( self ) :
		FlexWindow.hide( self )
		self.pyBinder.onCollapsed__()

	# -------------------------------------------------
	def addItem( self, pyItem ) :
		"""
		添加一个选项
		"""
		assert isinstance( pyItem, ComboItem ), "item '%s' added to ComboBox must inherit from ComboItem!" % str( pyItem )
		pre = pyItem not in self.pyItems				# 判断选项是否已经在列表中
		pyItem.setComboBox__( self.pyBinder )			# 设置所属 ComboBox
		self.__pyListPanel.addItem( pyItem )			# 添加到列表
		lat = pyItem in self.pyItems					# 再次判断选项是否在列表中（因为有可能添加失败）
		if not ( pre and lat ) : return					# 如果添加失败，则返回

		itemCount = self.itemCount
		viewCount = self.viewCount
		if itemCount <= viewCount :						# 如果选项总数量小于可视选项数量
			self.__reheight()							# 实时设置版面高度
			self.__rewidthItem( pyItem )				# 设置新添加选项的高度
		elif itemCount == viewCount + 1 :				# 选项总数刚好超过可视选项数量
			self.__showScroll()							# 则显示滚动条（注：这里也要设置新添加选项的宽度，只是这一步已经在 showScroll 中做了）
		else :											# 选项总数量本来就超过可视选项的数量
			self.__rewidthItem( pyItem )				# 所以只需要设置新选项的高度

	def addItems( self, pyItems ) :
		"""
		添加一组选项
		"""
		for pyItem in pyItems :
			self.addItem( pyItem )

	def removeItem( self, pyItem ) :
		"""
		删除一个选项
		"""
		if pyItem not in self.pyItems : return
		self.__pyListPanel.removeItem( pyItem )
		pyItem.setComboBox__( None )

		itemCount = self.itemCount
		viewCount = self.viewCount
		if itemCount < viewCount :						# 如果选项总数小于可视选项数量
			self.__reheight()							# 重新设置版面高度
		elif itemCount == viewCount :					# 如果选项总数刚好等于可视数量
			self.__hideScroll()							# 则隐藏滚动条

	def clearItems( self ) :
		"""
		删除所有选项
		"""
		for pyItem in self.pyItems :
			pyItem.setComboBox__( None )
		self.__pyListPanel.clearItems()
		self.__hideScroll()
		self.hide()

	# ---------------------------------------
	def getItem( self, index ) :
		"""
		获取指定索引处的选项
		"""
		return self.__pyListPanel.getItem( index )

	# -------------------------------------------------
	def upSelect( self ) :
		"""
		向上选择一项
		"""
		self.__pyListPanel.upSelect()

	def downSelect( self ) :
		"""
		向下选择一项
		"""
		self.__pyListPanel.downSelect()

	# -------------------------------------------------
	def sort( self, cmp = None, key = None, reverse = False ) :
		"""
		排序所有选项
		"""
		if cmp is None and key is None :
			self.__pyListPanel.sort( key = lambda pyItem : pyItem.text )
		else :
			self.__pyListPanel.sort( cmp, key, reverse )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getItems( self ) :
		return self.__pyListPanel.pyItems

	# ---------------------------------------
	def _getItemCount( self ) :
		return self.__pyListPanel.itemCount

	# ---------------------------------------
	def _getViewCount( self ) :
		return self.__viewCount

	def _setViewCount( self, count ) :
		count = max( count, 1 )
		self.__viewCount = count

	# ---------------------------------------
	def isOverView( self ) :
		return self.itemCount > self.viewCount

	# -------------------------------------------------
	def _getSelItem( self ) :
		return self.__pyListPanel.pySelItem

	def _setSelItem( self, pyItem ) :
		self.__pyListPanel.pySelItem = pyItem

	# ---------------------------------------
	def _getSelIndex( self ) :
		return self.__pyListPanel.selIndex

	def _setSelIndex( self, index ) :
		self.__pyListPanel.selIndex = index

	# ---------------------------------------
	def _getAutoSelect( self ) :
		return self.__pyListPanel.autoSelect

	def _setAutoSelect( self, auto ) :
		self.__pyListPanel.autoSelect = auto



	# ----------------------------------------------------------------
	# proeprties
	# ----------------------------------------------------------------
	pyItems = property( _getItems )										# 获取所有选项
	itemCount = property( _getItemCount )								# 获取选项数量
	viewCount = property( _getViewCount, _setViewCount )				# 获取可视选项数量
	autoSelect = property( _getAutoSelect, _setAutoSelect )				# 任何时候是否自动选择一项
	pySelItem = property( _getSelItem, _setSelItem )					# 获取/设置当前选中的选项
	selIndex = property( _getSelIndex, _setSelIndex )					# 获取/设置当前选中的索引

	width = property( FlexWindow._getWidth )							# 获取下拉列表的宽度
	height = property( FlexWindow._getHeight )							# 获取下拉列表的高度


# --------------------------------------------------------------------
# implement combo item class
# --------------------------------------------------------------------
class ComboItem( SingleColListItem ) :
	def __init__( self, text = "", item = None ) :
		SingleColListItem.__init__( self, item )
		self.__pyComboBox = None
		self.text = text

	def __del__( self ) :
		SingleColListItem.__del__( self )
		if Debug.output_del_ComboBox :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# friend methods
	# ----------------------------------------------------------------
	def setComboBox__( self, pyComboBox ) :
		"""
		设置所属的 comboBox（只给 ComboList 调用）
		"""
		if pyComboBox is None :
			self.__pyComboBox = None
		else :
			self.__pyComboBox = weakref.ref( pyComboBox )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getComboBox( self ) :
		if self.__pyComboBox is None :
			return self.__pyComboBox
		return self.__pyComboBox()

	def _setText( self, text ) :
		if text == self.text : return
		SingleColListItem._setText( self, text )
		if self.pyComboBox :
			self.pyComboBox.onItemTextChanged__( self )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyComboBox = property( _getComboBox )									# 获取所属的 ComboBox
	text = property( SingleColListItem._getText, _setText )
