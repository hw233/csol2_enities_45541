# -*- coding: gb18030 -*-

from SpawnPoint import SpawnPoint

class SpawnPointTongFHLT( SpawnPoint ):
	# ������սˢ�ֵ�
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def initEntityParams( self, spaceEntity, params ):
		"""
		virtual method.
		��ʼ��һ�²���
		"""
		entityParams = {}
		entityParams[ "belongTong" ] = params[ "belongTong" ].asInt
		return entityParams