# -*- coding: gb18030 -*-
from SpawnPoint import SpawnPoint

class SpawnPointSpecial( SpawnPoint ):
	"""
	�ر�ˢ�µ�
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )	
	
		
	def getEntityType( self ):
		"""
		��ȡSpawnPoint �� Entity Type
		retrun String
		"""
		return "SpawnPointActivity"