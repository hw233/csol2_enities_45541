# -*- coding: gb18030 -*-
"""
天降神兽副本中怪物出生点
"""

from SpawnPointCopy import SpawnPointCopy

class SpawnPointCopyDragon( SpawnPointCopy ):
	"""
	副本中怪物出生点类型
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopy.initEntity( self, selfEntity )

	def initTempParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化参数
		"""
		tempMapping = {}
		tempMapping[ "monsterType" ] = params[ "monsterType" ].asInt
		return tempMapping