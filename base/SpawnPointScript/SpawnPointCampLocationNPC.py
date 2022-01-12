# -*- coding: gb18030 -*-
from SpawnPoint import SpawnPoint

class SpawnPointCampLocationNPC( SpawnPoint ):
	"""
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def getEntityType( self ):
		"""
		获取SpawnPoint 的 Entity Type
		retrun String
		"""
		return "SpawnPointCampLocationNPC"
