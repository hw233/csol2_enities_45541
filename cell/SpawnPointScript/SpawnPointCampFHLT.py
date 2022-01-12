# -*- coding: gb18030 -*-
from SpawnPointCopy import SpawnPointCopy
import random
import csdefine
import csconst
from bwdebug import *

class SpawnPointCampFHLT( SpawnPointCopy ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPointCopy.initEntity( self, selfEntity )
		belongCamp = selfEntity.getEntityData( "belongCamp" )
		selfEntity.getCurrentSpaceBase().cell.addSpawnPoint( selfEntity.base, belongCamp )
		self.spaceBaseMB = selfEntity.getCurrentSpaceBase()

	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		#self.spaceBaseMB.cell.onMonsterDie({"className":selfEntity.entityName})
		return

	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		刷出怪物
		"""	
		args = SpawnPointCopy.getEntityArgs( self, selfEntity, params )
		args[ "ownCamp" ] = params[ "camp" ]
		return args