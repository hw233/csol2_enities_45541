# -*- coding: gb18030 -*-

import BigWorld
import cschannel_msgs
import ShareTexts as ST

from NormalActivityManager import NormalActivityManager
import Love3


class MonsterActivityMgr( BigWorld.Base, NormalActivityManager ):
	# 兵临城下活动
	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.noticeMsg 			= cschannel_msgs.BCT_GWGC_MONSTER_ACTIVE_NOTIFY
		self.startMsg 			= ""
		self.endMgs 			= ""
		self.errorStartLog 		= cschannel_msgs.MONSTERACTIVITYMGR_NOTICE_1
		self.errorEndLog 		= cschannel_msgs.MONSTERACTIVITYMGR_NOTICE_2
		self.globalFlagKey		= "MonsterActivity"
		self.spawnMonsterCount  = 40
		self.managerName 		= "MonsterActivityManager"
		self.crondNoticeKey		= "MonsterActivityMgr_notice"
		self.crondStartKey		= "MonsterActivityMgr_start"
		self.crondEndKey		= "MonsterActivityMgr_end"
		NormalActivityManager.__init__( self )

		self.buffSpawnPoints = {}


	def onEnd( self ):
		"""
		define method.
		活动结束
		"""
		for i in self.currMonsterSpawns:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_GWGC_WAS_OCCUPIED % i, [] )
		NormalActivityManager.onEnd( self )


	def addActivityBuffSpawnPoint( self, spaceName, spawnPointMailBox ):
		"""
		define method
		"""
		if not self.buffSpawnPoints.has_key( spaceName ):
			self.buffSpawnPoints[spaceName] = []

		self.buffSpawnPoints[spaceName].append( spawnPointMailBox )

	def onMonsterDie( self, spaceName, spawnPointMailBox ):
		"""
		define method
		"""
		if not self.currMonsterSpawns.has_key( spaceName ):
			return
		for i in self.currMonsterSpawns[spaceName]:
			if i.id == spawnPointMailBox.id:
				self.currMonsterSpawns[spaceName].remove( i )
				break

		if len( self.currMonsterSpawns[spaceName] ) == 0:
			del self.currMonsterSpawns[spaceName]
			self.onAreaMonstersDie( spaceName )

	def onAreaMonstersDie( self, spaceName ):
		"""
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_GWGC_WON_OVER % spaceName, [] )
		if spaceName not in self.buffSpawnPoints:
			return
		for i in self.buffSpawnPoints[spaceName]:
			i.cell.remoteCallScript( "addAreaPlayerBuff", [] )