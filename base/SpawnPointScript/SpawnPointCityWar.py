# -*- coding: gb18030 -*-

from SpawnPoint import SpawnPoint

class SpawnPointCityWar( SpawnPoint ):
	# 帮会城市战刷怪点
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def initEntityParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化参数
		"""
		entityParams = {}
		entityParams[ "belong" ] = params[ "belong" ].asInt
		entityParams[ "monsterType" ] = params[ "monsterType" ].asInt
		entityParams[ "damageToIntegral" ] = params[ "damageToIntegral" ].asInt
		return entityParams