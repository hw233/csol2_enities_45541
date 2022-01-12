# -*- coding: gb18030 -*-
from SpawnPoint import SpawnPoint

class RandomSpawnPoint( SpawnPoint ):
	"""
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def initEntityParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化参数
		"""
		entityParams = {}
		if params[ "positions" ].asString:
			entityParams[ "positions" ] = eval( params[ "positions" ].asString )
		return entityParams