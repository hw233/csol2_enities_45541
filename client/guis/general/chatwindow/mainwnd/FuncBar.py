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
		self.pyChannelBtn_ = ChannelButton( bar.channelBtn )								# 频道选择列表
		self.pyChannelBtn_.onMouseEnter.bind( self.onMouseEnter_ )
		self.pyChannelBtn_.onLClick.bind( self.showBar )
		self.pyChannelBtn_.onChannelSelectChanged.bind( self.onChannelSelectChanged_ )

		self.pyWhisper_ = WhisperInputBox( bar.cbWhisper )									# 密语对象输入框
		self.pyWhisper_.h_dockStyle = "RIGHT"
		self.pyWhisper_.pyComboList_.posZSegment = ZSegs.L4
		self.pyWhisper_.onKeyDown.bind( self.onWhisperKeyDown_ )
		self.pyWhisper_.onTabIn.bind( self.onWhisperTabIn_, True )
		self.pyWhisper_.onTabIn.bind( self.__onInputTabIn, True )							# True 参数，表示可以添加同一个类内的多个方法
		self.pyWhisper_.onTabOut.bind( self.__onInputTabOut )

		self.pyMSGInput_ = MSGInputBox( bar.msgBar, self )									# 消息输入框
		self.pyMSGInput_.h_dockStyle = "HFILL"
		self.pyMSGInput_.onKeyDown.bind( self.onMSGInputKeyDown_ )
		self.pyMSGInput_.onTabIn.bind( self.onMSGInputTabIn_, True )
		self.pyMSGInput_.onTabIn.bind( self.__onInputTabIn, True )
		self.pyMSGInput_.onTabOut.bind( self.__onInputTabOut )
		msgInserter.setDefInputObj( self.pyMSGInput_ )										# 作为默认的插入消息的接收框

		self.tabSwitcher_ = TabSwitcher( [self.pyMSGInput_, self.pyWhisper_] )				# 焦点转移控件

		self.__visibleDetectCBID = 0														# 侦测鼠标是否在功能条上
		self.__focusCBID = 0
		self.__triggers = {}
		self.__registerTriggers()

		rds.shortcutMgr.setHandler( "CHAT_TOGGLE_TABSTOP", self.__toggleTabStop )			# 获取/退出输入焦点
		rds.shortcutMgr.setHandler( "CHAT_ACTIVE_CHANNEL", self.__activeChannel )			# 激活输入，并输入频道快捷前缀
		rds.shortcutMgr.setHandler( "CHAT_WHISPER_TARGET", self.__whisperWithTarget )		# 对当前目标进行密语
		rds.shortcutMgr.setHandler( "CHAT_RESPONSE_LAST_WHISPER", self.__responseLastWhisper )	# 回复最近的密聊目标


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
		检测 funcbar 是否应该可见
		"""
		if self.needToShowed_() or self.pyBinder.isResizing :
			self.__visibleDetectCBID = BigWorld.callback( 3.0, self.__visibleDetect )
		else :
			self.hideBar()

	# -------------------------------------------------
	def __toggleTabStop( self ) :
		"""
		按回车键获得输入焦点
		"""
		if not self.visible :
			return False
		else :
			self.showBar()
			self.pyMSGInput_.tabStop = True
		return True

	def __activeChannel( self ) :
		"""
		按指令前缀“/”时激活聊天输入
		"""
		self.showBar()
		self.pyMSGInput_.tabStop = True
		self.pyMSGInput_.text = "/"
		return True

	def __whisperWithTarget( self ) :
		"""
		对当前目标进行密语
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
		回复最近的密聊目标
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
		消息输入框或密语对象输入框获得焦点时被触发
		"""
		self.showBar()

	def __onInputTabOut( self ) :
		"""
		消息输入框或密语对象输入框失去焦点时被触发
		"""
		if not self.needToShowed_() :
			self.hideBar()

	# ---------------------------------------
	def __activeSender( self, channel, receiver ) :
		"""
		激活发送消息窗口
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
		发送消息
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
		重新恢复为默认状态
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
		是否需要显示
		"""
		if self.isMouseHit() :
			return True
		if self.tabStop :
			return True
		return False
	# -------------------------------------------------
	def onMouseEnter_( self ) :
		"""
		鼠标进入时被触发
		"""
		self.showBar()

	def onMouseLeave_( self ) :
		"""
		鼠标离开时被触发
		"""
	#	if not self.needToShowed_() :
	#		self.hideBar()						# 改为不马上隐藏
		return True

	# -------------------------------------------------
	def onChannelSelectChanged_( self, channel ) :
		"""
		当某个频道选中是被调用
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
		私聊对象输入框获得焦点时被触发
		"""
		self.selectChinnelViaID( csdefine.CHAT_CHANNEL_WHISPER )

	def onWhisperKeyDown_( self, key, mods ) :
		"""
		焦点在私聊对象输入框中，并且按下键盘按键时被触发
		"""
		if key == KEY_RETURN or key == KEY_NUMPADENTER and mods == 0 :
			self.pyMSGInput_.tabStop = True
			return True
		return self.onKeyDown_( key, mods )

	def onMSGInputKeyDown_( self, key, mods ) :
		"""
		焦点在信息输入框中，并且按下键盘按键时被触发
		"""
		if key == KEY_RETURN or key == KEY_NUMPADENTER :
			self.__sendMessage()
			return True
		return self.onKeyDown_( key, mods )

	def onMSGInputTabIn_( self ) :
		"""
		私聊对象输入框撤离焦点时被触发
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
		显示功能条
		"""
		self.__fader.value = 1
		if self.__visibleDetectCBID == 0 :
			self.__visibleDetect()

	def hideBar( self ) :
		"""
		隐藏功能条
		"""
		self.__fader.value = 0
		BigWorld.cancelCallback( self.__visibleDetectCBID )
		self.__visibleDetectCBID = 0

	# -------------------------------------------------
	def whisperTo( self, name ) :
		"""
		与指定对象进行密语
		"""
		self.selectChinnelViaID( csdefine.CHAT_CHANNEL_WHISPER )
		self.pyWhisper_.text = name
		self.pyMSGInput_.tabStop = True

	def insertMessage( self, text ) :
		"""
		往信息熟人框中输入一段文本
		注：提供这个接口不是很恰当，但外层确实需要该接口
		"""
		self.pyMSGInput_.insertMessage( text )

	def selectChinnelViaID( self, chid ) :
		"""
		切换至id指定的频道
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
		if tabStop :											# 将焦点传给消息输入框
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
	pyCHItems = property( lambda self : self.pyChannelBtn_.pyItems )				# 获取所有频道
	channelCount = property( lambda self : self.pyChannelBtn_.channelCount )		# 获取频道数量
	pySelCHItem = property( lambda self : self.pyChannelBtn_.pySelItem )			# 获取/设置当前点击选中的频道
	pyCheckedCHItems = property( lambda self : self.pyChannelBtn_.pyCheckedItems )	# 获取当前 Check 选中的所有频道

	width = property( HFrame._getWidth, HFrame._setWidth )