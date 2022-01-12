# -*- coding: gb18030 -*-
"""
夸父神殿出生点
"""
from SpawnPointCopyYeWai import SpawnPointCopyYeWai

class SpawnPointCopyKuafuRemains( SpawnPointCopyYeWai ):
	"""
	副本中怪物出生点类型
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopyYeWai.initEntity( self, selfEntity )
	
	def initTempParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化一下参数
		"""
		tempMapping = {}
		tempMapping[ "entityType" ] = params[ "entityType" ].asInt
		tempMapping[ "step" ] = params[ "step" ].asInt
		tempMapping[ "group" ] = params[ "group" ].asInt
		tempMapping[ "event" ] = params[ "event" ].asInt
		tempMapping[ "isSpawnOnStep" ] = params[ "isSpawnOnStep" ].asInt
		return tempMapping