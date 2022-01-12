# -*- coding: gb18030 -*-
"""
副本怪物出生点，死亡后在原地复活
"""
from SpawnPointCopy import SpawnPointCopy

class SpawnPointCopyRevival( SpawnPointCopy ):
	"""
	副本中怪物出生点类型
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopy.initEntity( self, selfEntity )

