# -*- coding: gb18030 -*-
from SpawnPointCopy import SpawnPointCopy

class SpawnPointCopyRabbitRun( SpawnPointCopy ):
	"""
	�����й������������
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopy.initEntity( self, selfEntity )
	
	def initTempParams( self, spaceEntity, params ):
		"""
		virtual method.
		��ʼ������
		"""
		tempMapping = {}
		tempMapping[ "entityType" ] =  params[ "entityType" ].asInt
		tempMapping[ "pointIndex" ] =  params[ "pointIndex" ].asInt
		tempMapping[ "pointsCount" ] = params[ "pointsCount" ].asInt
		tempMapping[ "endPoint" ] = params[ "endPoint" ].asInt
		return tempMapping
	
	def getEntityType( self ):
		"""
		��ȡSpawnPoint �� Entity Type
		retrun String
		"""
		return "SpawnPointTrap"