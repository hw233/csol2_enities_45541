# -*- coding: gb18030 -*-
from SpawnPointCopy import SpawnPointCopy

class SpawnPointCopyYayu( SpawnPointCopy ):
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
		tempMapping[ "monsterType" ] = params[ "monsterType" ].asInt
		return tempMapping