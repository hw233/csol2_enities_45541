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
		��ʼ������
		"""
		tempMapping = SpawnPointCopy.initTempParams( self, spaceEntity, params )
		if params.has_key( "monsterType" ):
			tempMapping[ "monsterType" ] = params[ "monsterType" ].asInt
		return tempMapping
	
	def getEntityType( self ):
		"""
		��ȡSpawnPoint �� Entity Type
		retrun String
		"""
		return "SpawnPointCopy"