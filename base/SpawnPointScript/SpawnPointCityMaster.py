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
		��ʼ��һ�²���
		"""
		entityParams = {}
		entityParams[ "modelScale" ] = params["modelScale"].asFloat
		return entityParams