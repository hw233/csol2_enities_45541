# -*- coding: gb18030 -*-
"""
���Ȫm؅���������
"""
from SpawnPointCopyYeWai import SpawnPointCopyYeWai

class SpawnPointCopyYayuMonster( SpawnPointCopyYeWai ):
	"""
	�����й������������
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopyYeWai.initEntity( self, selfEntity )
	
	def initTempParams( self, spaceEntity, params ):
		"""
		virtual method.
		��ʼ������
		"""
		tempMapping = SpawnPointCopyYeWai.initTempParams( self, spaceEntity, params )
		tempMapping[ "difficulty" ] = spaceEntity.params[ "difficulty" ]
		return tempMapping