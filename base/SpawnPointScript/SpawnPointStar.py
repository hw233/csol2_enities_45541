# -*- coding: gb18030 -*-
from SpawnPoint import SpawnPoint

class SpawnPointStar( SpawnPoint ):
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
		entityParams[ "connectQuestID" ] = params[ "questID" ].asInt
		return entityParams