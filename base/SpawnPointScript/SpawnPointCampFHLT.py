# -*- coding: gb18030 -*-

from SpawnPoint import SpawnPoint

class SpawnPointCampFHLT( SpawnPoint ):
	# ������սˢ�ֵ�
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def initEntityParams( self, spaceEntity, params ):
		"""
		virtual method.
		��ʼ������
		"""
		entityParams = {}
		entityParams[ "belongCamp" ] = params[ "belongCamp" ].asInt
		return entityParams