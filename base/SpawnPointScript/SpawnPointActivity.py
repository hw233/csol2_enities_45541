# -*- coding: gb18030 -*-
from SpawnPoint import SpawnPoint

class SpawnPointActivity( SpawnPoint ):
	"""
	活动刷新点
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def getEntityType( self ):
		"""
		获取SpawnPoint 的 Entity Type
		retrun String
		"""
		return "SpawnPointActivity"