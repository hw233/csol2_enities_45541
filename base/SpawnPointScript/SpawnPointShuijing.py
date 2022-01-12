# -*- coding: gb18030 -*-
from SpawnPoint import SpawnPoint

class SpawnPointShuijing( SpawnPoint ):
	"""
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def initTempParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化参数
		"""
		tempMapping = {}
		tempMapping[ "group" ] = params[ "group" ].asInt
		tempMapping[ "checkpoints" ] = params[ "checkpoints" ].asInt
		return tempMapping