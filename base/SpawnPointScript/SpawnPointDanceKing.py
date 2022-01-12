# -*- coding: gb18030 -*-

from SpawnPoint import SpawnPoint

class SpawnPointDanceKing( SpawnPoint ):
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
		entityParams[ "modelScale" ] = params[ "modelScale" ].asFloat
		entityParams[ "locationIndex" ] = params[ "locationIndex" ].asInt
		return entityParams