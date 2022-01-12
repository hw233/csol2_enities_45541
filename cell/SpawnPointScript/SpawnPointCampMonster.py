# -*- coding: gb18030 -*-

# CSOL-1774,add by cwl

import BigWorld
import Const
import csconst
from SpawnPoint import SpawnPoint
from ObjectScripts.GameObjectFactory import g_objFactory

SPAWN_TIMER = 111

class SpawnPointCampMonster( SpawnPoint ):
	"""
	阵营活动刷新点
	
	1、由活动管理器开启刷怪和统一销毁怪物。注：只适用于怪物在刷新点附近的情况，否则活动结束怪物无法销毁。
	2、刷怪频率兼容死亡复活、定时检测复活。
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPoint.initEntity( self, selfEntity  )
		BigWorld.globalData["CampMgr"].addActivityMonsterSpawnPoint( selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), selfEntity.entityName, selfEntity.base, selfEntity.camp )
		
	def createEntity( self, selfEntity, dict ):
		"""
		define method
		开始刷怪
		"""
		if not self.checkActivity( selfEntity ):			# 如果不是阵营活动管理器指定的地图和活动类型，此刷新点不刷怪
			return
		selfEntity.setTemp( "activityStart", True )
		self.spawnAllMonster( selfEntity )
		
		if selfEntity.spawnTime  >= 0:
			selfEntity.spawnTimer = selfEntity.addTimer( 1, selfEntity.spawnTime , SPAWN_TIMER )				# 间隔多久后再刷怪。 注：要么设置自动复活时间，要么设置间隔刷怪时间
		
	def checkActivity( self, selfEntity ):
		"""
		检查阵营活动地图和活动类型
		"""
		if not BigWorld.globalData.has_key( "CampActivityCondition" ):		# 数据类型( [ spaceNames ], type )
			return False
		
		temp = BigWorld.globalData["CampActivityCondition"]
		if selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) not in temp[0]:
			return False
		
		activityTypeList = [ int( i ) for i in selfEntity.activityTypes.split( "," ) ]			# 此刷新点可能会被多个活动用到
		if temp[1] not in activityTypeList:
			return False
			
		return True
		
	def spawnAllMonster( self, selfEntity ):
		"""
		刷所有数量的怪
		@num : 刷怪数量
		"""
		position = tuple( selfEntity.position )

		d = { "spawnPos" : position, "spawnMB" : selfEntity.base, "randomWalkRange" : selfEntity.randomWalkRange }
		if selfEntity.level > 1:
			d["level"] = selfEntity.level
		if len( selfEntity.patrolPathNode ):
			d["patrolPathNode"] = selfEntity.patrolPathNode
			d["patrolList"] = selfEntity.patrolList
		
		idList = selfEntity.queryTemp( 'monsterIDs', [] )
		for i in xrange( selfEntity.rediviousTotal ):
			entity = g_objFactory.getObject( selfEntity.entityName ).createEntity( selfEntity.spaceID, position, selfEntity.direction, d )
			idList.append( entity.id )
		selfEntity.setTemp( 'monsterIDs', idList )
		
	def spawnDiedMonster( self, selfEntity ):
		"""
		刷已死亡数量的怪
		"""
		position = tuple( selfEntity.position )
		d = { "spawnPos" : position, "spawnMB" : selfEntity.base, "randomWalkRange" : selfEntity.randomWalkRange }
		if selfEntity.level > 1:
			d["level"] = selfEntity.level
		if len( selfEntity.patrolPathNode ):
			d["patrolPathNode"] = selfEntity.patrolPathNode
			d["patrolList"] = selfEntity.patrolList
		
		idList = selfEntity.queryTemp( 'monsterIDs', [] )
		for i in xrange( selfEntity.currentRedivious ):
			entity = g_objFactory.getObject( selfEntity.entityName ).createEntity( selfEntity.spaceID, position, selfEntity.direction, d )
			idList.append( entity.id )
		selfEntity.setTemp( 'monsterIDs', idList )
		
	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		if not selfEntity.queryTemp( "activityStart", False ):
			return
			
		if selfEntity.rediviousTime > 0 or selfEntity.spawnTime  > 0:
			selfEntity.currentRedivious += 1
		
		if selfEntity.rediviousTime > 0 and not selfEntity.rediviousTimer:
			selfEntity.rediviousTimer = selfEntity.addTimer( selfEntity.rediviousTime, 0, Const.SPAWN_ON_MONSTER_DIED )
			
	def onActivityEnd( self, selfEntity ):
		"""
		define method
		"""
		if not selfEntity.queryTemp( "activityStart", False ):		# 没开启刷怪
			return
		selfEntity.setTemp( "activityStart", False )
		idList = selfEntity.queryTemp( 'monsterIDs', [] )
		for id in idList:
			monster = BigWorld.entities.get( id, None )
			if monster:
				monster.resetEnemyList()
				monster.destroy()
		selfEntity.removeTemp( 'monsterIDs' )
		
		selfEntity.cancel( selfEntity.spawnTimer )
		selfEntity.spawnTimer = 0
		selfEntity.cancel( selfEntity.rediviousTimer )
		selfEntity.rediviousTimer = 0
		selfEntity.currentRedivious = 0
		
	def onTimer( self, selfEntity, controllerID, userData ):
		"""
		"""
		if userData == SPAWN_TIMER:
			if selfEntity.currentRedivious < selfEntity.rediviousTotal:			# 被全歼了才刷下一批
				return
			self.spawnAllMonster( selfEntity )
			
		elif userData == Const.SPAWN_ON_MONSTER_DIED:
			selfEntity.rediviousTimer = 0
			self.spawnDiedMonster( selfEntity )
		
		selfEntity.currentRedivious = 0
			
	def onBaseGotCell( self, selfEntity ):
		"""
		"""
		pass

