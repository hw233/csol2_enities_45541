# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from SpawnPoint import SpawnPoint

class SpawnPointScheme( SpawnPoint ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPoint.initEntity( self, selfEntity )
	
	def createEntity( self, params, spaceEntity, position, direction ):
		"""
		创建SpawnPoint Entity
		return Entity
		"""
		entity = SpawnPoint.createEntity( self, params, spaceEntity, position, direction )
		entity.activityKeyStart = params[ "activityKeyStart" ].asString
		entity.activityKeyEnd = params[ "activityKeyEnd" ].asString
		entity.getScript().registeToScheme( entity )
		return entity
		
	def registeToScheme( self, selfEntity ):
		"""
		define method
		注册到刷新点管理器
		"""
		if not selfEntity.activityKeyStart is None or selfEntity.activityKeyStart != "":
			BigWorld.globalBases["ActivityBroadcastMgr"].registeSpawnPoint( selfEntity.activityKeyStart, selfEntity )
		if not selfEntity.activityKeyEnd is None or selfEntity.activityKeyEnd != "":
			BigWorld.globalBases["ActivityBroadcastMgr"].registeSpawnPoint( selfEntity.activityKeyEnd, selfEntity )