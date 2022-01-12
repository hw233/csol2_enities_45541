# -*- coding: gb18030 -*-

from SpawnPointCopy import SpawnPointCopy

class SpawnPointCopyDragon( SpawnPointCopy ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPointCopy.initEntity( self, selfEntity )
		monsterType = selfEntity.queryTemp( "monsterType" ,0 )
		selfEntity.getCurrentSpaceBase().addSpawnPointCopyDragon( selfEntity.base, monsterType )	
	
	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		if selfEntity.getCurrentSpaceBase():
			selfEntity.getCurrentSpaceBase().cell.onConditionChange( {} )