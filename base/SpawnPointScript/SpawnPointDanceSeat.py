# -*- coding: gb18030 -*-

from SpawnPoint import SpawnPoint

class SpawnPointDanceSeat( SpawnPoint ):
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
		entityParams[ "locationIndex" ] = params[ "locationIndex" ].asInt
		return entityParams