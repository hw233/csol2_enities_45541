# -*- coding: gb18030 -*-
from SpawnPoint import SpawnPoint

class SpawnPointActivity( SpawnPoint ):
	"""
	�ˢ�µ�
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def getEntityType( self ):
		"""
		��ȡSpawnPoint �� Entity Type
		retrun String
		"""
		return "SpawnPointActivity"