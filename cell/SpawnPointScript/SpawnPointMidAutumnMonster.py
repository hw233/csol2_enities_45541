# -*- coding: gb18030 -*-

import BigWorld
import csdefine
import csconst
import random
import Const
from bwdebug import *
from SpawnPointCopy import SpawnPointCopy
from ObjectScripts.GameObjectFactory import g_objFactory

class SpawnPointMidAutumnMonster( SpawnPointCopy ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPointCopy.initEntity( self, selfEntity )
		if BigWorld.globalData.has_key("Mid_Autumn_Monster"):
			self.createEntity( selfEntity )

	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		pass

	def createEntity( self, selfEntity, params = {} ):
		"""
		"""
		
		d = self.getEntityArgs( selfEntity, params )
		spaceEntity = BigWorld.entities.get( selfEntity.getCurrentSpaceBase().id )
		if not spaceEntity.isReal():
			selfEntity.addTimer( 10, 0, Const.SPAWN_ON_SERVER_START )		#中秋活动刷怪特殊处理。因为是副本，基本能保证都是realEntity
			return
		
		if hasattr( spaceEntity, "shuijing_level" ):
			d["level"] = spaceEntity.shuijing_level
		elif hasattr( spaceEntity, "teamLevel" ):
			d["level"] = spaceEntity.teamLevel
		elif "copyLevel" in spaceEntity.params:
			d["level"] = spaceEntity.params["copyLevel"]
		else:
			return
			
		entity = g_objFactory.getObject( selfEntity.entityName ).createEntity( selfEntity.spaceID, selfEntity.position, selfEntity.direction, d )


	def onTimer( self, selfEntity, controllerID, userData ):
		"""
		"""
		if userData == Const.SPAWN_ON_SERVER_START:
			self.createEntity( selfEntity )