# -*- coding: gb18030 -*-

# $Id: RoleChat.py,v 1.17 2008-08-30 09:03:04 huangyongwei Exp $
"""
implement broadcaster for player

2009.03.28 : writen by huangyongwei
"""

import csdefine
import csconst
import event.EventCenter as ECenter
from ChatFacade import chatFacade
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.RadioButton import RadioButtonEx
from guis.controls.CheckerGroup import CheckerGroup
from guis.tooluis.CSMLRichTextBox import CSMLRichTextBox
from guis.tooluis.CSRichText import CSRichText
from Receiver import Receivers
import Language

class Sender( Window ) :
	def __init__( self ) :
		wnd = GUI.load( "guis/general/chatwindow/rolebroadcaster/sender/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.addToMgr()

		self.__initialize( wnd )
		self.__pyReceivers = Receivers()								# 广播接收窗口

	def __initialize( self, wnd ) :
		self.__pyRTBMsg = CSMLRichTextBox( wnd.frmInput.clipPanel, wnd.frmInput.sbar )		# 信息输入框
		self.__pyRTBMsg.forceNewline = False
		self.__pyRTBMsg.clearTemplates()								# 默认选中的是地音（不解释表情）
		self.__pyRTBMsg.maxLength = min( 70, csconst.CHAT_MESSAGE_UPPER_LIMIT )
		self.__pyRTBMsg.onTextChanged.bind( self.__onTextChanged )

		self.__pyBTNEmote = Button( wnd.frmProp.btnEmote )				#“表情”按钮
		self.__pyBTNEmote.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBTNEmote.onLClick.bind( self.__showEmotions )

		self.__pyBTNSend = Button( wnd.btnSend )						#“发送”按钮
		self.__pyBTNEmote.enable = False
		self.__pyBTNSend.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBTNSend.onLClick.bind( self.__sendMessage )
#		self.setOkButton( self.__pyBTNSend )

		self.__pyBTNCancel = Button( wnd.btnCancel )					#“取消按钮”
		self.__pyBTNCancel.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBTNCancel.onLClick.bind( self.hide )

		self.__pyRBWelkin = RadioButtonEx( wnd.frmProp.rbWelkin )				# 天音选项
		self.__pyRBTunnel = RadioButtonEx( wnd.frmProp.rbTunnel )				# 地音选项
		self.__pyRBTunnel.checked = True
		self.__checkerGroup = CheckerGroup( self.__pyRBWelkin, self.__pyRBTunnel )
		self.__checkerGroup.onCheckChanged.bind( self.__onYellRadioCheckChanged )

		self.__pySTGold = StaticText( wnd.frmProp.boxGold.stText )						# 金币数
		self.__pySTGold.text = "--"
		self.__pySTSilver = StaticText( wnd.frmProp.boxSilver.stText )					# 银币数
		self.__pySTSilver.text = "--"

		self.__pyRTRemind = CSRichText( wnd.frmProp.rtRemind )					# 提醒

		self.__pySTRemain = StaticText( wnd.stRemain )							# 银币数
		remainLength = int( self.__pyRTBMsg.maxLength ) - int( self.__pyRTBMsg.length )
		self.__pySTRemain.text = labelGather.getText( "ChatWindow:RoleBroadcaster", "stRemain", remainLength )

		# ---------------------------------------------
		# 设置文本标签
		# ---------------------------------------------
		labelGather.setLabel( wnd.lbTitle, "ChatWindow:RoleBroadcaster", "title" )
		labelGather.setLabel( wnd.inputBg.bgTitle.stTitle, "ChatWindow:RoleBroadcaster", "inputTitle")
		labelGather.setLabel( wnd.frmProp.bgTitle.stTitle, "ChatWindow:RoleBroadcaster", "propTitle")
		labelGather.setPyBgLabel( self.__pyRBWelkin, "ChatWindow:RoleBroadcaster", "rbWelkin" )
		labelGather.setPyBgLabel( self.__pyRBTunnel, "ChatWindow:RoleBroadcaster", "rbTunnel" )
		labelGather.setPyBgLabel( self.__pyBTNSend, "ChatWindow:RoleBroadcaster", "btnSend" )
		labelGather.setPyBgLabel( self.__pyBTNCancel, "ChatWindow:RoleBroadcaster", "btnCancel" )
		labelGather.setPyBgLabel( self.__pyRTRemind, "ChatWindow:RoleBroadcaster", "rtRemind" )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __insertEmotion( self, sign ) :
		if self.__pyRTBMsg.tabStop :
			signLen = len( sign )
			remainLength = int( self.__pyRTBMsg.maxLength ) - int( self.__pyRTBMsg.length )
			if remainLength < signLen:return
			self.__pyRTBMsg.notifyInput( sign )

	# -------------------------------------------------
	def __showEmotions( self ) :
		"""
		显示表情按钮被点击时触发
		"""
		emotionBox = rds.ruisMgr.emotionBox
		emotionBox.toggle( self.__insertEmotion, self )
		emotionBox.top = self.__pyRTBMsg.topToScreen
		emotionBox.left = self.__pyRTBMsg.rightToScreen

	def __sendMessage( self ) :
		"""
		发送
		"""
		if self.__pyRTBMsg.wtext.strip() == "" :
			# "请输入广播信息"
			showAutoHideMessage( 2.0, 0x0261, "", MB_OK )
			return
		if self.__pyRBWelkin.checked :
			chatFacade.sendChannelMessage( csdefine.CHAT_CHANNEL_WELKIN_YELL, self.__pyRTBMsg.wtext )
		else :
			chatFacade.sendChannelMessage( csdefine.CHAT_CHANNEL_TUNNEL_YELL, self.__pyRTBMsg.wtext )
		self.hide()

	def __onYellRadioCheckChanged( self, pyRadio ) :
		"""
		选中天音/地音
		"""
		if pyRadio == self.__pyRBWelkin :
			self.__pyBTNEmote.enable = True
			self.__pyRTBMsg.setCSTemplates()
		else :
			self.__pyBTNEmote.enable = False
			rds.ruisMgr.emotionBox.hide()
			self.__pyRTBMsg.clearTemplates()

	def __onTextChanged( self ):
		remainLength = int( self.__pyRTBMsg.maxLength ) - int( self.__pyRTBMsg.wlength )
		self.__pySTRemain.text = labelGather.getText( "ChatWindow:RoleBroadcaster", "stRemain", remainLength )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		if eventMacro == "EVT_ON_SPECIAL_GET_ITEMS_PRICES" :
			prices = args[0]
			wsuccess, wPrice = prices[csconst.CHAT_WELKIN_ITEM]
			tsuccess, tPrice = prices[csconst.CHAT_TUNNEL_ITEM]

			if wsuccess == csdefine.SPECIALSHOP_REQ_SUCCESS :
				self.__pySTGold.text = str( int( wPrice ) )
			else :
				self.__pySTGold.text = "--"
			if tsuccess == csdefine.SPECIALSHOP_REQ_SUCCESS :
				self.__pySTSilver.text = str( int( tPrice ) )
			else :
				self.__pySTSilver.text = "--"

	def onLeaveWorld( self ) :
		Window.onLeaveWorld( self )
		self.__pyRTBMsg.text = ""
		self.hide()

	# --------------------------------------------
	def show( self ) :
		ECenter.registerEvent( "EVT_ON_SPECIAL_GET_ITEMS_PRICES", self )
		chatItems = [csconst.CHAT_WELKIN_ITEM, csconst.CHAT_TUNNEL_ITEM]
		BigWorld.player().spe_requestItemsPrices( chatItems )
		Window.show( self )
		self.__pyRTBMsg.tabStop = True
		self.__pyRTBMsg.selectAll()

	def hide( self ) :
		ECenter.unregisterEvent( "EVT_ON_SPECIAL_GET_ITEMS_PRICES", self )
		Window.hide( self )
