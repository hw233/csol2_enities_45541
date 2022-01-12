# -*- coding: gb18030 -*-
#
# $Id: FuncBar.py,v 1.60 2008-09-04 01:00:31 huangyongwei Exp $

"""
imlement function bar for send message

2009/03/17: writen by huangyongwei
"""

import csdefine
import csconst
import csstatus
from ChatFacade import chatFacade, msgInserter
import guis.general.chatwindow.YellVerifyBox as YellVerifyBox
from guis import *
from guis.common.Frame import HFrame
from guis.controls.Control import Control
from guis.controls.TabSwitcher import TabSwitcher
from ChannelButton import ChannelButton
from WhisperInputBox import WhisperInputBox
from MSGInputBox import MSGInputBox


class FuncBar( HFrame, Control ) :
	def __init__( self, bar, pyBinder ) :
		HFrame.__init__( self, bar )
		Control.__init__( self, bar, pyBinder )
		self.crossFocus = True

		self.__fader = bar.fader
		self.__fader.speed = 0.5
		self.__fader.value = 0
		self.pyChannelBtn_ = ChannelButton( bar.channelBtn )								# Ƶ��ѡ���б�
		self.pyChannelBtn_.onMouseEnter.bind( self.onMouseEnter_ )
		self.pyChannelBtn_.onLClick.bind( self.showBar )
		self.pyChannelBtn_.onChannelSelectChanged.bind( self.onChannelSelectChanged_ )

		self.pyWhisper_ = WhisperInputBox( bar.cbWhisper )									# ������������
		self.pyWhisper_.h_dockStyle = "RIGHT"
		self.pyWhisper_.pyComboList_.posZSegment = ZSegs.L4
		self.pyWhisper_.onKeyDown.bind( self.onWhisperKeyDown_ )
		self.pyWhisper_.onTabIn.bind( self.onWhisperTabIn_, True )
		self.pyWhisper_.onTabIn.bind( self.__onInputTabIn, True )							# True ��������ʾ�������ͬһ�����ڵĶ������
		self.pyWhisper_.onTabOut.bind( self.__onInputTabOut )

		self.pyMSGInput_ = MSGInputBox( bar.msgBar, self )									# ��Ϣ�����
		self.pyMSGInput_.h_dockStyle = "HFILL"
		self.pyMSGInput_.onKeyDown.bind( self.onMSGInputKeyDown_ )
		self.pyMSGInput_.onTabIn.bind( self.onMSGInputTabIn_, True )
		self.pyMSGInput_.onTabIn.bind( self.__onInputTabIn, True )
		self.pyMSGInput_.onTabOut.bind( self.__onInputTabOut )
		msgInserter.setDefInputObj( self.pyMSGInput_ )										# ��ΪĬ�ϵĲ�����Ϣ�Ľ��տ�

		self.tabSwitcher_ = TabSwitcher( [self.pyMSGInput_, self.pyWhisper_] )				# ����ת�ƿؼ�

		self.__visibleDetectCBID = 0														# �������Ƿ��ڹ�������
		self.__focusCBID = 0
		self.__triggers = {}
		self.__registerTriggers()

		rds.shortcutMgr.setHandler( "CHAT_TOGGLE_TABSTOP", self.__toggleTabStop )			# ��ȡ/�˳����뽹��
		rds.shortcutMgr.setHandler( "CHAT_ACTIVE_CHANNEL", self.__activeChannel )			# �������룬������Ƶ�����ǰ׺
		rds.shortcutMgr.setHandler( "CHAT_WHISPER_TARGET", self.__whisperWithTarget )		# �Ե�ǰĿ���������
		rds.shortcutMgr.setHandler( "CHAT_RESPONSE_LAST_WHISPER", self.__responseLastWhisper )	# �ظ����������Ŀ��


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_CHAT_ACTIVE_CHAT_SENDER"] = self.__activeSender
		self.__triggers["EVT_ON_CHAT_INSERT_MSG"] = self.pyMSGInput_.insertMessage
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	# -------------------------------------------------
	def __visibleDetect( self ) :
		"""
		��� funcbar �Ƿ�Ӧ�ÿɼ�
		"""
		if self.needToShowed_() or self.pyBinder.isResizing :
			self.__visibleDetectCBID = BigWorld.callback( 3.0, self.__visibleDetect )
		else :
			self.hideBar()

	# -------------------------------------------------
	def __toggleTabStop( self ) :
		"""
		���س���������뽹��
		"""
		if not self.visible :
			return False
		else :
			self.showBar()
			self.pyMSGInput_.tabStop = True
		return True

	def __activeChannel( self ) :
		"""
		��ָ��ǰ׺��/��ʱ������������
		"""
		self.showBar()
		self.pyMSGInput_.tabStop = True
		self.pyMSGInput_.text = "/"
		return True

	def __whisperWithTarget( self ) :
		"""
		�Ե�ǰĿ���������
		"""
		player = BigWorld.player()
		target = player.targetEntity
		if target is None :
			player.statusMessage( csstatus.WHISPER_FORBID_TARGET_IS_NONE )
		else :
			self.whisperTo( target.getName() )
		return True

	def __responseLastWhisper( self ) :
		"""
		�ظ����������Ŀ��
		"""
		channel = chatFacade.channels[csdefine.CHAT_CHANNEL_WHISPER]
		lastWhisper = channel.getLastWhisper()
		if lastWhisper == "" :
			self.pyWhisper_.tabStop = True
		else :
			self.whisperTo( lastWhisper )

	# -------------------------------------------------
	def __onInputTabIn( self ) :
		"""
		��Ϣ�������������������ý���ʱ������
		"""
		self.showBar()

	def __onInputTabOut( self ) :
		"""
		��Ϣ������������������ʧȥ����ʱ������
		"""
		if not self.needToShowed_() :
			self.hideBar()

	# ---------------------------------------
	def __activeSender( self, channel, receiver ) :
		"""
		�������Ϣ����
		"""
		self.showBar()
		pyItem = self.pyChannelBtn_.pyItems[channel.id]
		self.pyChannelBtn_.pySelItem = pyItem
		if channel.id == csdefine.CHAT_CHANNEL_WHISPER :
			if receiver == "" :
				self.pyWhisper_.tabStop = True
			else :
				self.pyWhisper_.text = receiver
				self.pyMSGInput_.tabStop = True
		else :
			self.pyMSGInput_.tabStop = True

	# -------------------------------------------------
	def __sendMessage( self ) :
		"""
		������Ϣ
		"""
		msg = self.pyMSGInput_.wtext.strip()
		if msg != "" :
			receiver = self.pyWhisper_.text.strip()
			channelID = self.pyChannelBtn_.pySelItem.channel.id
			chatFacade.sendChannelMessage( channelID, msg, receiver )
			self.pyMSGInput_.saveMessage( self.pyMSGInput_.wtext )
			self.pyMSGInput_.text = ""
		self.hideBar()
		self.pyMSGInput_.tabStop = False

	def __cancelFocus( self ):
		pySelPage = self.pyBinder.pyReceiver_.pySelPage
		if pySelPage.focus:
			pySelPage.focus = False
		BigWorld.cancelCallback( self.__focusCBID )
	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEnterWorld( self ) :
		self.pyChannelBtn_.reset()

	# -------------------------------------------------
	def onLeaveWorld( self ) :
		"""
		���»ָ�ΪĬ��״̬
		"""
		self.pyMSGInput_.reset()
		self.pyWhisper_.reset()
		self.__needYellVerify = True
		self.__focusCBID = 0

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def needToShowed_( self ) :
		"""
		�Ƿ���Ҫ��ʾ
		"""
		if self.isMouseHit() :
			return True
		if self.tabStop :
			return True
		return False
	# -------------------------------------------------
	def onMouseEnter_( self ) :
		"""
		������ʱ������
		"""
		self.showBar()

	def onMouseLeave_( self ) :
		"""
		����뿪ʱ������
		"""
	#	if not self.needToShowed_() :
	#		self.hideBar()						# ��Ϊ����������
		return True

	# -------------------------------------------------
	def onChannelSelectChanged_( self, channel ) :
		"""
		��ĳ��Ƶ��ѡ���Ǳ�����
		"""
		pySelPage = self.pyBinder.pyReceiver_.pySelPage
		if not pySelPage.focus:
			pySelPage.focus = True
			self.__focusCBID = BigWorld.callback( 0.5, self.__cancelFocus )
		if channel.id == csdefine.CHAT_CHANNEL_WHISPER :
			if not self.pyWhisper_.tabStop :
				self.pyWhisper_.tabStop = True
			whisperer = channel.getLastReceiver()
			if whisperer != "" and self.pyWhisper_.text.strip() == "" :
				self.pyWhisper_.text = whisperer
		else :
			self.pyWhisper_.text = ""
			self.pyMSGInput_.tabStop = True

	def onWhisperTabIn_( self ) :
		"""
		˽�Ķ���������ý���ʱ������
		"""
		self.selectChinnelViaID( csdefine.CHAT_CHANNEL_WHISPER )

	def onWhisperKeyDown_( self, key, mods ) :
		"""
		������˽�Ķ���������У����Ұ��¼��̰���ʱ������
		"""
		if key == KEY_RETURN or key == KEY_NUMPADENTER and mods == 0 :
			self.pyMSGInput_.tabStop = True
			return True
		return self.onKeyDown_( key, mods )

	def onMSGInputKeyDown_( self, key, mods ) :
		"""
		��������Ϣ������У����Ұ��¼��̰���ʱ������
		"""
		if key == KEY_RETURN or key == KEY_NUMPADENTER :
			self.__sendMessage()
			return True
		return self.onKeyDown_( key, mods )

	def onMSGInputTabIn_( self ) :
		"""
		˽�Ķ���������뽹��ʱ������
		"""
		if self.pyWhisper_.text.strip() == "" and \
			self.pyChannelBtn_.pySelItem.channel.id == csdefine.CHAT_CHANNEL_WHISPER :
				self.selectChinnelViaID( csdefine.CHAT_CHANNEL_NEAR )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eMacro, *args ) :
		self.__triggers[eMacro]( *args )

	# -------------------------------------------------
	def showBar( self ) :
		"""
		��ʾ������
		"""
		self.__fader.value = 1
		if self.__visibleDetectCBID == 0 :
			self.__visibleDetect()

	def hideBar( self ) :
		"""
		���ع�����
		"""
		self.__fader.value = 0
		BigWorld.cancelCallback( self.__visibleDetectCBID )
		self.__visibleDetectCBID = 0

	# -------------------------------------------------
	def whisperTo( self, name ) :
		"""
		��ָ�������������
		"""
		self.selectChinnelViaID( csdefine.CHAT_CHANNEL_WHISPER )
		self.pyWhisper_.text = name
		self.pyMSGInput_.tabStop = True

	def insertMessage( self, text ) :
		"""
		����Ϣ���˿�������һ���ı�
		ע���ṩ����ӿڲ��Ǻ�ǡ���������ȷʵ��Ҫ�ýӿ�
		"""
		self.pyMSGInput_.insertMessage( text )

	def selectChinnelViaID( self, chid ) :
		"""
		�л���idָ����Ƶ��
		"""
		self.pyChannelBtn_.selectChinnelViaID( chid )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getTabStop( self ) :
		if self.pyChannelBtn_.isDropped :
			return True
		if self.pyWhisper_.tabStop :
			return True
		if self.pyMSGInput_.tabStop :
			return True
		return Control._getTabStop( self )

	def _setTabStop( self, tabStop ) :
		if tabStop :											# �����㴫����Ϣ�����
			self.pyMSGInput_.tabStop = tabStop
		elif self.pyMSGInput_.tabStop :
			self.pyMSGInput_.tabStop = False
		elif self.pyWhisper_.tabStop :
			self.pyWhisper_.tabStop = False
		elif self.pyChannelBtn_.isDropped :
			self.pyChannelBtn_.collapse()
		return Control._setTabStop( self, tabStop )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	tabStop = property( _getTabStop, _setTabStop )
	pyCHItems = property( lambda self : self.pyChannelBtn_.pyItems )				# ��ȡ����Ƶ��
	channelCount = property( lambda self : self.pyChannelBtn_.channelCount )		# ��ȡƵ������
	pySelCHItem = property( lambda self : self.pyChannelBtn_.pySelItem )			# ��ȡ/���õ�ǰ���ѡ�е�Ƶ��
	pyCheckedCHItems = property( lambda self : self.pyChannelBtn_.pyCheckedItems )	# ��ȡ��ǰ Check ѡ�е�����Ƶ��

	width = property( HFrame._getWidth, HFrame._setWidth )