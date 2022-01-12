# -*- coding: gb18030 -*-

"""
Ӣ�����˹��ǳ��;�Ӣ�ĳ�����
"""

from SpawnPointCopy import SpawnPointCopy

class SpawnPointCopyYXLM( SpawnPointCopy ):
	"""
	�����й������������
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopy.initEntity( self, selfEntity )

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