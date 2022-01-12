# -*- coding: gb18030 -*-
from SpawnPoint import SpawnPoint

class SpawnPointMonsterAttack( SpawnPoint ):
	"""
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def initTempParams( self, spaceEntity, params ):
		"""
		virtual method.
		��ʼ������
		"""
		tempMapping = {}
		tempMapping[ "monsterType" ] = params[ "monsterType" ].asFloat
		tempMapping[ "buffRange" ] = params[ "buffRange" ].asInt
		tempMapping[ "group" ] = params[ "group" ].asInt
		tempMapping[ "part" ] = params[ "part" ].asInt
		tempMapping[ "buffID" ] = params[ "buffID" ].asInt
		return tempMapping