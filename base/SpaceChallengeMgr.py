# -*- coding: gb18030 -*-
import time
import uuid
import random

import BigWorld
import csdefine
import csstatus
import csconst
from bwdebug import *

# ���ɽ�����
SPACE_CHALLENGE_ENTER_MAX = 3
# ��ս�Ĺ���
CHALLENGE_SPACE_MAX = 140

SPACE_GATE_PI_SHAN = csconst.HUA_SHAN_PI_SHAN_GATE # ��ɽ�������ڵĲ�
# ����ʱ��
TIME_SPACE_LIVING = 1 * 60 * 60
TIME_CLOSE_SPACE = 1 * 60

class ChallengeItem( object ):
	def __init__( self, cmgr, playerEntitys, minLevel, enterNum ):
		self.cmgr = cmgr
		self.playerEntitys = playerEntitys
		self.challengeKey = self._getChallengeUUID()
		self.currentGate = minLevel - 4
		self.enterNum = enterNum
		self.isPiShanNpc = False # ��ɽ��������NPC�Ƿ��Ѿ�ˢ��
		self.isEnterPiShan = False # �Ƿ������ɽ����
		self.isEnterBaoXiang = False # �Ƿ���뱦�ظ���
		self.currentSpaceMailBox = None
		self.startTime = time.time()
		self.teamMailbox = None
		BigWorld.globalData[ "SCC_time_%s" % self.challengeKey ] = self.startTime
	
	def getChallengeKey( self ):
		return self.challengeKey
	
	def start( self ):
		# ��ʼ��ս����
		spaceInfo = self.cmgr.getSpaceInfo( self.currentGate )
		for playerMailBox in self.playerEntitys:
			playerMailBox.cell.challengeSpaceOnStart( self.challengeKey, self.currentGate, spaceInfo[0], spaceInfo[1], spaceInfo[2] )
	
	def registerSpaceIns( self, spaceMailBox ):
		# ע����ս������ͼʵ��
		if self.currentSpaceMailBox:
			self.currentSpaceMailBox.mgrDestroySelf()
			
		self.currentSpaceMailBox = spaceMailBox
	
	def enterGate( self, enterGate ):
		# ����
		spaceInfo = self.cmgr.getSpaceInfo( enterGate )
		if spaceInfo == None:
			self.endChallenge()
			return
		
		for e in self.playerEntitys:
			e.cell.challengeSpaceGotoGate( enterGate, spaceInfo[0], spaceInfo[1], spaceInfo[2] )
		
	def levelGate( self, levelGate ):
		# �뿪��ǰ��
		pass
	
	def endChallenge( self ):
		# ��ս����
		self.noticeClose()
		self.cmgr.destroyChallenge( self.challengeKey )
		
	def noticeClose( self ):
		# ֪ͨ�����ս����
		for player in self.playerEntitys:
			player.client.onStatusMessage( csstatus.CHALLENGE_CLOSE_NOTICE, "" )
	
	def onDestroyChallenge( self ):
		# ����������
		# ������ҳ�����
		for player in self.playerEntitys:
			# notice role leave
			player.cell.challengeSpaceOnEnd()
		
		if BigWorld.globalData.has_key( "SCC_time_%s" % self.challengeKey ):
			del BigWorld.globalData[ "SCC_time_%s" % self.challengeKey ]
		
		if BigWorld.globalData.has_key( "SCC_piShanNPC_%s" % self.challengeKey ):
			del BigWorld.globalData[ "SCC_piShanNPC_%s" % self.challengeKey ]
		
		if self.teamMailbox and BigWorld.globalData.has_key( "spaceChallengeTeam_%d"%self.teamMailbox.id ):
			del BigWorld.globalData[ "spaceChallengeTeam_%d"%self.teamMailbox.id ]
		
		self.cmgr.clearDBIDInfos( self.challengeKey )
		# ͨ��������������
		self.currentSpaceMailBox.mgrDestroySelf()
			
	def passGateDoor( self ):
		# ͨ��������
		self.levelGate( self.currentGate )
		self.currentGate += 1
		self.enterGate( self.currentGate )
	
	def reEnter( self, playerMailBox ):
		# ���½��븱��
		reGate = self.currentGate
		if self.isEnterPiShan:
			reGate = SPACE_GATE_PI_SHAN
			
		spaceInfo = self.cmgr.getSpaceInfo( reGate )
		playerMailBox.cell.challengeSpaceGotoGate( reGate, spaceInfo[0], spaceInfo[1], spaceInfo[2] )
		self.registerPlayer( playerMailBox )
	
	def newJoin( self, playerMailBox ):
		# �¼����Ա
		reGate = self.currentGate
		if self.isEnterPiShan:
			reGate = SPACE_GATE_PI_SHAN
			
		spaceInfo = self.cmgr.getSpaceInfo( reGate )
		playerMailBox.cell.challengeSpaceOnStart( self.challengeKey, reGate, spaceInfo[0], spaceInfo[1], spaceInfo[2] )
		self.registerPlayer( playerMailBox )
	
	def playerLeave( self, playerMailBox ):
		# ����뿪����
		self.deletedPlayer( playerMailBox )
		playerMailBox.cell.challengeSpaceOnEnd()
	
	def playerTempLeave( self, playerMailBox, challengeGate ):
		# �����ʱ�뿪����
		if self.currentGate == challengeGate and not self.isEnterPiShan and not self.isEnterBaoXiang: # ����뿪�Ĳ��������ڵ�ǰ�Ĳ������Ǿ���ͨ�����ͣ����Բ���
			self.deletedPlayer( playerMailBox )
	
	def backSpace( self ):
		# ���Ϸ��ظ������ṩ�ӱ���/��ɽ�����ķ���
		self.isEnterPiShan = False
		self.isEnterBaoXiang = False
		self.enterGate( self.currentGate )
	
	def enterPiShan( self ):
		# ������ɽ����
		self.isEnterPiShan = True
		self.enterGate( SPACE_GATE_PI_SHAN )
		for player in self.playerEntitys:
			player.cell.challengeSpaceEnterPiShan()
	
	def levelPiShan( self ):
		# �뿪��ɽ����
		self.isEnterPiShan = False		
		self.cmgr.onDestroyChallenge( self.challengeKey )
	
	def enterBaoXiang( self ):
		# ���뱦�ظ���
		self.isEnterBaoXiang = True
		for player in self.playerEntitys:
			player.cell.challengeSpaceEnterBaoXiang()
	
	def callPiShanEnterNpc( self ):
		# ��ɽ����NPC����ˢ��
		if not self.isPiShanNpc:
			self.isPiShanNpc = True
			BigWorld.globalData[ "SCC_piShanNPC_%s" % self.challengeKey ] = self.currentGate
	
	def playerDisconnected( self, playerMailBox ):
		# ��ҵ���
		self.deletedPlayer( playerMailBox )
	
	def playerConnected( self, playerMailBox ):
		# �������
		self.registerPlayer( playerMailBox )
	
	def registerPlayer( self, playerMailBox ):
		if playerMailBox.id not in [ mb.id for mb in self.playerEntitys ]:
			self.playerEntitys.append( playerMailBox )
	
	def deletedPlayer( self, playerMailBox ):
		for index, mailbox in enumerate( self.playerEntitys ):
			if mailbox.id == playerMailBox.id:
				self.playerEntitys.pop( index )
				break
	
	def checkIsCanEnter( self, playerMailBox ):
		# ����Ƿ�ɽ���
		if len( self.playerEntitys ) < SPACE_CHALLENGE_ENTER_MAX:
			return True
			
		if playerMailBox.id in [ mb.id for mb in self.playerEntitys ]:
			return True
			
		return False
	
	def getEnterNum( self ):
		return self.enterNum
	
	def _getChallengeUUID( self ):
		# ��ȡһ��Ψһʶ����
		return str( uuid.uuid1() )

