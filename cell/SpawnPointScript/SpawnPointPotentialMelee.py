# -*- coding: gb18030 -*-
import copy
import random
import BigWorld
from SpawnPointCopy import SpawnPointCopy
from ObjectScripts.GameObjectFactory import g_objFactory
from Love3 import g_copyPotentialMeleeLoader

TIMER_ARG_SPAWN = 1000

class SpawnPointPotentialMelee( SpawnPointCopy ):
	# 潜能乱斗副本刷新点
	def initEntity( self, selfEntity ):
		SpawnPointCopy.initEntity( self, selfEntity )
		self.spawnDict = {}
		
	def createEntity( self, selfEntity, params = {} ):
		"""
		define method.
		通过刷新点刷出怪物
		"""
		batch =  params.pop( "batch" )
		proDict = self.getEntityArgs( selfEntity, params )
		spInfos = g_copyPotentialMeleeLoader[ batch ]
		for inf in spInfos:
			delayTimer = inf[ 3 ]
			if delayTimer == 0:
				self.onSpawn( selfEntity, inf, proDict )
			else:
				selfEntity.addTimer( delayTimer, 0, Const.SPAWN_ON_SERVER_START )
				selfEntity.setTemp( tid, ( inf, proDict ) )
	
	def onSpawn( self, selfEntity, inf, proDict ):
		className = inf[ 0 ]
		pos = inf[ 1 ]
		direction = inf[ 2 ]
		spCount = inf[ 4 ]
		posRandom = inf[ 5 ]
		pos += ( random.randint( - posRandom, posRandom ), 0, random.randint( - posRandom, posRandom ) )
		proDict[ "spawnPos" ] = pos
		for i in xrange( spCount ):
			g_objFactory.getObject( className ).createEntity( selfEntity.spaceID, pos, direction, copy.deepcopy( proDict ) )
	
	def onTimer( self, selfEntity, id, userArg ):
		if Const.SPAWN_ON_SERVER_START == userArg:
			if selfEntity.queryTemp( id ):
				inf, proDict = selfEntity.popTemp( id )
				self.onSpawn( selfEntity, inf, proDict )
				return
			
		SpawnPointCopy.onTimer( selfEntity, self, id, userArg )