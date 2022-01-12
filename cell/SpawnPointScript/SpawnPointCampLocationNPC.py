# -*- coding: gb18030 -*-

# CSOL-1774 add by cwl

import BigWorld
import Const
import csconst
from SpawnPoint import SpawnPoint
from ObjectScripts.GameObjectFactory import g_objFactory
from bwdebug import *

TIMER_ARG_SPAWN_TIMER = 10001

class SpawnPointCampLocationNPC( SpawnPoint ):
	"""
	阵营据点NPC刷新点: 据点被占领需要转换成对方阵营的NPC
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity  )
		if selfEntity.isCount:
			BigWorld.globalData["CampMgr"].addLocationSpawnPoint( selfEntity.camp, selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), selfEntity.entityName, selfEntity.base, selfEntity.getCurrentSpaceBase(), selfEntity.rediviousTotal )
	
	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		获取刷出entity的参数
		"""	
		args = SpawnPoint.getEntityArgs( self, selfEntity, params )
		
		levelRange = [ int( i ) for i in selfEntity.level.split(";") ]
		if len( levelRange ) >= 2:
			args["level"] = random.randint( levelRange[0], levelRange[1] )
		elif len( levelRange ) == 1:
			args["level"] = levelRange[0]
		
		args[ "camp" ] = selfEntity.camp
		args[ "className" ] = self.getSpawnClassName( selfEntity )
		return args
		
	def createEntity( self, selfEntity, params = {} ):
		"""
		刷NPC
		"""
		if not self.checkActivity( selfEntity ):
			return
		
		entityName = self.getSpawnClassName( selfEntity )
		if not entityName:
			return
			
		SpawnPoint.createEntity( self, selfEntity, params )
		if selfEntity.spawnTime  > 0:
			selfEntity.spawnTimer = selfEntity.addTimer( 1.0, selfEntity.spawnTime , TIMER_ARG_SPAWN_TIMER )				# 间隔多久后再刷怪。 注：要么设置自动复活时间，要么设置间隔刷怪时间
	
	def rediviousEntity( self, selfEntity ):
		oldSpawnLen = len( selfEntity.spawnList )
		self.createEntity( selfEntity )
		newSpawnLen = len( selfEntity.spawnList )
		newSpawnNum = newSpawnLen - oldSpawnLen
		if not self.isOccued and self.isCount and newSpawnNum:
			BigWorld.globalData["CampMgr"].onLocationMonsterRedivious( self.camp, selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), selfEntity.entityName, newSpawnNum )
	
	def getSpawnClassName( self, selfEntity ):
		if selfEntity.isOccued:
			return self.enemyCampClassName
		else:
			return selfEntity.entityName
			
	def onLocationOccuped( self, selfEntity ):
		"""
		define method
		据点被攻占
		"""
		self.isOccued = True
		self.destroyMonster()
		self.rediviousMonster( selfEntity )
		self.recoverTimer = selfEntity.addTimer( 1 * 60 * 60, 0, 0 )			# 据点恢复timer
	
	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		if not self.isOccued and self.isCount:
			BigWorld.globalData["CampMgr"].onLocationMonsterDie( self.camp, selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), selfEntity.entityName )
		
		if selfEntity.rediviousTime < 0:
			return
		
		if selfEntity.rediviousTime > 0 or selfEntity.spawnTime  > 0:
			selfEntity.currentRedivious += 1
		
		if not selfEntity.rediviousTimer:
			selfEntity.rediviousTimer = selfEntity.addTimer( selfEntity.rediviousTime, 0, Const.SPAWN_ON_MONSTER_DIED )
	
	def recoverLocation( self, selfEntity ):
		"""
		define method
		据点恢复
		"""
		if self.recoverTimer > 0:
			selfEntity.cancel( self.recoverTimer )
			self.recoverTimer = 0
			
		self.isOccued = False
		self.destroyMonster()
		self.createEntity( selfEntity )
	
	def checkActivity( self, selfEntity ):
		"""
		检查阵营活动地图和活动类型
		"""
		if selfEntity.activityTypes == "":
			return True
			
		if not BigWorld.globalData.has_key( "CampActivityCondition" ):		# 数据类型( [ spaceNames ], type )
			return False
		
		temp = BigWorld.globalData["CampActivityCondition"]
		if selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) not in temp[0]:
			return False
		
		activityTypeList = [ int( i ) for i in selfEntity.activityTypes.split( "," ) ]			# 此刷新点可能会被多个活动用到
		if temp[1] not in activityTypeList:
			return False
			
		return True

	def destroyMonster( self ):
		"""
		销毁NPC
		"""
		for eid in selfEntity.spawnList:
			monster = BigWorld.entities.get( eid, None )
			if monster:
				if hasattr( monster, "resetEnemyList" ):
					monster.resetEnemyList()
				monster.destroy()
				
	def onTimer( self, selfEntity, controllerID, userData ):
		"""
		"""
		if controllerID == selfEntity.recoverTimer:
			self.recoverLocation()
			
		if userData == Const.SPAWN_ON_MONSTER_DIED:
			selfEntity.rediviousTimer = 0
			self.rediviousEntity( selfEntity )
			
		elif userData == Const.SPAWN_ON_SERVER_START:
			self.createEntity( selfEntity )
			
		elif userData == TIMER_ARG_SPAWN_TIMER:
			if selfEntity.currentRedivious >= selfEntity.rediviousTotal:			# 被全歼了才刷下一批
				selfEntity.currentRedivious = 0
				self.rediviousMonster( selfEntity )