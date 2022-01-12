# -*- coding: gb18030 -*-

from SpawnPointCopy import SpawnPointCopy
from ObjectScripts.GameObjectFactory import GameObjectFactory

g_objFactory = GameObjectFactory.instance()

class SpawnPointCityWarFinal( SpawnPointCopy ):
	"""
	帮会夺城战决赛刷新点
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopy.initEntity( self, selfEntity )
		if hasattr( self, "cellData" ):
			selfEntity.monsterType = selfEntity.cellData["monsterType"]
	
	def initEntityParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化参数
		"""
		entityParams = {}
		entityParams[ "monsterType" ] = params[ "monsterType" ].asInt
		entityParams[ "integral" ] = params[ "integral" ].asInt
		return entityParams