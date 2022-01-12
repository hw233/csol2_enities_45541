# -*- coding: gb18030 -*-
#
# $Id: ChatWindow.py,v 1.60 2008-09-04 01:00:31 huangyongwei Exp $

"""
imlement text for input message

2009/03/17: writen by huangyongwei
"""

import weakref
import csconst
from ChatFacade import emotionParser, chatFacade
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.FlexExWindow import HVFlexExWindow
from guis.common.ODListWindow import ODListWindow
from guis.controls.Control import Control
from guis.controls.ODComboBox import ODComboBox, IBox
from guis.controls.Button import Button
from guis.tooluis.CSRichTextBox import CSRichTextBox
from guis.tooluis.fulltext.FullText import FullText as BaseFullText
from guis.tooluis.CSRichTextBox import EItem
from guis.tooluis.CSRichTextBox import LItem

class MSGInputBox( Control ) :
	__cc_history_maxcount	= 60

	def __init__( self, box, pyBinder ) :
		Control.__init__( self, box, pyBinder )
		self.pyCBInput_ = ODComboBox( box.cbMSG, InputBox )						# 消息输入框
		self.pyCBInput_.itemHeight = emotionParser.cc_emote_size[1]
		self.pyCBInput_.ownerDraw = True
		self.pyCBInput_.h_dockStyle = "HFILL"
		self.pyCBInput_.readOnly = False
		self.pyCBInput_.viewCount = 16
		self.pyCBInput_.viewItem = ""
		self.pyCBInput_.pyComboList_.posZSegment = ZSegs.L4
		self.pyCBInput_.pyBox.maxLength = csconst.CHAT_MESSAGE_UPPER_LIMIT
		self.pyCBInput_.onViewItemInitialized.bind( self.__onInputBoxInitialized )
		self.pyCBInput_.onDrawItem.bind( self.__onInputBoxDrawItem )
		self.pyCBInput_.onItemMouseEnter.bind( self.__onInputBoxMouseEnter )
		self.pyCBInput_.onItemMouseLeave.bind( self.__onInputBoxMouseLeave )
		self.pyCBInput_.onKeyDown.bind( self.onKeyDown_ )
		self.pyCBInput_.onTabIn.bind( self.onTabIn_ )
		self.pyCBInput_.onTabOut.bind( self.onTabOut_ )

		self.pyActionsBtn_ = Button( box.actionsBtn )							# 行为列表按钮
		self.pyActionsBtn_.h_dockStyle = "RIGHT"
		self.pyActionsBtn_.setStatesMapping( UIState.MODE_R2C2 )
		self.pyActionsBtn_.onLClick.bind( self.__showActionList )
		self.pyEmoteBtn_ = Button( box.emoteBtn )								# 表情选择
		self.pyEmoteBtn_.h_dockStyle = "RIGHT"
		self.pyEmoteBtn_.setStatesMapping( UIState.MODE_R2C2 )
		self.pyEmoteBtn_.onLClick.bind( self.__showEmotions )

		self.__tmpMsg = ""														# 保存当前输入的消息


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		产生控件事件
		"""
		Control.generateEvents_( self )
		self.__onMessageReady = self.createEvent_( "onMessageReady" )			# 消息准备好，通知发送

	@property
	def onMessageReady( self ) :
		"""
		左键点击某个超链接消息时被触发
		"""
		return self.__onMessageReady


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onInputBoxInitialized( self, pyViewItem ) :
		"""
		初始化历史选项
		"""
		box = util.copyGui( pyViewItem.gui )
		pyViewItem.gui.addChild( box )
		pyBox = CSRichTextBox( box )
		pyBox.font = self.pyCBInput_.font
		pyBox.width -= 8
		pyBox.pos = 4, 0
		pyBox.readOnly = True
		pyBox.canTabIn = False
		pyBox.focus = False
		pyBox.moveFocus = False
		pyBox.crossFocus = False
		pyBox.vTextAlign = "MIDDLE"
		pyViewItem.pyBox = pyBox

	def __onInputBoxDrawItem( self, pyViewItem ) :
		"""
		重画历史选项
		"""
		pyBox = pyViewItem.pyBox
		pyBox.width = pyViewItem.width - 8
		if pyViewItem.selected :
			pyBox.foreColor = self.pyCBInput_.itemSelectedForeColor				# 选中状态下的前景色
			pyViewItem.color = self.pyCBInput_.itemSelectedBackColor			# 选中状态下的背景色
		elif pyViewItem.highlight :
			pyBox.foreColor = self.pyCBInput_.itemHighlightForeColor			# 高亮状态下的前景色
			pyViewItem.color = self.pyCBInput_.itemHighlightBackColor			# 高亮状态下的背景色
		else :
			pyBox.foreColor = self.pyCBInput_.itemCommonForeColor
			pyViewItem.color = self.pyCBInput_.itemCommonBackColor
		pyBox.text = pyViewItem.listItem

	def __onInputBoxMouseEnter( self, pyViewItem ) :
		"""
		鼠标进入选项
		"""
		pyBox = pyViewItem.pyBox
		if pyBox.textWidth > pyBox.width :
			FullText.show( pyViewItem, pyBox )

	def __onInputBoxMouseLeave( self, pyViewItem ) :
		"""
		鼠标离开选项
		"""
		FullText.hide()

	# -------------------------------------------------
	def __onEmotionChosen( self, sign ) :
		"""
		某个表情选中时被触发
		"""
		if rds.ruisMgr.emotionBox.pyBinder == self :
			if not self.pyCBInput_.tabStop :
				self.pyCBInput_.tabStop = True
			self.pyCBInput_.pyBox.notifyInput( sign )

	# -------------------------------------------------
	def __showActionList( self ) :
		"""
		显示行为技能列表
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_SKILL_WINDOW", 3 )

	def __showEmotions( self ) :
		"""
		显示表情选择窗口
		"""
		emotionBox = rds.ruisMgr.emotionBox
		emotionBox.toggle( self.__onEmotionChosen, self )
		emotionBox.left = self.leftToScreen + 15.0
		emotionBox.bottom = self.topToScreen + 10.0
		if not self.pyCBInput_.tabStop :
			self.pyCBInput_.tabStop = True


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		"""
		当焦点在输入框中，并有按键按下时被调用
		"""
		return Control.onKeyDown_( self, key, mods )

	def onTabIn_( self ) :
		"""
		获得焦点时被调用( 覆盖父类的 onTabIn_ 方法 )
		"""
		self.onTabIn()
		rds.helper.courseHelper.openWindow( "liaotian_chuangkou" )

	def onTabOut_( self ) :
		"""
		失去焦点时被调用( 覆盖父类的 onTabOut_ 方法 )
		"""
		self.onTabOut()
		rds.ruisMgr.emotionBox.hide()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def insertMessage( self, text ) :
		"""
		往信息输入框中输入一段文本
		注：提供这个接口不是很恰当，但外层确实需要该接口
		"""
		if not self.tabStop : self.tabStop = True
		self.pyCBInput_.pyBox.notifyInput( text, 4 )						# 假设物品名字的字数都是 4

	def saveMessage( self, text ) :
		"""
		保存一条消息到历史列表
		"""
		text = text.strip()
		if text == "" : return
		if text in self.pyCBInput_.items :									# 历史列表中已经存在该密语者
			self.pyCBInput_.sort( key = lambda pyItem : pyItem == text )	# 则把最新用过的密语者放到最后
		else :
			if self.pyCBInput_.itemCount >= self.__cc_history_maxcount :	# 如果历史数量已经超过指定值
				self.pyCBInput_.removeItemOfIndex( 0 )						# 删除最前面一个
			self.pyCBInput_.addItem( text )									# 并将新的添加到最后
		self.pyCBInput_.selIndex = self.pyCBInput_.itemCount - 1			# 选中最新添加的选项

	def notifyInput( self, text ) :
		"""
		往信息输入框中输入一段文本
		这个接口在msgInserter中使用
		"""
		self.insertMessage( text )

	# -------------------------------------------------
	def reset( self ) :
		"""
		重新恢复为默认状态
		"""
		self.pyCBInput_.pyBox.text = ""
		self.pyCBInput_.clearItems()


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( lambda self : self.pyCBInput_.pyBox.text, \
		lambda self, v : self.pyCBInput_.pyBox._setText( v ) )
	wtext = property( lambda self : self.pyCBInput_.pyBox.wtext )
	viewText = property( lambda self : self.pyCBInput_.pyBox.viewText )
	tabStop = property( lambda self : self.pyCBInput_.tabStop, \
		lambda self, v : self.pyCBInput_._setTabStop( v ) )