class SpaceChallengeMgr( BigWorld.Base ):
	def __init__( self ):
		BigWorld.Base.__init__( self )
		self.registerGlobally( "SpaceChallengeMgr", self._onRegisterManager )
		# ��ǰ�����ĸ������ {playerID:ChallengeItem, ...}
		self._challengeDict = {}
		# ��ս������ͼ {cno:(spaceKey, enterPosition, enterDirection), ...}
		self._spaceInfo = {}
		# �����б�
		self._destroyDict = {}
		self.initSpaceInfo()
		self.playerDbidToItem = {}
	
	def initSpaceInfo( self ):
		# ��ʼ����ͼ��Ϣ
		if BigWorld.globalData.has_key( "ChallengeSpaceTempList" ):
			ChallengeSpaceTempList = BigWorld.globalData[ "ChallengeSpaceTempList" ]
			for spaceInfo in ChallengeSpaceTempList:
				gateIDs = spaceInfo[0]
				for gate in gateIDs:
					self._spaceInfo[ gate ] = ( spaceInfo[1], spaceInfo[2], spaceInfo[3] )
				
			del BigWorld.globalData[ "ChallengeSpaceTempList" ]
		
	def getSpaceInfo( self, spaceChNo ):
		if self._spaceInfo.has_key( spaceChNo ):
			return self._spaceInfo[ spaceChNo ]
		else:
			return None
	
	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register SpaceChallengeMgr Fail!" )
			self.registerGlobally( "SpaceChallengeMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["SpaceChallengeMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("SpaceChallengeMgr Create Complete!")
	
	def registerSpaceInfo( self, spaceChNos, spaceKey, enterPosition, enterDirection ):
		"""
		��С��ͼ��Ϣע�ᵽ�б�
		@spaceChNo	��ս������ͼ���
		@spaceKey	��ͼkey
		@enterPosition	�����
		@enterDirection	��������
		"""
		for spaceChNo in spaceChNos:
			self._spaceInfo[ spaceChNo ] = ( spaceKey, enterPosition, enterDirection )
				
	def registerSpaceIns( self, challengeKey, spaceMailBox ):
		# define method
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].registerSpaceIns( spaceMailBox )
		
	def onRequestChallengeTeam( self, playerEntitys, dbidList, minLevel, teamMailbox ):
		# define method
		#���������ս����,����
		cItem = ChallengeItem( self, playerEntitys, minLevel, 3 )
		self._challengeDict[ cItem.getChallengeKey() ] = cItem
		cItem.teamMailbox = teamMailbox
		cItem.start()
		for dbid in dbidList:
			self.playerDbidToItem[ dbid ] = cItem
		# ��Ӹ�������timer
		timerID = self.addTimer( TIME_SPACE_LIVING )
		self._destroyDict[ timerID ] = cItem.getChallengeKey()
		BigWorld.globalData[ "spaceChallengeTeam_%d"%teamMailbox.id ] = cItem.getChallengeKey()
	
	def onRequestChallenge( self, playerEntity, dbid, minLevel ):
		# ���������ս����������
		cItem = ChallengeItem( self, [playerEntity,], minLevel, 1 )
		self._challengeDict[ cItem.getChallengeKey() ] = cItem
		cItem.start()
		self.playerDbidToItem[ dbid ] = cItem
		timerID = self.addTimer( TIME_SPACE_LIVING )
		self._destroyDict[ timerID ] = cItem.getChallengeKey()
	
	def playerRequestEnter( self, domainBase, position, direction, baseMailbox, params ):
		# define method
		# ��ҽ��븱������������
		spaceChallengeKey = params[ "spaceChallengeKey" ]
		if self._challengeDict.has_key( spaceChallengeKey ):
			cItem = self._challengeDict[ spaceChallengeKey ]
			params[ "spaceChallengeEnterNums" ] = cItem.getEnterNum()
			if not cItem.checkIsCanEnter( baseMailbox ):
				baseMailbox.client.onStatusMessage( csstatus.CHALLENGE_SPACE_MEMBER_FULL, "" )
				return
			
			cItem.registerPlayer( baseMailbox )
		else:
			ERROR_MSG( "can't find spaceChallengeKey:%s, player id: %d" %( spaceChallengeKey, params[ "dbID" ] ) )
			return
		
		domainBase.onChallengeSpaceEnter( position, direction, baseMailbox, params )
	
	def playerRequestLogin( self, domainBase, baseMailbox,  params ):
		# define method.
		# ������������ս����
		dbid = params[ "dbID" ]
		if self.playerDbidToItem.has_key( dbid ):
			challengeItem = self.playerDbidToItem[ dbid ]
			if challengeItem.getEnterNum() == 3: #��ǰ�����˸���
				baseMailbox.logonSpaceInSpaceCopy()
				baseMailbox.cell.challengeSpaceIsTimeOut()
				return
				
			challengeItem.playerConnected( baseMailbox )
			if not challengeItem.checkIsCanEnter( baseMailbox ):
				baseMailbox.logonSpaceInSpaceCopy()
				return
						
			spaceChallengeGate = challengeItem.currentGate
			spaceChallengeKey = challengeItem.getChallengeKey()
			spaceKey = "%s_%d"%( spaceChallengeKey, spaceChallengeGate )
			params["spaceKey"] = spaceKey
			
		domainBase.onChallengeSpaceLogin( baseMailbox, params )
	
	def destroyChallenge( self, challengeKey ):
		# define method
		timerID = self.addTimer( TIME_CLOSE_SPACE )
		self._destroyDict[ timerID ] = challengeKey
	
	def onDestroyChallenge( self, challengeKey ):
		if challengeKey in self._challengeDict:
			self._challengeDict[ challengeKey ].onDestroyChallenge()
			self._challengeDict.pop( challengeKey )
			# �������ض�ʱ��
			for tid, cid in self._destroyDict.iteritems():
				if cid == challengeKey:
					self.delTimer( tid )
	
	def clearDBIDInfos( self, challengeKey ):
		clearList = []
		for dbid, citem in self.playerDbidToItem.iteritems():
			if citem.getChallengeKey() == challengeKey:
				clearList.append( dbid )
		
		for dbid in clearList:
			self.playerDbidToItem.pop( dbid )
			
	def onTimer( self, id, userArg ):
		challengeKey = self._destroyDict[ id ]
		if challengeKey:
			self._destroyDict.pop( id )
			self.onDestroyChallenge( challengeKey )
	
	def passGateDoor( self, challengeKey ):
		# define method
		# ͨ��
		if challengeKey in self._challengeDict:
			self._challengeDict[ challengeKey ].passGateDoor()
	
	def reEnter( self, challengeKey, playerMaiBox ):
		# define method
		# �ص���ս����
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].reEnter( playerMaiBox )
		else:
			playerMaiBox.cell.challengeSpaceIsTimeOut()
	
	def newJoin( self, challengeKey, playerMaiBox, dbid ):
		# define method.
		# �¼����Ա
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].newJoin( playerMaiBox )
			self.playerDbidToItem[ dbid ] = self._challengeDict[ challengeKey ]
		else:
			playerMaiBox.cell.challengeSpaceIsTimeOut()
	
	def newJoinRequestEnter( self, challengeKey, playerMailbox ):
		# define method.
		# �¼����油��Ա��Ҫ�����
		if not self._challengeDict.has_key( challengeKey ):
			ERROR_MSG( "key : %s is error" % challengeKey )
			return
			
		cItem = self._challengeDict[ challengeKey ]
		if cItem.checkIsCanEnter( playerMailbox ):
			playerMailbox.client.challengeSpaceShow( csconst.SPACE_CHALLENGE_SHOW_TYPE_RESERVE )
		else:
			playerMailbox.client.onStatusMessage( csstatus.CHALLENGE_SPACE_MEMBER_FULL, "" )
	
	def playerLeave( self, challengeKey, playerMaiBox ):
		# define method
		# ��������뿪( �����˶� )
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].playerLeave( playerMaiBox )
	
	def playerTempLeave( self, challengeKey, playerMaiBox, challengeGate ):
		# define method
		# �����ʱ���뿪����
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].playerTempLeave( playerMaiBox, challengeGate )
	
	def enterPiShan( self, challengeKey ):
		# define method
		# ������ɽ����
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].enterPiShan()
	
	def levelPiShan( self, challengeKey ):
		# define method
		# �뿪��ɽ����
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].levelPiShan()
			
	def enterBaoXiang( self, challengeKey ):
		# define method
		# ���뱦�ظ���
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].enterBaoXiang()
	
	def callPiShanEnterNpc( self, challengeKey ):
		# define method
		# ֪ͨ�������ˢ��
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].callPiShanEnterNpc()
	
	def endChallenge( self, challengeKey ):
		# define method
		# ��������
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].endChallenge()
			
	def playerDisconnected( self, challengeKey, playerMailBox ):
		# ��ҵ���
		if challengeKey in self._challengeDict:
			self._challengeDict[ challengeKey ].playerDisconnected( playerMailBox )
	
	def playerConnected( self, challengeKey, playerMailBox ):
		# �������
		if challengeKey in self._challengeDict:
			self._challengeDict[ challengeKey ].playerConnected( playerMailBox )
		else:
			playerMailBox.cell.challengeSpaceOnEnd()
