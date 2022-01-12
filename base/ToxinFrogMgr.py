# -*- coding: gb18030 -*-
#
# 千年毒蛙活动
#

from NormalActivityManager import NormalActivityManager
from bwdebug import *
import cschannel_msgs
import ShareTexts as ST
import csstatus
import csdefine
import Const
import random
import BigWorld
import Love3
import time


ADD_MONSTER = 1													#开始刷新怪物
ADD_DOOR = 2													#开始刷新门

class ToxinFrogMgr( BigWorld.Base, NormalActivityManager ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.noticeMsg 			= cschannel_msgs.BCT_QNDW_BEGIN_NOTIFY_0
		self.startMsg 			= cschannel_msgs.BCT_QNDW_BEGIN_NOTIFY
		self.endMgs 			= ""
		self.errorStartLog 		= cschannel_msgs.QIAN_NIAN_DU_WA_NOTICE_1
		self.errorEndLog 		= cschannel_msgs.QIAN_NIAN_DU_WA_NOTICE_2
		self.globalFlagKey		= "ToxinFrogStart"
		self.spawnMonsterCount  = 40
		self.oneSpaceMonsterCount = 8							#总共5个地图，每个地图产生8个怪物
		self.managerName 		= "ToxinFrogMgr"
		self.crondNoticeKey		= "ToxinFrogMgr_start_notice"
		self.crondStartKey		= "ToxinFrogMgr_start"
		self.crondEndKey		= "ToxinFrogMgr_end"
		self.playerMBToSpawnMBDict = {}
		self.doorSpawnPoints = {}
		self.currDoorSpawns = {}
		NormalActivityManager.__init__( self )
		
	def spawnMonster( self ):
		"""
		"""
		count = 0
		allSpawnCount = 0
		for iSpaceName in self.monsterSpawnPoints:
			allSpawnCount += len( self.monsterSpawnPoints[iSpaceName] )
		if allSpawnCount < self.spawnMonsterCount:
			self.spawnMonsterCount = allSpawnCount
		for iSpaceName in self.monsterSpawnPoints:
			spawns = self.monsterSpawnPoints[iSpaceName]
			if len( spawns ) == 0:
				continue
			if len( spawns ) <= self.oneSpaceMonsterCount:
				spawnPoint = spawns
			else:
				spawnPoint = random.sample( spawns, self.oneSpaceMonsterCount )
			for i in spawnPoint:
				if count > self.spawnMonsterCount:
					break
				if not self.currMonsterSpawns.has_key( iSpaceName ):
					self.currMonsterSpawns[iSpaceName] = []
				self.currMonsterSpawns[iSpaceName].append( i )
				i.cell.createEntityNormal()
				count += 1
			if count > self.spawnMonsterCount:
				break
							
	def addActivityMonsterSpawnPoint( self, spaceName, spawnPointMailBox, lineNum ):
		"""
		define method
		"""
		if not self.monsterSpawnPoints.has_key( spaceName ):
			self.monsterSpawnPoints[spaceName] = []

		self.monsterSpawnPoints[spaceName].append( spawnPointMailBox )
		
	def addActivityDoorSpawnPoint( self, spaceName, spawnPointMailBox ):
		"""
		define method
		"""
		if not self.doorSpawnPoints.has_key( spaceName ):
			self.doorSpawnPoints[ spaceName ] = []
			
		self.doorSpawnPoints[ spaceName ].append( spawnPointMailBox )
		
	def onNotifySpawnBoss( self, spawnMB, playerMB, level, camp ):
		"""
		define method
		"""
		playerID = playerMB.id
		if playerID in self.playerMBToSpawnMBDict:
			playerMB.client.onStatusMessage( csstatus.AN_YING_ZHI_MENG_PLAYER_IS_FIGHTING, "" )
		else:
			if BigWorld.globalData[ self.globalFlagKey ]:
				if camp == csdefine.ENTITY_CAMP_TAOISM:
					spawnMB.cell.remoteCallScript( "spawnAndDestroyMonster", [ playerMB, level, Const.AN_YING_ZHI_MENG_DEMON ] )
				elif camp == csdefine.ENTITY_CAMP_DEMON:
					spawnMB.cell.remoteCallScript( "spawnAndDestroyMonster", [ playerMB, level, Const.AN_YING_ZHI_MENG_TAOISM ] )
				self.playerMBToSpawnMBDict[ playerID ] = spawnMB.id
		
	def onBossExitFight( self, spawnMB ):
		"""
		define method
		"""
		t = None
		for i,j in self.playerMBToSpawnMBDict.iteritems():
			if j == spawnMB.id:
				t = i
		if t:
			self.playerMBToSpawnMBDict.pop( t )
		if BigWorld.globalData[ self.globalFlagKey ]:
			spawnMB.cell.createEntityNormal()
	
	def onBossDie( self, spawnMB ):
		"""
		define method
		"""
		t = None
		for i,j in self.playerMBToSpawnMBDict.iteritems():
			if j == spawnMB.id:
				t = i
		if t:
			self.playerMBToSpawnMBDict.pop( t )
		spaceName = ""
		spawnPoint = None
		for iSpaceName in self.currMonsterSpawns:
			spawnPoints = self.currMonsterSpawns[ iSpaceName ]
			for iSpawnPoint in spawnPoints:
				if spawnMB.id == iSpawnPoint.id:
					spaceName = iSpaceName
					spawnPoint = iSpawnPoint
		self.currMonsterSpawns[ spaceName ].remove( spawnPoint )
		if not self.currMonsterSpawns[ spaceName ]:
			self.currDoorSpawns[ spaceName ][ 0 ].cell.onActivityEnd()
		
	def onStart( self ):
		"""
		define method.
		活动开始
		"""
		if BigWorld.globalData.has_key( self.globalFlagKey ) and BigWorld.globalData[self.globalFlagKey] == True:
			curTime = time.localtime()
			ERROR_MSG( self.errorStartLog%(curTime[3],curTime[4] ) )
			return
		BigWorld.globalData[self.globalFlagKey] = True
		if self.startMsg != "":
			Love3.g_baseApp.anonymityBroadcast( self.startMsg, [] )
		self.addTimer( 0.1, 0, ADD_DOOR )
		self.addTimer( 5.1, 0, ADD_MONSTER )
		INFO_MSG( self.globalFlagKey, "start", "" )

	def onEnd( self ):
		"""
		define method.
		活动结束
		"""
		if not BigWorld.globalData.has_key( self.globalFlagKey ) or BigWorld.globalData[self.globalFlagKey] == False:
			curTime = time.localtime()
			ERROR_MSG( self.errorEndLog%(curTime[3],curTime[4] ) )
			return

		BigWorld.globalData[self.globalFlagKey] = False

		for i in self.currMonsterSpawns:
			for j in self.currMonsterSpawns[i]:
				j.cell.onActivityEnd()

		for iSpaceName in self.currDoorSpawns:
			for spawnMB in self.currDoorSpawns[ iSpaceName ]:
				spawnMB.cell.onActivityEnd()
				
		self.currMonsterSpawns = {}
		self.currDoorSpawns = {}
		if self.endMgs != "":
			Love3.g_baseApp.anonymityBroadcast( self.endMgs, [] )
		
		INFO_MSG( self.globalFlagKey, "end", "" )


	def onTimer( self, id, userArg ):
		"""
		"""
		if userArg == ADD_MONSTER:
			self.spawnMonster()
		elif userArg == ADD_DOOR:
			self.spawnDoor()
			
	def spawnDoor( self ):
		"""
		刷新一个门一样的entity
		"""
		for iSpaceName in self.doorSpawnPoints:
			spawnPointList = self.doorSpawnPoints[ iSpaceName ]
			if spawnPointList:
				spawnPoint = spawnPointList[0]
				if not self.currDoorSpawns.has_key( iSpaceName ):
					self.currDoorSpawns[ iSpaceName ] = []
				self.currDoorSpawns[ iSpaceName ].append( spawnPoint )
				spawnPoint.cell.createEntityNormal()
