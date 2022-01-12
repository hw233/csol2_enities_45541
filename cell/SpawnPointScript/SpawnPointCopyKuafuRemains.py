# -*- coding: gb18030 -*-

import BigWorld
import csdefine
import csconst
import random
from bwdebug import *
from SpawnPointCopy import SpawnPointCopy
from ObjectScripts.GameObjectFactory import g_objFactory

class SpawnPointCopyKuafuRemains( SpawnPointCopy ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPointCopy.initEntity( self, selfEntity )
		newDict = {}
		newDict[ "spawnPoint" ] = selfEntity.base
		newDict[ "step" ] = selfEntity.queryTemp( "step", 0 )
		newDict[ "entityType" ] = selfEntity.queryTemp( "entityType", 0 )
		newDict[ "event" ] = selfEntity.queryTemp( "event", 0 )
		newDict[ "group" ] = selfEntity.queryTemp( "group", 0 )
		newDict[ "isSpawnOnStep" ] = selfEntity.queryTemp( "isSpawnOnStep", 0 )
		
		selfEntity.getCurrentSpaceBase().addSpawnPoint( newDict )
		selfEntity.entityName = random.choice( selfEntity.entityName.split("|") )

	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		spaceMB = selfEntity.getCurrentSpaceBase()
		if spaceMB is None:
			return
		
		newDict = {}
		newDict[ "className" ] = selfEntity.entityName
		newDict[ "entityType" ] = selfEntity.queryTemp( "entityType", 0 )
		newDict[ "step" ] = selfEntity.queryTemp( "step", 0 )
		newDict[ "group" ] = selfEntity.queryTemp( "group", 0 )
		spaceMB.cell.onMonsterDie( newDict )

	def wakeUpMonster( self ):
		"""
		define method
		唤醒该刷新点记录的怪物id对应的怪物，使其进入自由状态
		"""
		monster = BigWorld.entities.get( selfEntity.queryTemp( "monsterID", 0 ) )
		if monster is None:
			return
		
		if selfEntity.queryTemp( "entityType" ) == csconst.KUA_FU_ENTITY_TYPE_STONE:
			print "第%i组石像被摧毁。"%selfEntity.queryTemp( "group")
			return
		
		monster.remoteCall( "changeState", ( csdefine.ENTITY_STATE_FREE, ) )
		monster.remoteCall( "removeFlag", ( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED, ) )

	def openDoor( self, selfEntity ):
		"""
		"""
		door = BigWorld.entities.get( selfEntity.queryTemp( "monsterID", 0 ) )
		if door:
			if door.isOpen != True:
				door.isOpen = True

	def createEntity( self, selfEntity, params = {} ):
		"""
		"""
		args = self.getEntityArgs( selfEntity, params )
		if not selfEntity.queryTemp( "entityType") in [csconst.KUA_FU_ENTITY_TYPE_MONSTER, csconst.KUA_FU_ENTITY_TYPE_BOSS, csconst.KUA_FU_ENTITY_TYPE_STONE, csconst.KUA_FU_ENTITY_TYPE_SHITI ]:
			if "level" in params:
				del params["level"]
		
		entity = g_objFactory.getObject( selfEntity.entityName ).createEntity( selfEntity.spaceID, selfEntity.position, selfEntity.direction, args )
		
		if not selfEntity.queryTemp( "entityType") == csconst.KUA_FU_ENTITY_TYPE_DOOR:
			entity.viewRange = 100
			entity.territory = 200
			
		selfEntity.setTemp( "monsterID", entity.id )
		
		if selfEntity.queryTemp( "group" ) != 0:
			entity.remoteCall( "changeState", ( csdefine.ENTITY_STATE_ENVIRONMENT_OBJECT, ) )
				
			if selfEntity.queryTemp( "entityType") == csconst.KUA_FU_ENTITY_TYPE_MONSTER:
				entity.remoteCall( "addFlag", ( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED, ) )
		
		if selfEntity.queryTemp( "entityType") == csconst.KUA_FU_ENTITY_TYPE_SHITI:
			entity.remoteCall( "changeState", ( csdefine.ENTITY_STATE_ENVIRONMENT_OBJECT, ) )
			entity.remoteCall( "addFlag", ( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED, ) )
		
		if selfEntity.queryTemp( "entityType") == csconst.KUA_FU_ENTITY_TYPE_ICE:
			entity.remoteCall( "addFlag", ( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED, ) )

		if selfEntity.queryTemp( "entityType") == csconst.KUA_FU_ENTITY_TYPE_NPC and selfEntity.queryTemp( "step") == 2:
			entity.remoteCall( "addFlag", ( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED, ) )

		if selfEntity.queryTemp( "entityType") == csconst.KUA_FU_ENTITY_TYPE_TREE:
			entity.remoteCall( "changeState", ( csdefine.ENTITY_STATE_ENVIRONMENT_OBJECT, ) )
			entity.remoteCall( "addFlag", ( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED, ) )


	def playerAction( self, actionName ):
		"""
		define method
		"""
		entity = BigWorld.entities.get( selfEntity.queryTemp( "monsterID", 0 ) )
		if entity is None:
			return
		entity.planesAllClients( "onPlayAction", ( actionName, ) )
	
	def wakeUpDeadBody( self, selfEntity ):
		"""
		define method
		"""
		entity = BigWorld.entities.get( selfEntity.queryTemp( "monsterID", 0 ) )
		if entity is None:
			return
		
		entity.remoteCall( "changeState", ( csdefine.ENTITY_STATE_FREE, ) )
		entity.remoteCall( "removeFlag", ( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED, ) )
		entity.setNextRunAILevel(0)
		entity.planesAllClients( "onPlayAction", ( "", ) )
	
	
	def changeEntityAILevel( self, params ):
		"""
		更改所属entityAI等级
		"""
		entity = BigWorld.entities.get( selfEntity.queryTemp( "monsterID", 0 ) )
		if entity is None:
			return
		entity.setNextRunAILevel( params["aiLevel"] )
