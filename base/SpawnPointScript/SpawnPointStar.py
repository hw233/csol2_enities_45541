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
		��ʼ��һ�²���
		"""
		entityParams = {}
		entityParams[ "connectQuestID" ] = params[ "questID" ].asInt
		return entityParams