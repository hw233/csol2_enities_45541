# -*- coding: gb18030 -*-
import time
import uuid
import random

import BigWorld
import csdefine
import csstatus
import csconst
from bwdebug import *

# 最多可进人数
SPACE_CHALLENGE_ENTER_MAX = 3
# 挑战的关数
CHALLENGE_SPACE_MAX = 140

SPACE_GATE_PI_SHAN = csconst.HUA_SHAN_PI_SHAN_GATE # 劈山副本所在的层
# 副本时间
TIME_SPACE_LIVING = 1 * 60 * 60
TIME_CLOSE_SPACE = 1 * 60

class ChallengeItem( object ):
	def __init__( self, cmgr, playerEntitys, minLevel, enterNum ):
		self.cmgr = cmgr
		self.playerEntitys = playerEntitys
		self.challengeKey = self._getChallengeUUID()
		self.currentGate = minLevel - 4
		self.enterNum = enterNum
		self.isPiShanNpc = False # 劈山副本进入NPC是否已经刷出
		self.isEnterPiShan = False # 是否进入劈山副本
		self.isEnterBaoXiang = False # 是否进入宝藏副本
		self.currentSpaceMailBox = None
		self.startTime = time.time()
		self.teamMailbox = None
		BigWorld.globalData[ "SCC_time_%s" % self.challengeKey ] = self.startTime
	
	def getChallengeKey( self ):
		return self.challengeKey
	
	def start( self ):
		# 开始挑战副本
		spaceInfo = self.cmgr.getSpaceInfo( self.currentGate )
		for playerMailBox in self.playerEntitys:
			playerMailBox.cell.challengeSpaceOnStart( self.challengeKey, self.currentGate, spaceInfo[0], spaceInfo[1], spaceInfo[2] )
	
	def registerSpaceIns( self, spaceMailBox ):
		# 注册挑战副本地图实例
		if self.currentSpaceMailBox:
			self.currentSpaceMailBox.mgrDestroySelf()
			
		self.currentSpaceMailBox = spaceMailBox
	
	def enterGate( self, enterGate ):
		# 进入
		spaceInfo = self.cmgr.getSpaceInfo( enterGate )
		if spaceInfo == None:
			self.endChallenge()
			return
		
		for e in self.playerEntitys:
			e.cell.challengeSpaceGotoGate( enterGate, spaceInfo[0], spaceInfo[1], spaceInfo[2] )
		
	def levelGate( self, levelGate ):
		# 离开当前关
		pass
	
	def endChallenge( self ):
		# 挑战结束
		self.noticeClose()
		self.cmgr.destroyChallenge( self.challengeKey )
		
	def noticeClose( self ):
		# 通知玩家挑战结束
		for player in self.playerEntitys:
			player.client.onStatusMessage( csstatus.CHALLENGE_CLOSE_NOTICE, "" )
	
	def onDestroyChallenge( self ):
		# 副本将销毁
		# 清理玩家出副本
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
		# 通过副本销毁自身
		self.currentSpaceMailBox.mgrDestroySelf()
			
	def passGateDoor( self ):
		# 通过传送门
		self.levelGate( self.currentGate )
		self.currentGate += 1
		self.enterGate( self.currentGate )
	
	def reEnter( self, playerMailBox ):
		# 重新进入副本
		reGate = self.currentGate
		if self.isEnterPiShan:
			reGate = SPACE_GATE_PI_SHAN
			
		spaceInfo = self.cmgr.getSpaceInfo( reGate )
		playerMailBox.cell.challengeSpaceGotoGate( reGate, spaceInfo[0], spaceInfo[1], spaceInfo[2] )
		self.registerPlayer( playerMailBox )
	
	def newJoin( self, playerMailBox ):
		# 新加入成员
		reGate = self.currentGate
		if self.isEnterPiShan:
			reGate = SPACE_GATE_PI_SHAN
			
		spaceInfo = self.cmgr.getSpaceInfo( reGate )
		playerMailBox.cell.challengeSpaceOnStart( self.challengeKey, reGate, spaceInfo[0], spaceInfo[1], spaceInfo[2] )
		self.registerPlayer( playerMailBox )
	
	def playerLeave( self, playerMailBox ):
		# 玩家离开副本
		self.deletedPlayer( playerMailBox )
		playerMailBox.cell.challengeSpaceOnEnd()
	
	def playerTempLeave( self, playerMailBox, challengeGate ):
		# 玩家暂时离开副本
		if self.currentGate == challengeGate and not self.isEnterPiShan and not self.isEnterBaoXiang: # 如果离开的层数不等于当前的层数，那就是通过传送，可以不管
			self.deletedPlayer( playerMailBox )
	
	def backSpace( self ):
		# 集合返回副本，提供从宝藏/劈山副本的返回
		self.isEnterPiShan = False
		self.isEnterBaoXiang = False
		self.enterGate( self.currentGate )
	
	def enterPiShan( self ):
		# 进入劈山副本
		self.isEnterPiShan = True
		self.enterGate( SPACE_GATE_PI_SHAN )
		for player in self.playerEntitys:
			player.cell.challengeSpaceEnterPiShan()
	
	def levelPiShan( self ):
		# 离开劈山副本
		self.isEnterPiShan = False		
		self.cmgr.onDestroyChallenge( self.challengeKey )
	
	def enterBaoXiang( self ):
		# 进入宝藏副本
		self.isEnterBaoXiang = True
		for player in self.playerEntitys:
			player.cell.challengeSpaceEnterBaoXiang()
	
	def callPiShanEnterNpc( self ):
		# 劈山副本NPC可以刷出
		if not self.isPiShanNpc:
			self.isPiShanNpc = True
			BigWorld.globalData[ "SCC_piShanNPC_%s" % self.challengeKey ] = self.currentGate
	
	def playerDisconnected( self, playerMailBox ):
		# 玩家掉线
		self.deletedPlayer( playerMailBox )
	
	def playerConnected( self, playerMailBox ):
		# 玩家上线
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
		# 检查是否可进入
		if len( self.playerEntitys ) < SPACE_CHALLENGE_ENTER_MAX:
			return True
			
		if playerMailBox.id in [ mb.id for mb in self.playerEntitys ]:
			return True
			
		return False
	
	def getEnterNum( self ):
		return self.enterNum
	
	def _getChallengeUUID( self ):
		# 获取一下唯一识别码
		return str( uuid.uuid1() )