# --------------------------------------------------------------------
# 重写输入框
# --------------------------------------------------------------------
class InputBox( CSRichTextBox, IBox ) :
	__cc_exposed_attrs = set( [
		"text",											# 当前文本
		] )												# 需要公开作为 ComboBox 属性的属性

	def __init__( self, box, pyBombo ) :
		CSRichTextBox.__init__( self, box )
		IBox.__init__( self, pyBombo )
		self.__followSelCBID = 0							# 输入文本时，跟随选中列表选项的 callback ID

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __selectStartswithInput( self ) :
		"""
		选中以 box 中输入的文本开头的选项
		"""
		if self.readOnly : return								# 只有在非只读时，才会存在文本框中的文本与选项文本不一致的问题
		wtext = self.wtext
		if wtext == "" : return									# 空文本不计算
		pyComboList_ = self.pyComboList_
		items = []
		for index, item in enumerate( pyComboList_.items ) :	# 获取列表中所有以 Box 中文本开头的选项
			if item.startswith( wtext ) :
				items.append( ( index, item ) )
		if len( items ) == 0 :									# 如果没有与 Box 中文本开头的选项
			pyComboList_.selIndex = -1							# 则预不选中任何选项
		else :													# 否则
			items.sort( key = lambda item : item[1] )			# 选中列表中第一个选项
			pyComboList_.selIndex = items[0][0]

	def __switchChannel( self, text ) :
		if text == "" or text[0] != "/" : return
		cmds = text.split( " " )								# 拆分指令
		if len( cmds ) < 2 : return
		shortcut = cmds[0][1:]									# 取指令部分，并去掉"/"号
		chid = chatFacade.shortcutToCHID( shortcut )
		if chid is None : return
		self.pyTopParent.selectChinnelViaID( chid )				# pyTopParent是ChatWindow
		self.text = text[len(cmds[0])+1:]						# 重新赋值为非指令部分（+1是连后面的一个空格一起去掉）


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
		return self.viewText

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
		CSRichTextBox.onTextChanged_( self )
		self.__switchChannel( self.text )							# 尝试切换至快捷键指定的频道
		pyEItems = []
		for pyElem in self.pyElems_:
			if isinstance( pyElem, EItem ) or isinstance( pyElem,LItem ):
				pyEItems.append( pyElem )
		chatFacade.onChatObjCount( len( pyEItems ) )
		if not self.pyComboBox.isDropped : return
		BigWorld.cancelCallback( self.__followSelCBID )
		self.__followSelCBID = BigWorld.callback( 0.3, self.__selectStartswithInput )

	def onItemSelectChanged_( self, index ) :
		"""
		选项改变时被调用
		"""
		if index < 0 :
			self.text = ""
		else :
			self.text = self.pyComboBox.items[index]


# --------------------------------------------------------------------
# 重写输入框
# --------------------------------------------------------------------
class FullText( BaseFullText ) :
	def __init__( self ) :
		BaseFullText.__init__( self )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onFullDuplicate_( self, pyUI ) :
		"""
		复制要完全显示的 UI 副本
		"""
		gui = self.gui
		dup = util.copyGuiTree( pyUI.gui )
		dup.scroll = 0, 0
		dup.width = pyUI.textWidth
		gui.addChild( dup, "dup" )
		self.__pyDup = PyGUI( dup )
		self.__pyDup.pos = self.edgeLeft_, self.edgeTop_
		self.width = self.__pyDup.width + self.edgeLeft_ * 2
		self.height = self.__pyDup.height + self.edgeTop_ * 2
