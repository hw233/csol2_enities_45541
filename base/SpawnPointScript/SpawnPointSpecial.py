# -*- coding: gb18030 -*-
from SpawnPoint import SpawnPoint

class SpawnPointSpecial( SpawnPoint ):
	"""
	特别刷新点
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )	
	
		
	def getEntityType( self ):
		"""
		获取SpawnPoint 的 Entity Type
		retrun String
		"""
		return "SpawnPointActivity"