class SpaceChallengeMgr( BigWorld.Base ):
	def __init__( self ):
		BigWorld.Base.__init__( self )
		self.registerGlobally( "SpaceChallengeMgr", self._onRegisterManager )
		# 当前开启的副本情况 {playerID:ChallengeItem, ...}
		self._challengeDict = {}
		# 挑战副本地图 {cno:(spaceKey, enterPosition, enterDirection), ...}
		self._spaceInfo = {}
		# 销毁列表
		self._destroyDict = {}
		self.initSpaceInfo()
		self.playerDbidToItem = {}
	
	def initSpaceInfo( self ):
		# 初始化地图信息
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
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register SpaceChallengeMgr Fail!" )
			self.registerGlobally( "SpaceChallengeMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["SpaceChallengeMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("SpaceChallengeMgr Create Complete!")
	
	def registerSpaceInfo( self, spaceChNos, spaceKey, enterPosition, enterDirection ):
		"""
		把小地图信息注册到列表
		@spaceChNo	挑战副本地图编号
		@spaceKey	地图key
		@enterPosition	传入点
		@enterDirection	传入面向
		"""
		for spaceChNo in spaceChNos:
			self._spaceInfo[ spaceChNo ] = ( spaceKey, enterPosition, enterDirection )
				
	def registerSpaceIns( self, challengeKey, spaceMailBox ):
		# define method
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].registerSpaceIns( spaceMailBox )
		
	def onRequestChallengeTeam( self, playerEntitys, dbidList, minLevel, teamMailbox ):
		# define method
		#申请进入挑战副本,队伍
		cItem = ChallengeItem( self, playerEntitys, minLevel, 3 )
		self._challengeDict[ cItem.getChallengeKey() ] = cItem
		cItem.teamMailbox = teamMailbox
		cItem.start()
		for dbid in dbidList:
			self.playerDbidToItem[ dbid ] = cItem
		# 添加副本销毁timer
		timerID = self.addTimer( TIME_SPACE_LIVING )
		self._destroyDict[ timerID ] = cItem.getChallengeKey()
		BigWorld.globalData[ "spaceChallengeTeam_%d"%teamMailbox.id ] = cItem.getChallengeKey()
	
	def onRequestChallenge( self, playerEntity, dbid, minLevel ):
		# 申请进入挑战副本，单人
		cItem = ChallengeItem( self, [playerEntity,], minLevel, 1 )
		self._challengeDict[ cItem.getChallengeKey() ] = cItem
		cItem.start()
		self.playerDbidToItem[ dbid ] = cItem
		timerID = self.addTimer( TIME_SPACE_LIVING )
		self._destroyDict[ timerID ] = cItem.getChallengeKey()
	
	def playerRequestEnter( self, domainBase, position, direction, baseMailbox, params ):
		# define method
		# 玩家进入副本，请求数据
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
		# 玩家请求进入挑战副本
		dbid = params[ "dbID" ]
		if self.playerDbidToItem.has_key( dbid ):
			challengeItem = self.playerDbidToItem[ dbid ]
			if challengeItem.getEnterNum() == 3: #当前是三人副本
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
			# 清理掉相关定时器
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
		# 通关
		if challengeKey in self._challengeDict:
			self._challengeDict[ challengeKey ].passGateDoor()
	
	def reEnter( self, challengeKey, playerMaiBox ):
		# define method
		# 回到挑战副本
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].reEnter( playerMaiBox )
		else:
			playerMaiBox.cell.challengeSpaceIsTimeOut()
	
	def newJoin( self, challengeKey, playerMaiBox, dbid ):
		# define method.
		# 新加入成员
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].newJoin( playerMaiBox )
			self.playerDbidToItem[ dbid ] = self._challengeDict[ challengeKey ]
		else:
			playerMaiBox.cell.challengeSpaceIsTimeOut()
	
	def newJoinRequestEnter( self, challengeKey, playerMailbox ):
		# define method.
		# 新加入替补成员，要求进入
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
		# 玩家请求离开( 包括退队 )
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].playerLeave( playerMaiBox )
	
	def playerTempLeave( self, challengeKey, playerMaiBox, challengeGate ):
		# define method
		# 玩家暂时的离开副本
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].playerTempLeave( playerMaiBox, challengeGate )
	
	def enterPiShan( self, challengeKey ):
		# define method
		# 进入劈山副本
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].enterPiShan()
	
	def levelPiShan( self, challengeKey ):
		# define method
		# 离开劈山副本
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].levelPiShan()
			
	def enterBaoXiang( self, challengeKey ):
		# define method
		# 进入宝藏副本
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].enterBaoXiang()
	
	def callPiShanEnterNpc( self, challengeKey ):
		# define method
		# 通知沉香可以刷出
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].callPiShanEnterNpc()
	
	def endChallenge( self, challengeKey ):
		# define method
		# 副本结束
		if self._challengeDict.has_key( challengeKey ):
			self._challengeDict[ challengeKey ].endChallenge()
			
	def playerDisconnected( self, challengeKey, playerMailBox ):
		# 玩家掉线
		if challengeKey in self._challengeDict:
			self._challengeDict[ challengeKey ].playerDisconnected( playerMailBox )
	
	def playerConnected( self, challengeKey, playerMailBox ):
		# 玩家上线
		if challengeKey in self._challengeDict:
			self._challengeDict[ challengeKey ].playerConnected( playerMailBox )
		else:
			playerMailBox.cell.challengeSpaceOnEnd()
