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
		��ʼ������
		"""
		entityParams = {}
		if params[ "positions" ].asString:
			entityParams[ "positions" ] = eval( params[ "positions" ].asString )
		return entityParams