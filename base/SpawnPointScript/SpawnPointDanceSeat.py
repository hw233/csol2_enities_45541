# -*- coding: gb18030 -*-

from SpawnPoint import SpawnPoint

class SpawnPointDanceSeat( SpawnPoint ):
	"""
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def initEntityParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化一下参数
		"""
		entityParams = {}
		entityParams[ "locationIndex" ] = params[ "locationIndex" ].asInt
		return entityParams