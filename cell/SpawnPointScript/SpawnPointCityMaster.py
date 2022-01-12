# -*- coding: gb18030 -*-
import random
import BigWorld
import ShareTexts as ST
from bwdebug import *
import csdefine
import csconst
from interface.GameObject import GameObject
from ObjectScripts.GameObjectFactory import g_objFactory

from TongCityWarFightInfos import MasterChiefData

from SpawnPoint import SpawnPoint

SPAWN_REGISTER_TONG_MGR = 100003

class SpawnPointCityMaster( SpawnPoint ):
	# 城主帮会帮主刷新点
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity  )
		selfEntity.addTimer( 2, 0, SPAWN_REGISTER_TONG_MGR )

	def registerTongMgr( self, selfEntity ):
		# 注册到帮会管理器
		if BigWorld.globalData.has_key( "TongManager" ):
			cityName = selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			BigWorld.globalData[ "TongManager" ].cityWarRegisterMasterSpawnPoint( cityName, selfEntity.base )
		else:
			selfEntity.addTimer( 2, 0, SPAWN_REGISTER_TONG_MGR )

	def createEntity( self, selfEntity, params = {} ):
		# define method
		pass

	def entityDead( self, selfEntity ):
		# define method
		pass

	def spawnNoMasterNpc( self, selfEntity ):
		d = {}
		d[ "spawnMB" ] = selfEntity.base
		d[ "spawnPos" ] = tuple( selfEntity.position )
		spawnEntity = selfEntity.queryTemp( "spawnEntity", None )
		if spawnEntity:
			spawnEntity.destroy()
			spawnEntity = None

		spawnEntity = g_objFactory.getObject( selfEntity.entityName ).createEntity( selfEntity.spaceID, selfEntity.position, selfEntity.direction, d )
		selfEntity.setTemp( "spawnEntity", spawnEntity )

	def spawnCityMaster( self, selfEntity, chiefData ):
		d = {}
		d[ "spawnMB" ] = selfEntity.base
		d[ "spawnPos" ] = tuple( selfEntity.position )
		d.update( selfEntity.entityParams )
		d.update( chiefData.getDictFromObj( chiefData ) )
		
		spawnEntity = selfEntity.queryTemp( "spawnEntity", None )
		if spawnEntity:
			spawnEntity.destroy()
			spawnEntity = None

		spawnEntity = BigWorld.createEntity( "NPCCityMaster", selfEntity.spaceID, selfEntity.position, selfEntity.direction, d )
		selfEntity.setTemp( "spawnEntity", spawnEntity )

	def onTimer( self, selfEntity, controllerID, userData ):
		if SPAWN_REGISTER_TONG_MGR == userData:
			self.registerTongMgr( selfEntity )

		SpawnPoint.onTimer( self, selfEntity, controllerID, userData )