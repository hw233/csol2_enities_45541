# -*- coding: gb18030 -*-

from SpawnPointCopy import SpawnPointCopy

class SpawnPointBelongTeam( SpawnPointCopy ):
	"""
	英雄联盟PVP BOSS刷新点
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopy.initEntity( self, selfEntity )
	
	def initEntityParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化参数
		"""
		entityParams = {}
		entityParams[ "belong" ] = params[ "belong" ].asInt
		return entityParams