# -*- coding: gb18030 -*-
from SpawnPoint import SpawnPoint

class SpawnPointCampLocationNPC( SpawnPoint ):
	"""
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def getEntityType( self ):
		"""
		��ȡSpawnPoint �� Entity Type
		retrun String
		"""
		return "SpawnPointCampLocationNPC"
