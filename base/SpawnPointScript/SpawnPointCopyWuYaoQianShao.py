# -*- coding: gb18030 -*-
"""
副本中怪物出生点
"""
from SpawnPointCopyYeWai import SpawnPointCopyYeWai

class SpawnPointCopyWuYaoQianShao( SpawnPointCopyYeWai ):
	"""
	副本中怪物出生点类型，把出生怪物id通知给所在的space
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopyYeWai.initEntity( self, selfEntity )