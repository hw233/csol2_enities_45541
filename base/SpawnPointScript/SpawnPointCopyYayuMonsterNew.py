# -*- coding: gb18030 -*-
"""
拯救猰貐怪物出生点
"""
from SpawnPointCopyYeWai import SpawnPointCopyYeWai

class SpawnPointCopyYayuMonsterNew( SpawnPointCopyYeWai ):
	"""
	副本中怪物出生点类型
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopyYeWai.initEntity( self, selfEntity )
	
	def initTempParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化参数
		"""
		tempMapping = SpawnPointCopyYeWai.initTempParams( self, spaceEntity, params )
		tempMapping[ "difficulty" ] = spaceEntity.params[ "difficulty" ]
		return tempMapping