# -*- coding: gb18030 -*-


import BigWorld
import time
from bwdebug import *
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
import random
import Love3
ADD_MONSTER = 1													#开始刷新怪物



class NormalActivityManager:
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.monsterSpawnPoints = {}							#怪物刷新点 例如{ 'fengming': line1: [s1,s2,s3,...], ... }
		self.currMonsterSpawns	= {}							#当前有怪物的地图和对应怪物出生点ID
		#self.noticeMsg 		= ""
		#self.startMsg 			= ""
		#self.endMgs 			= ""
		#self.errorStartLog 	= ""
		#self.errorEndLog 		= ""
		#self.globalFlagKey		= ""
		#self.spawnMonsterCount = 0
		#self.managerName 		= ""
		#self.crondNoticeKey	= ""
		#self.crondStartKey		= ""
		#self.crondEndKey		= ""

		self.registerGlobally( self.managerName, self._onRegisterManager )

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register %s Fail!"%self.managerName )
			# again
			self.registerGlobally( self.managerName, self._onRegisterManager )
		else:
			BigWorld.globalData[self.managerName] = self		# 注册到所有的服务器中
			INFO_MSG("%s Create Complete!"%self.managerName)
			self.registerCrond()

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
					  	self.crondNoticeKey : "onStartNotice",
					  	self.crondStartKey : "onStart",
						self.crondEndKey :	"onEnd",
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )
		BigWorld.globalData["Crond"].addAutoStartScheme( self.crondStartKey, self, "onStart" )


	def onStartNotice( self ):
		"""
		define method.
		活动开始通知
		"""
		if self.noticeMsg != "":
			Love3.g_baseApp.anonymityBroadcast( self.noticeMsg, [] )
		
		INFO_MSG( self.globalFlagKey, "notice", "" )

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
		self.addTimer( 0.1, 0, ADD_MONSTER )
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

		self.currMonsterSpawns = {}
		if self.endMgs != "":
			Love3.g_baseApp.anonymityBroadcast( self.endMgs, [] )
		
		INFO_MSG( self.globalFlagKey, "end", "" )


	def onTimer( self, id, userArg ):
		"""
		"""
		if userArg == ADD_MONSTER:
			self.spawnMonster()


	def spawnMonster( self ):
		"""
		"""
		count = 0
		for i, spawnList in self.currMonsterSpawns.iteritems():
			count += len( spawnList )
			
		allSpawnCount = 0
		for iSpaceName in self.monsterSpawnPoints:
			for jLine in  self.monsterSpawnPoints[iSpaceName]:
				allSpawnCount += len( self.monsterSpawnPoints[iSpaceName][jLine] )
				
		if allSpawnCount < self.spawnMonsterCount:
			self.spawnMonsterCount = allSpawnCount
		
		if self.spawnMonsterCount == 0:
			WARNING_MSG( "MGR( %s ) monsterSpawnPoints is empty!!" % self.globalFlagKey )
			return
			
		while count < self.spawnMonsterCount:
			for iSpaceName in self.monsterSpawnPoints:
				for jLine in  self.monsterSpawnPoints[iSpaceName]:
					spawns = [ e for e in self.monsterSpawnPoints[iSpaceName][jLine] if e not in self.currMonsterSpawns.get( iSpaceName,[] ) ]
					if len( spawns ) == 0:
						continue
					spawnPoint = random.choice( spawns )
					if not self.currMonsterSpawns.has_key( iSpaceName ):
						self.currMonsterSpawns[iSpaceName] = []
					self.currMonsterSpawns[iSpaceName].append( spawnPoint )
					spawnPoint.cell.createEntityNormal()
					count += 1
					if count >= self.spawnMonsterCount:
						break
				if count >= self.spawnMonsterCount:
					break


	def addActivityMonsterSpawnPoint( self, spaceName, spawnPointMailBox, lineNum ):
		"""
		define method
		"""
		if not self.monsterSpawnPoints.has_key( spaceName ):
			self.monsterSpawnPoints[spaceName] = {}

		if not self.monsterSpawnPoints[spaceName].has_key( lineNum ):
			self.monsterSpawnPoints[spaceName][lineNum] = []

		self.monsterSpawnPoints[spaceName][lineNum].append( spawnPointMailBox )


	def onMonsterDie( self, spaceName, spawnPointMailBox ):
		"""
		define method
		"""
		pass
