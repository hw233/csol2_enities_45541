# -*- coding: gb18030 -*-

import random
import BigWorld
import ShareTexts as ST
from bwdebug import *
import csdefine
import csconst
from interface.GameObject import GameObject
from ObjectScripts.GameObjectFactory import g_objFactory

from SpawnPoint import SpawnPoint

SPAWN_DANCEMODEL_DANCEMGR = 1523

class SpawnPointDanceKing( SpawnPoint ):
	# 舞厅中1到19个模型刷新点
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity  )
		selfEntity.addTimer( 2, 0, SPAWN_DANCEMODEL_DANCEMGR )
		selfEntity.getCurrentSpaceBase().cell.registerDanceKingSpawnPoint(selfEntity.queryTemp( "locationIndex", 0 ), selfEntity.base)

	def registerDanceMgr( self, selfEntity ):
		# 注册到帮会管理器
		if BigWorld.globalData.has_key( "DanceMgr" ):
			BigWorld.globalData[ "DanceMgr" ].registerDanceModelSpawnPoint( selfEntity.queryTemp( "locationIndex", 0 ), selfEntity.base )
		else:
			selfEntity.addTimer( 2, 0, SPAWN_DANCEMODEL_DANCEMGR )

	def createEntity( self, selfEntity, params = {} ):
		# define method
		pass

	def entityDead( self, selfEntity ):
		# define method
		pass

	def spawnNoNpcDanceKing( self, selfEntity ):
		# define method
		spawnEntity = selfEntity.queryTemp( "spawnEntity" )
		if spawnEntity:
			spawnEntity.destroy()
			selfEntity.setTemp( "spawnEntity", None )
			
		INFO_MSG("spawnNoNpcDanceKing")

	def spawnNPCDanceKing( self, selfEntity,  danceKingData ):
		# define method
		args = self.getEntityArgs( selfEntity, danceKingData )
		
		spawnEntity = selfEntity.queryTemp( "spawnEntity" )
		if spawnEntity:
			spawnEntity.destroy()
			selfEntity.setTemp( "spawnEntity", None )

		spawnEntity = BigWorld.createEntity( "DanceKing", selfEntity.spaceID, selfEntity.position, selfEntity.direction, args )
		selfEntity.setTemp( "spawnEntity", spawnEntity )
		INFO_MSG("spawnNPCDanceKing and its' ID is %d"%self.spawnEntity.id)

	def onTimer( self, selfEntity, controllerID, userData ):
		if SPAWN_DANCEMODEL_DANCEMGR == userData:
			self.registerDanceMgr( selfEntity )

		SpawnPoint.onTimer( self, selfEntity, controllerID, userData )