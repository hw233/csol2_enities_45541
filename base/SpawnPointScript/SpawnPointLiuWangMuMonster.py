# -*- coding: gb18030 -*-
from SpawnPointNormalActivity import SpawnPointNormalActivity

class SpawnPointLiuWangMuMonster( SpawnPointNormalActivity ):
	"""
	"""
	def initEntity( self, selfEntity ):
		SpawnPointNormalActivity.initEntity( self, selfEntity )
	
	def initTempParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化一下参数
		"""
		tempMapping = {}
		tempMapping[ "floorNum" ] = params[ "floorNum" ].asInt
		tempMapping[ "spawnTime" ] = ""
		if params.has_key( "monsterType" ):
			tempMapping[ "spawnTime" ] = params.readString( "spawnTime" )
			
		tempMapping[ "monsterType" ] = params[ "monsterType" ].asInt
		return tempMapping