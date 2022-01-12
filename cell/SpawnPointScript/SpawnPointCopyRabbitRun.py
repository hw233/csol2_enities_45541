# -*- coding: gb18030 -*-

import BigWorld
import csdefine
import csconst
import random
import time
from bwdebug import *
from SpawnPointCopy import SpawnPointCopy
from ObjectScripts.GameObjectFactory import g_objFactory

class SpawnPointCopyRabbitRun( SpawnPointCopy ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPointCopy.initEntity( self, selfEntity )
		if selfEntity.queryTemp( "entityType" ) == csconst.RABBIT_RUN_ENTITY_TYPE_ROAD_POINT:
			selfEntity.addProximityExt( csconst.RABBIT_RUN_POINT_TRAP_RANGE )
		else:
			tTime = BigWorld.globalData["AS_RabbitRun_Start_Time"] - int(time.time())			#距离活动开始时间
			rTime = random.randint( tTime + csconst.RABBIT_RUN_NPC_REVIDE_MIN_TIME, tTime + csconst.RABBIT_RUN_NPC_REVIDE_MAX_TIME )
			selfEntity.rediviousTimer = selfEntity.addTimer( rTime, 0, Const.SPAWN_ON_MONSTER_DIED )
		
		selfEntity.currentRedivious = 0

	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		selfEntity.currentRedivious += 1
		if selfEntity.currentRedivious < selfEntity.rediviousTotal:
			rTime = random.randint( csconst.RABBIT_RUN_NPC_REVIDE_MIN_TIME, csconst.RABBIT_RUN_NPC_REVIDE_MAX_TIME )
			selfEntity.rediviousTimer = selfEntity.addTimer( rTime, 0, Const.SPAWN_ON_MONSTER_DIED )

	def onEnterTrapExt( self, selfEntity, entity, range, controllerID ):
		"""
		"""
		if not entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			return
		
		pointIndex = selfEntity.queryTemp( "pointIndex" )
		pointsCount = selfEntity.queryTemp( "pointsCount" )
		endPoint = selfEntity.queryTemp( "endPoint" )
		entity.onEnterRabbitRunRoadPoint( pointIndex, pointsCount, endPoint )
		
