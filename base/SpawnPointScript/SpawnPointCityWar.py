# -*- coding: gb18030 -*-

from SpawnPoint import SpawnPoint

class SpawnPointCityWar( SpawnPoint ):
	# ������սˢ�ֵ�
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def initEntityParams( self, spaceEntity, params ):
		"""
		virtual method.
		��ʼ������
		"""
		entityParams = {}
		entityParams[ "belong" ] = params[ "belong" ].asInt
		entityParams[ "monsterType" ] = params[ "monsterType" ].asInt
		entityParams[ "damageToIntegral" ] = params[ "damageToIntegral" ].asInt
		return entityParams