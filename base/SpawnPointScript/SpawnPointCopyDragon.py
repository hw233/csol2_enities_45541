# -*- coding: gb18030 -*-
"""
�콵���޸����й��������
"""

from SpawnPointCopy import SpawnPointCopy

class SpawnPointCopyDragon( SpawnPointCopy ):
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