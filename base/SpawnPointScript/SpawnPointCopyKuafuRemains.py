# -*- coding: gb18030 -*-
"""
�丸��������
"""
from SpawnPointCopyYeWai import SpawnPointCopyYeWai

class SpawnPointCopyKuafuRemains( SpawnPointCopyYeWai ):
	"""
	�����й������������
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopyYeWai.initEntity( self, selfEntity )
	
	def initTempParams( self, spaceEntity, params ):
		"""
		virtual method.
		��ʼ��һ�²���
		"""
		tempMapping = {}
		tempMapping[ "entityType" ] = params[ "entityType" ].asInt
		tempMapping[ "step" ] = params[ "step" ].asInt
		tempMapping[ "group" ] = params[ "group" ].asInt
		tempMapping[ "event" ] = params[ "event" ].asInt
		tempMapping[ "isSpawnOnStep" ] = params[ "isSpawnOnStep" ].asInt
		return tempMapping