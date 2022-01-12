# -*- coding: gb18030 -*-
import BigWorld
from bwdebug import *
import csdefine
import csconst
import Const
from SpawnPoint import SpawnPoint
import random
from items import ItemDataList
g_items = ItemDataList.instance()

class SpawnPointDropItem( SpawnPoint ):
	"""
	根据与策划的沟通,怪物死亡时一次性复活,即第一个怪物死亡后开始计时,计时结束时后面有怪物死亡时一次性复活.
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity  )
		if len( self.itemNames ) == 0:
			spaceType = selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			ERROR_MSG( "space %s: spawn point entity name is Null." % spaceType, selfEntity.position )
			return
		selfEntity.rediviousTime = 10.0												#1分钟后重新刷

	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		selfEntity.currentRedivious += 1
		if not selfEntity.rediviousTimer:
			selfEntity.rediviousTimer = selfEntity.addTimer( selfEntity.rediviousTime, 0, Const.SPAWN_ON_MONSTER_DIED )
	
	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		获取要创建的entity参数
		"""
		args = SpawnPoint.getEntityArgs( selfEntity, params )
		
		entityNames = self.itemNames.split("|")
		entityName = entityNames[random.randint( 0, len(entityNames)-1 )]
		args[ "className" ] = entityName
		return args

	def onBaseGotCell( self, selfEntity ):
		"""
		由base回调回来，通知spawn point，base已经获得了cell的通知
		"""
		# 当base获得了onGetCell()回调后再开始怪物的增产生，以求能解决怪物出生时出生点不正确的问题
		# 当前该问题很可能是底层的bug
		self.createEntity( selfEntity )