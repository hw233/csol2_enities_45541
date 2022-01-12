# -*- coding: gb18030 -*-
from SpawnPointCopy import SpawnPointCopy

class SpawnPointCopyRabbitRun( SpawnPointCopy ):
	"""
	副本中怪物出生点类型
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopy.initEntity( self, selfEntity )
	
	def initTempParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化参数
		"""
		tempMapping = {}
		tempMapping[ "entityType" ] =  params[ "entityType" ].asInt
		tempMapping[ "pointIndex" ] =  params[ "pointIndex" ].asInt
		tempMapping[ "pointsCount" ] = params[ "pointsCount" ].asInt
		tempMapping[ "endPoint" ] = params[ "endPoint" ].asInt
		return tempMapping
	
	def getEntityType( self ):
		"""
		获取SpawnPoint 的 Entity Type
		retrun String
		"""
		return "SpawnPointTrap"