# -*- coding: gb18030 -*-
import random
import csdefine
import csconst
from bwdebug import *

from SpawnPoint import SpawnPoint


SHUIJING_DIAOXIANG_ID = "20254010"			#第二关雕像ID
SHUIJING_DIAOXIANG_INTERVAL_TIME = 5.0		#第二关雕像刷新间隔
SPAWN_MONSTER					= 5555
GUANQIA							= "2"		#第二关

class SpawnPointShuijing( SpawnPoint ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPoint.initEntity( self, selfEntity )
		group = selfEntity.queryTemp( "group", 0 )
		checkpoints = selfEntity.queryTemp( "checkpoints", 0 )
		selfEntity.getCurrentSpaceBase().cell.addSpawnPoint( selfEntity.base, group, checkpoints )

	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		selfEntity.getCurrentSpaceBase().cell.onMonsterDie({"className":selfEntity.entityName})

	def onTimer( self, selfEntity, controllerID, userData ):
		"""
		"""
		if userData == SPAWN_MONSTER:
			self.spawnSpecialMonster( selfEntity )
		return

	def spawnSpecialMonster( self, selfEntity ):
		"""
		"""
		args = self.getEntityArgs( selfEntity )
		if selfEntity.queryTemp( "monsterLevel", 0 ):
			args['level'] = selfEntity.queryTemp( "monsterLevel", 0 )
			
		selfEntity.createNPCObject( selfEntity.entityName, selfEntity.position, selfEntity.direction, args )
	
	def createEntity( self, selfEntity, params = {} ):
		"""
		"""
		if selfEntity.entityName == SHUIJING_DIAOXIANG_ID:
			selfEntity.setTemp( "monsterLevel", params['level'] )
			selfEntity.addTimer( SHUIJING_DIAOXIANG_INTERVAL_TIME, 0, SPAWN_MONSTER )
			return
		
		args = self.getEntityArgs( selfEntity, params )

		selfEntity.createNPCObject( selfEntity.entityName, selfEntity.position, selfEntity.direction, args )

	def spawnThirdGroupMonster( self, selfEntity, level, checkpointsAndGroup, classNameList ):
		"""
		"""
		args = self.getEntityArgs( selfEntity )
		
		args['level'] = level
		if classNameList:
			for className in classNameList:
				pos = selfEntity.position
				pos = ( pos[0] + random.randint(-2,2), pos[1], pos[2] + random.randint(-2,2) )
				args["spawnPos"] = pos
				selfEntity.createNPCObject( className, pos, selfEntity.direction, args )
		else:
			selfEntity.createNPCObject( selfEntity.entityName, selfEntity.position, selfEntity.direction, args )

	def spawnBoss( self, selfEntity, level, checkpoints ):
		"""
		define method
		"""
		args = self.getEntityArgs( selfEntity )
		if level > csconst.ROLE_LEVEL_UPPER_LIMIT:
			args['level'] = csconst.ROLE_LEVEL_UPPER_LIMIT
		else:
			args['level'] = level
		
		selfEntity.createNPCObject( selfEntity.entityName, selfEntity.position, selfEntity.direction, args )
	
	def onBaseGotCell( self, selfEntity ):
		pass