# -*- coding: gb18030 -*-
from SpawnPoint import SpawnPoint

class SpawnPointTianguan( SpawnPoint ):
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
		entityParams[ "level" ] = params[ "level" ].asInt
		entityParams[ "teamcount" ] = params[ "teamcount" ].asInt
		entityParams[ "mapName" ] = params[ "mapName" ].asString
		entityParams[ "monsterType" ] = params[ "monsterType" ].asInt
		return entityParams
	