# -*- coding: gb18030 -*-

"""
英雄联盟攻城车和精英的出生点
"""

from SpawnPointCopy import SpawnPointCopy

class SpawnPointCopyYXLM( SpawnPointCopy ):
	"""
	副本中怪物出生点类型
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopy.initEntity( self, selfEntity )

	def initEntityParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化一下参数
		"""
		entityParams = {}
		entityParams[ "level" ] = params[ "level" ].asInt
		entityParams[ "teamcount" ] = params[ "teamcount" ].asInt
		entityParams[ "mapName" ] = params[ "mapName" ].asString
		entityParams[ "monsterType" ] = params[ "monsterType" ].asInt
		return entityParams