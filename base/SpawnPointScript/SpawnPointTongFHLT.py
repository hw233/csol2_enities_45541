# -*- coding: gb18030 -*-

from SpawnPoint import SpawnPoint

class SpawnPointTongFHLT( SpawnPoint ):
	# 帮会城市战刷怪点
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def initEntityParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化一下参数
		"""
		entityParams = {}
		entityParams[ "belongTong" ] = params[ "belongTong" ].asInt
		return entityParams