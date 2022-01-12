# -*- coding: gb18030 -*-

from SpawnPointCopy import SpawnPointCopy

class SpawnPointCopyYeWai( SpawnPointCopy ):
	"""
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopy.initEntity( self, selfEntity )
	
	def initTempParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化参数
		"""
		tempMapping = SpawnPointCopy.initTempParams( self, spaceEntity, params )
		if params.has_key( "monsterType" ):
			tempMapping[ "monsterType" ] = params[ "monsterType" ].asInt
		return tempMapping
	
	def getEntityType( self ):
		"""
		获取SpawnPoint 的 Entity Type
		retrun String
		"""
		return "SpawnPointCopy"