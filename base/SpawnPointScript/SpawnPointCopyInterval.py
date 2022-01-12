# -*- coding: gb18030 -*-
"""
副本中怪物出生点
"""
from SpawnPoint import SpawnPoint

class SpawnPointCopyInterval( SpawnPoint ):
	"""
	副本中怪物出生点类型，间隔一定时间，出生一个怪物，直到足够数量
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def initTempParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化参数
		"""
		tempMapping = {}
		tempMapping[ "spawnNum" ] = params[ "spawnNum" ].asInt
		tempMapping[ "intervalTime" ] = params[ "intervalTime" ].asInt
		return tempMapping