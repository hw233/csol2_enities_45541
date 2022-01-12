# -*- coding: gb18030 -*-

from SpawnPoint import SpawnPoint

class SpawnPointCityMaster( SpawnPoint ):
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
		entityParams[ "modelScale" ] = params["modelScale"].asFloat
		return entityParams