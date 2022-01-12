# -*- coding: gb18030 -*-

from SpawnPointActivity import SpawnPointActivity

class SpawnPointNormalActivity( SpawnPointActivity ):
	"""
	英雄联盟PVP BOSS刷新点
	"""
	def initEntity( self, selfEntity ):
		SpawnPointActivity.initEntity( self, selfEntity )