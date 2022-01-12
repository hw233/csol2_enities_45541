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
		��ʼ��һ�²���
		"""
		tempMapping = {}
		tempMapping[ "floorNum" ] = params[ "floorNum" ].asInt
		tempMapping[ "spawnTime" ] = ""
		if params.has_key( "monsterType" ):
			tempMapping[ "spawnTime" ] = params.readString( "spawnTime" )
			
		tempMapping[ "monsterType" ] = params[ "monsterType" ].asInt
		return tempMapping