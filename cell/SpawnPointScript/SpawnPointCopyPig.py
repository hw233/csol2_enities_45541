# -*- coding: gb18030 -*-

from SpawnPointCopy import SpawnPointCopy

class SpawnPointCopyPig( SpawnPointCopy ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPointCopy.initEntity( self, selfEntity )
		selfEntity.getCurrentSpaceBase().addSpawnPointCopyPig( selfEntity.base, selfEntity.queryTemp( "monsterType" ) )	
	
	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		if selfEntity.getCurrentSpaceBase() == None:
			return
		if selfEntity.getCurrentSpaceBase():
			selfEntity.getCurrentSpaceBase().cell.onConditionChange( {} )