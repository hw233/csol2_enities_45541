# -*- coding: gb18030 -*-

# �������촰�ڼ������¼������
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
		self.__pyWnds = {}								# �������촰��
		self.__newMsgs = {}								# δ����Ϣ��¼
		self.__pyNotifier = None						# ����Ϣ��ʾ��

		chid = csdefine.CHAT_CHANNEL_PLAYMATE			# ���������Ƶ��
		chatFacade.bindChannelHandler( chid, self.__onReceiveMessage )

		self.__triggers = {}
		self.__registerTriggers()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		"""
		ע���¼������롢�˳���Ϸ���������ߡ����ߣ������������
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
		�������һ�����ڵ���λ��
		"""
		screenSize = BigWorld.screenSize()
		firstPos = 254, 120								# ��һ�����ڵ�λ��
		skipPos = 10, 22								# ��һ�����ڵ�λ��ƫ��ֵ
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
		����һ���µ����촰��
		"""
		pyChatWnd = PLMChatWindow()
		pyChatWnd.onAfterClosed.bind( self.__onChatWndClosed )
		self.__pyWnds[ objName ] = pyChatWnd
		pyChatWnd.pos = self.__calcNextPos()
		pyChatWnd.show()
		return pyChatWnd

	def __onReceiveMessage( self, channel, spkID, spkName, msg, date = None ) :
		"""
		�յ�������Ϣ
		@param		channel	: ����Ƶ��
		@type		channel	: instance of Channel
		@param		spkID	: �����ߵ�ID
		@type		spkID	: INT64
		@param		spkName	: �����ߵ�����
		@type		spkName	: string
		@param		msg		: ��Ϣ����
		@type		msg		: string
		"""
		if date is None :
			date = time.strftime( "%H:%M:%S", Time.localtime() )	# ��ȡ������ʱ��
		pyChatWnd = self.__pyWnds.get( spkName )
		if pyChatWnd is None :
			self.__notifyNewMsg( channel, spkID, spkName, msg, date )
			self.__recordNewMsg( channel, spkID, spkName, msg, date )
		else :
			pyChatWnd.onReceiveMessage( channel, spkID, spkName, msg, date )
		self.__recordMsg( channel, spkID, spkName, msg, date )

	def __notifyNewMsg( self, channel, spkID, spkName, msg, date ) :
		"""
		֪ͨ����յ��µĺ�����Ϣ
		"""
		if self.__pyNotifier :
			self.__pyNotifier.notifyNewMsg()

	def __recordNewMsg( self, channel, spkID, spkName, msg, date ) :
		"""
		��¼�յ�������Ϣ
		"""
		msgs = self.__newMsgs.get( spkName )
		if msgs is None :
			msgs = [ ( channel.id, spkID, spkName, msg, date ) ]
			self.__newMsgs[ spkName ] = msgs
		else :
			msgs.append( ( channel.id, spkID, spkName, msg, date ) )

	def __recordMsg( self, channel, spkID, spkName, msg, date ) :
		"""
		��¼�����յ�����Ϣ
		"""
		plmLogBrowser.recordMsg( channel, spkID, spkName, msg, date )

	def __extractNewMsg( self, spkName ) :
		"""
		��ȡ����Ϣ������Ϣ�Ӽ�¼���Ƴ�
		"""
		msgs = self.__newMsgs.get( spkName )
		if msgs is None : return []
		del self.__newMsgs[ spkName ]
		return msgs

	def __allMsgRead( self ) :
		"""
		�Ƿ���������Ϣ�����Ķ�
		"""
		return len( self.__newMsgs ) == 0

	# -------------------------------------------------
	def __onChatWndClosed( self, pyChatWnd ) :
		"""
		���촰�ڹر�ʱ����
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
		��ҵ��
		"""
		for spkName in self.__newMsgs.iterkeys() :
			self.onReadNewMsg( spkName )
			break

	# -------------------------------------------------
	def __onPlaymateLogout( self, relationUID, offline ) :
		"""
		��������
		"""
		player = BigWorld.player()
		playmate = player.relationDatas.get( relationUID )
		if playmate is None : return
		relationStatus = playmate.relationStatus
		if not relationStatus & csdefine.ROLE_RELATION_FRIEND : return
		self.__onUpdateOLState( playmate.playerName, offline )

	def __onPlaymateLogon( self, relationUID, relationStatus ) :
		"""
		��������
		"""
		if not relationStatus & csdefine.ROLE_RELATION_FRIEND : return
		player = BigWorld.player()
		playmate = player.relationDatas.get( relationUID )
		if playmate is None : return
		self.__onUpdateObjInfo( playmate.playerName )

	def __onUpdateObjInfo( self, objName ) :
		"""
		���������Ϣ
		"""
		pyChatWnd = self.__pyWnds.get( objName )
		if pyChatWnd is None : return						# û�к͸��������
		objInfo = self.__getObjInfo( objName )
		pyChatWnd.updateChatObj( objInfo )

	def __onUpdateOLState( self, objName, online ) :
		"""
		��������״̬
		"""
		pyChatWnd = self.__pyWnds.get( objName )
		if pyChatWnd is None : return						# û�к͸��������
		pyChatWnd.updateObjOnlineState( online )

	def __onPlaymateRemove( self, relationUID, relationStatus ) :
		"""
		�Ƴ�����
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
		�������ֻ�ȡ����������Ϣ
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
		������Ϸʱ����
		"""
		if role != BigWorld.player() : return
		if self.__pyNotifier is None :
			self.__pyNotifier = PLMNotifier()			# ����Ϣ��ʾ��
			self.__pyNotifier.onLClick.bind( self.__onNotifierClick )
		if not self.__allMsgRead() :
			self.__notifyNewMsg()
		ECenter.unregisterEvent( "EVT_ON_ROLE_ENTER_WORLD", self )
		del self.__triggers[ "EVT_ON_ROLE_ENTER_WORLD" ]

	def __onLeaveWorld( self, role ) :
		"""
		�뿪��Ϸ�����
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
		��Ҷ�ȡ����Ϣ
		@param		spkName	: ������������
		@type		spkName	: string
		"""
		msgs = self.__extractNewMsg( spkName )
		if len( msgs ) == 0 : return					# û����Ϣ��¼
		pyChatWnd = self.__pyWnds.get( spkName )
		if pyChatWnd is None :							# ���û�жԻ����򴴽�һ��
			objInfo = self.__getObjInfo( spkName )
			pyChatWnd = self.__createChatWindow( spkName )
			pyChatWnd.updateChatObj( objInfo )
		pyChatWnd.onReceiveMessages( msgs )
		if self.__allMsgRead() :						# �����Ϣ���Ѷ�ȡ
			self.__pyNotifier.hide()					# ��������ʾ��

	def onOriginateChat( self, objName ) :
		"""
		��������
		"""
		pyChatWnd = self.__pyWnds.get( objName )
		if pyChatWnd is None :							# ���û�жԻ����򴴽�һ��
			objInfo = self.__getObjInfo( objName )
			pyChatWnd = self.__createChatWindow( objName )
			pyChatWnd.updateChatObj( objInfo )
		msgs = self.__extractNewMsg( objName )
		pyChatWnd.onReceiveMessages( msgs )
		rds.ruisMgr.activeRoot( pyChatWnd )				# �����
		if self.__allMsgRead() :						# �����Ϣ���Ѷ�ȡ
			self.__pyNotifier.hide()					# ��������ʾ��

	def onBrowseChatLog( self, objName, pyOnwer = None ) :
		"""
		�鿴��Ϣ��¼
		@param		objName	: ������������
		@type		objName	: string
		@param		pyOnwer		: ��Ϣ��¼���ڵĸ�����
		@type		pyOnwer		: instance of UIScript
		"""
		plmLogBrowser.showChatLogs( objName, pyOnwer )
		self.onReadNewMsg( objName )					# �����δ�鿴������Ϣ���򵯳���Ϣ����

	def onUpdateChatObj( self, objInfo ) :
		"""
		������������״̬
		"""
		objName = objInfo[0]
		pyChatWnd = self.__pyWnds.get( objName )
		if pyChatWnd is None : return					# ���û�жԻ����򴴽�һ��
		pyChatWnd.updateChatObj( objInfo )

	def onEvent( self, evtMacro, *args ) :
		self.__triggers[evtMacro]( *args )


plmChatMgr = PLMChatMgr()