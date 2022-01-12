# -*- coding: gb18030 -*-

from SpawnPointNormalActivity import SpawnPointNormalActivity

class SpawnPointActivityTDBattle( SpawnPointNormalActivity ):
	"""
	仙魔论战活动刷新点
	"""
	def initEntity( self, selfEntity ):
		SpawnPointNormalActivity.initEntity( self, selfEntity )