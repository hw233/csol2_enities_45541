# -*- coding: gb18030 -*-
# 副本怪物出生点，死亡后在原地复活
import Const
from SpawnPointCopy import SpawnPointCopy

class SpawnPointCopyRevival( SpawnPointCopy ):
	"""
	副本怪物出生点，死亡后在原地复活
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPointCopy.initEntity( self, selfEntity )
		selfEntity.getCurrentSpaceBase().addSpawnPointCopy( selfEntity.base, selfEntity.entityName )
			
	def onTimer( self, selfEntity, controllerID, userData ):
		"""
		"""
		if userData == Const.SPAWN_ON_MONSTER_DIED:
			if not selfEntity.queryTemp( "canRevival", True ):
				return
				
			self.rediviousEntity( selfEntity, selfEntity.entityParams )
			return
		
		SpawnPointCopy.onTimer( self, selfEntity, controllerID, userData )

	def stopRevival( self, selfEntity, className ):
		"""
		define method
		"""
		if selfEntity.entityParams.get( "revivalEntityName", selfEntity.entityName ) == className:
			selfEntity.setTemp( "canRevival", False )
	