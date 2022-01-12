# -*- coding: gb18030 -*-
import BigWorld
from SpawnPoint import SpawnPoint

class SpawnPointChallenge( SpawnPoint ):
	"""
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		if self.getCurrentSpaceBase() == None:
			return
		self.currentRedivious += 1
		monsterType = selfEntity.queryTemp( "monsterType" )
		self.getCurrentSpaceBase().cell.onConditionChange( {"monsterType" : monsterType, "redivious": 0 } )