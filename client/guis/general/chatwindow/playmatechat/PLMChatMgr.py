# -*- coding: gb18030 -*-

# 好友聊天窗口及聊天记录管理器
# created by ganjinxing 2010-06-13

import time
import BigWorld
import csdefine
from Time import Time
from bwdebug import *
from ChatFacade import chatFacade
from AbstractTemplates import Singleton
from event import EventCenter as ECenter
from gbref import rds

from PLMNotifier import PLMNotifier
from PLMChatWindow import PLMChatWindow
from PLMLogBrowser import plmLogBrowser


class PLMChatMgr( Singleton ) :

	def __init__( self ) :
		self.__pyWnds = {}								# 保存聊天窗口
		self.__newMsgs = {}								# 未读消息记录
		self.__pyNotifier = None						# 新消息提示器

		chid = csdefine.CHAT_CHANNEL_PLAYMATE			# 绑定玩伴聊天频道
		chatFacade.bindChannelHandler( chid, self.__onReceiveMessage )

		self.__triggers = {}
		self.__registerTriggers()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		"""
		注册事件：进入、退出游戏，好友上线、下线，更新聊天对象
		"""
		self.__triggers[ "EVT_ON_ROLE_ENTER_WORLD" ] = self.__onEnterWorld
		self.__triggers[ "EVT_ON_ROLE_LEAVE_WORLD" ] = self.__onLeaveWorld
		self.__triggers[ "EVT_ON_UPDATE_CHAT_OBJ" ] = self.onUpdateChatObj
		self.__triggers[ "EVT_ON_RELATION_OFFLINE" ] = self.__onPlaymateLogout
		self.__triggers[ "EVT_ON_ROLE_UPDATE_RELATION" ] = self.__onPlaymateLogon
		self.__triggers[ "EVT_ON_ROLE_REMOVE_RELATION" ] = self.__onPlaymateRemove
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	# -------------------------------------------------
	def __calcNextPos( self ) :
		"""
		计算出下一个窗口弹出位置
		"""
		screenSize = BigWorld.screenSize()
		firstPos = 254, 120								# 第一个窗口的位置
		skipPos = 10, 22								# 下一个窗口的位置偏移值
		wndCount = len( self.__pyWnds ) - 1
		posX, posY = firstPos
		while wndCount > 0 :
			posX += skipPos[0]
			posY += skipPos[1]
			if posX + 20 > screenSize[0] :
				posX = firstPos[0]
			if posY + 20 > screenSize[1] :
				posY = firstPos[1]
			wndCount -= 1
		return posX, posY

	def __createChatWindow( self, objName ) :
		"""
		创建一个新的聊天窗口
		"""
		pyChatWnd = PLMChatWindow()
		pyChatWnd.onAfterClosed.bind( self.__onChatWndClosed )
		self.__pyWnds[ objName ] = pyChatWnd
		pyChatWnd.pos = self.__calcNextPos()
		pyChatWnd.show()
		return pyChatWnd

	def __onReceiveMessage( self, channel, spkID, spkName, msg, date = None ) :
		"""
		收到好友消息
		@param		channel	: 聊天频道
		@type		channel	: instance of Channel
		@param		spkID	: 发言者的ID
		@type		spkID	: INT64
		@param		spkName	: 发言者的名称
		@type		spkName	: string
		@param		msg		: 消息内容
		@type		msg		: string
		"""
		if date is None :
			date = time.strftime( "%H:%M:%S", Time.localtime() )	# 获取服务器时间
		pyChatWnd = self.__pyWnds.get( spkName )
		if pyChatWnd is None :
			self.__notifyNewMsg( channel, spkID, spkName, msg, date )
			self.__recordNewMsg( channel, spkID, spkName, msg, date )
		else :
			pyChatWnd.onReceiveMessage( channel, spkID, spkName, msg, date )
		self.__recordMsg( channel, spkID, spkName, msg, date )

	def __notifyNewMsg( self, channel, spkID, spkName, msg, date ) :
		"""
		通知玩家收到新的好友消息
		"""
		if self.__pyNotifier :
			self.__pyNotifier.notifyNewMsg()

	def __recordNewMsg( self, channel, spkID, spkName, msg, date ) :
		"""
		记录收到的新消息
		"""
		msgs = self.__newMsgs.get( spkName )
		if msgs is None :
			msgs = [ ( channel.id, spkID, spkName, msg, date ) ]
			self.__newMsgs[ spkName ] = msgs
		else :
			msgs.append( ( channel.id, spkID, spkName, msg, date ) )

	def __recordMsg( self, channel, spkID, spkName, msg, date ) :
		"""
		记录所有收到的消息
		"""
		plmLogBrowser.recordMsg( channel, spkID, spkName, msg, date )

	def __extractNewMsg( self, spkName ) :
		"""
		获取新消息并将消息从记录中移除
		"""
		msgs = self.__newMsgs.get( spkName )
		if msgs is None : return []
		del self.__newMsgs[ spkName ]
		return msgs

	def __allMsgRead( self ) :
		"""
		是否所有新消息都已阅读
		"""
		return len( self.__newMsgs ) == 0

	# -------------------------------------------------
	def __onChatWndClosed( self, pyChatWnd ) :
		"""
		聊天窗口关闭时触发
		"""
		for spkName, pyWnd in self.__pyWnds.iteritems() :
			if pyWnd == pyChatWnd :
				del self.__pyWnds[ spkName ]
				pyChatWnd.dispose()
				break
		else :
			ERROR_MSG( "ERROR! Chat window not in record! [%s]" % str( pyChatWnd ) )

	def __onNotifierClick( self ) :
		"""
		玩家点击
		"""
		for spkName in self.__newMsgs.iterkeys() :
			self.onReadNewMsg( spkName )
			break

	# -------------------------------------------------
	def __onPlaymateLogout( self, relationUID, offline ) :
		"""
		好友下线
		"""
		player = BigWorld.player()
		playmate = player.relationDatas.get( relationUID )
		if playmate is None : return
		relationStatus = playmate.relationStatus
		if not relationStatus & csdefine.ROLE_RELATION_FRIEND : return
		self.__onUpdateOLState( playmate.playerName, offline )

	def __onPlaymateLogon( self, relationUID, relationStatus ) :
		"""
		好友上线
		"""
		if not relationStatus & csdefine.ROLE_RELATION_FRIEND : return
		player = BigWorld.player()
		playmate = player.relationDatas.get( relationUID )
		if playmate is None : return
		self.__onUpdateObjInfo( playmate.playerName )

	def __onUpdateObjInfo( self, objName ) :
		"""
		更新玩家信息
		"""
		pyChatWnd = self.__pyWnds.get( objName )
		if pyChatWnd is None : return						# 没有和该玩家聊天
		objInfo = self.__getObjInfo( objName )
		pyChatWnd.updateChatObj( objInfo )

	def __onUpdateOLState( self, objName, online ) :
		"""
		更新在线状态
		"""
		pyChatWnd = self.__pyWnds.get( objName )
		if pyChatWnd is None : return						# 没有和该玩家聊天
		pyChatWnd.updateObjOnlineState( online )

	def __onPlaymateRemove( self, relationUID, relationStatus ) :
		"""
		移除好友
		"""
		if not relationStatus & csdefine.ROLE_RELATION_FRIEND : return
		player = BigWorld.player()
		playmate = player.relationDatas.get( relationUID )
		if playmate is None : return
		objName = playmate.playerName
		self.__extractNewMsg( objName )
		plmLogBrowser.removeChatLog( objName )

	def __getObjInfo( self, objName ) :
		"""
		根据名字获取聊天对象的信息
		"""
		player = BigWorld.player()
		friend = player.friends.get( objName )
		online = False
		raceClass = 0
		headTexture = ""
		if friend is not None :
			online = friend.online
			raceClass = friend.raceClass
			headTexture = friend.headTexture
			if not headTexture :
				headTexture = BigWorld.player().getHeadTexture()
		return ( objName, online, raceClass, headTexture )

	# -------------------------------------------------
	def __onEnterWorld( self, role ) :
		"""
		进入游戏时调用
		"""
		if role != BigWorld.player() : return
		if self.__pyNotifier is None :
			self.__pyNotifier = PLMNotifier()			# 新消息提示器
			self.__pyNotifier.onLClick.bind( self.__onNotifierClick )
		if not self.__allMsgRead() :
			self.__notifyNewMsg()
		ECenter.unregisterEvent( "EVT_ON_ROLE_ENTER_WORLD", self )
		del self.__triggers[ "EVT_ON_ROLE_ENTER_WORLD" ]

	def __onLeaveWorld( self, role ) :
		"""
		离开游戏后调用
		"""
		if role != BigWorld.player() : return
		self.__pyWnds = {}
		self.__newMsgs = {}
		plmLogBrowser.clearMsgs()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onReadNewMsg( self, spkName ) :
		"""
		玩家读取新消息
		@param		spkName	: 聊天对象的名称
		@type		spkName	: string
		"""
		msgs = self.__extractNewMsg( spkName )
		if len( msgs ) == 0 : return					# 没有消息记录
		pyChatWnd = self.__pyWnds.get( spkName )
		if pyChatWnd is None :							# 如果没有对话框，则创建一个
			objInfo = self.__getObjInfo( spkName )
			pyChatWnd = self.__createChatWindow( spkName )
			pyChatWnd.updateChatObj( objInfo )
		pyChatWnd.onReceiveMessages( msgs )
		if self.__allMsgRead() :						# 如果消息都已读取
			self.__pyNotifier.hide()					# 则隐藏提示器

	def onOriginateChat( self, objName ) :
		"""
		发起聊天
		"""
		pyChatWnd = self.__pyWnds.get( objName )
		if pyChatWnd is None :							# 如果没有对话框，则创建一个
			objInfo = self.__getObjInfo( objName )
			pyChatWnd = self.__createChatWindow( objName )
			pyChatWnd.updateChatObj( objInfo )
		msgs = self.__extractNewMsg( objName )
		pyChatWnd.onReceiveMessages( msgs )
		rds.ruisMgr.activeRoot( pyChatWnd )				# 激活窗口
		if self.__allMsgRead() :						# 如果消息都已读取
			self.__pyNotifier.hide()					# 则隐藏提示器

	def onBrowseChatLog( self, objName, pyOnwer = None ) :
		"""
		查看消息记录
		@param		objName	: 聊天对象的名称
		@type		objName	: string
		@param		pyOnwer		: 消息记录窗口的父窗口
		@type		pyOnwer		: instance of UIScript
		"""
		plmLogBrowser.showChatLogs( objName, pyOnwer )
		self.onReadNewMsg( objName )					# 如果有未查看的新消息，则弹出消息窗口

	def onUpdateChatObj( self, objInfo ) :
		"""
		更新聊天对象的状态
		"""
		objName = objInfo[0]
		pyChatWnd = self.__pyWnds.get( objName )
		if pyChatWnd is None : return					# 如果没有对话框，则创建一个
		pyChatWnd.updateChatObj( objInfo )

	def onEvent( self, evtMacro, *args ) :
		self.__triggers[evtMacro]( *args )


plmChatMgr = PLMChatMgr()