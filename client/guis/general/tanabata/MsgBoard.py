# -*- coding: gb18030 -*-
# $Id: Bulletin.py $

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.Button import Button
from AbstractTemplates import Singleton
from guis.controls.ODComboBox import ODComboBox
from guis.tooluis.CSRichText import CSRichText
from guis.controls.StaticText import StaticText
from guis.controls.CheckBox import CheckBoxEx
from config.client.msgboxtexts import Datas as mbmsgs
from guis.tooluis.CSMLRichTextBox import CSMLRichTextBox
import csconst

class MsgBoard( Window ):
	
	__instance = None
	
	def __init__( self ):
		assert MsgBoard.__instance is None ,"MsgBoard instance has been created"
		MsgBoard.__instance = self
		wnd = GUI.load( "guis/general/tanabata/msgboard.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.isAnony = False
		self.isSendMail = True
		self.__initialize( wnd )
		self.addToMgr( "msgBoard" )
		rds.mutexShowMgr.addMutexRoot( self, MutexGroup.TANABATA1 )

	def __del__(self):
		"""
		just for testing memory leak
		"""
		Window.__del__( self )
		if Debug.output_del_MsgBoard:
			INFO_MSG( str( self ) )
		
	def __initialize( self, wnd ) :
		labelGather.setPyLabel( self.pyLbTitle_, "Tanabata:MsgBoard", "lbTitle" )
		self.__pyCBFilter = ODComboBox( wnd.cbFilter )
		self.__pyCBFilter.onItemSelectChanged.bind( self.__onFilterChanged )
		self.__pyCBFilter.readOnly = True
		self.__pyCBFilter.autoSelect = False
		
		self.__pyRTBMsg = CSMLRichTextBox( wnd.frmInput.clipPanel, wnd.frmInput.sbar )		# 消息输入框
		self.__pyRTBMsg.clearTemplates()
		self.__pyRTBMsg.maxLength = 100
		self.__pyRTBMsg.onTextChanged.bind( self.__onTextChanged )

		self.__pySTRemain = StaticText( wnd.stRemain )							# 剩余字数
		remainLength = int( self.__pyRTBMsg.maxLength ) - int( self.__pyRTBMsg.length )
		self.__pySTRemain.text = labelGather.getText( "Tanabata:MsgBoard", "stRemain", remainLength )

		self.__pyCBAnony = CheckBoxEx( wnd.frmProp.cbAnony )	# 是否匿名
		self.__pyCBAnony.checked = False
		labelGather.setPyLabel( self.__pyCBAnony.pyText_, "Tanabata:MsgBoard", "anonySend" )
		self.__pyCBAnony.onCheckChanged.bind( self.__anonyChange )
		
		self.__pyCBMail = CheckBoxEx( wnd.frmProp.cbSendMail )		# 是否发邮件
		self.__pyCBMail.checked = True
		labelGather.setPyLabel( self.__pyCBMail.pyText_, "Tanabata:MsgBoard", "mailSend" )
		self.__pyCBMail.onCheckChanged.bind( self.__sendMailChange )
		
		self.__pyBtnSend = Button( wnd.btnSend )
		self.__pyBtnSend.setStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyLabel( self.__pyBtnSend, "Tanabata:MsgBoard", "btnSend" )
		self.__pyBtnSend.onLClick.bind( self.__onSend )
		
		self.__pyBtnCancel = Button( wnd.btnCancel )
		self.__pyBtnCancel.setStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyLabel( self.__pyBtnCancel, "Tanabata:MsgBoard", "btnCancel" )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )
		
		labelGather.setLabel( wnd.frmInput.bgTitle.stTitle, "Tanabata:MsgBoard", "inputTitle" )
		labelGather.setLabel( wnd.frmProp.bgTitle.stTitle, "Tanabata:MsgBoard", "propTitle" )
		labelGather.setLabel( wnd.friendText, "Tanabata:MsgBoard", "choiceFriend" )

	def __onFilterChanged( self, index ):
		"""
		选择发送对象
		"""
		self.__pyRTBMsg.enable = index != -1
		
	def __onTextChanged( self ):
		"""
		"""
		remainLength = int( self.__pyRTBMsg.maxLength ) - int( self.__pyRTBMsg.wlength )
		self.__pySTRemain.text = labelGather.getText( "Tanabata:MsgBoard", "stRemain" )%remainLength
		
	def __anonyChange( self, checked ):
		"""
		是否匿名
		"""
		if self.isAnony != checked:
			self.isAnony = checked
	
	def __sendMailChange( self, checked ):
		"""
		是否发送邮件
		"""
		if self.isSendMail != checked:
			self.isSendMail = checked
	
	def __onSend( self ):
		if self.__pyCBFilter.selItem is None:
			showAutoHideMessage( 3.0, 0x0e62, "", MB_OK )
			return
		msg = self.__pyRTBMsg.text
		if msg == "" :
			# "请输入表白信息"
			showAutoHideMessage( 3.0, 0x0e63, "", MB_OK )
			return
		elif len( msg ) < 10:
			showAutoHideMessage( 3.0, 0x0e64, "", MB_OK )
			return
		elif rds.wordsProfanity.searchMsgProfanity( msg ) :
			# "要发送消息含有禁用词汇!"
			showAutoHideMessage( 3.0, mbmsgs[0x0e66], "", MB_OK )
			return
		name = self.__pyCBFilter.selItem
		BigWorld.player().base.sendLoveMsg( name, msg, self.isAnony, self.isSendMail )
		
	def __onCancel( self ):
		"""
		取消发送
		"""
		self.hide()
	
	@staticmethod
	def instance():
		if MsgBoard.__instance is None:
			MsgBoard.__instance = MsgBoard()
		return MsgBoard.__instance

	@staticmethod
	def getInstance():
		"""
		"""
		return MsgBoard.__instance
	
	def onLeaveWorld( self ) :
		Window.onLeaveWorld( self )
		self.hide()

	def show( self, pyOwner = None ):
		self.__pyCBFilter.clearItems()
		labelGather.setPyLabel( self.__pyCBFilter.pyBox_, "Tanabata:MsgBoard", "friendName" )
		Window.show( self, pyOwner )
		self.__pyRTBMsg.tabStop = True
		self.__pyCBAnony.checked = self.isAnony
		self.__pyCBMail.checked = self.isSendMail
		self.__pyRTBMsg.selectAll()
		friends = BigWorld.player().friends
		self.__pyCBFilter.addItems( friends.keys() )
		
	def hide( self ):
		self.__pyRTBMsg.text = ""
		Window.hide( self )
		self.removeFromMgr()
		MsgBoard.__instance = None