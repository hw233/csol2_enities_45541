# -*- coding: gb18030 -*-

from SpawnPointCopy import SpawnPointCopy

class SpawnPointBelongTeam( SpawnPointCopy ):
	"""
	Ӣ������PVP BOSSˢ�µ�
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopy.initEntity( self, selfEntity )
	
	def initEntityParams( self, spaceEntity, params ):
		"""
		virtual method.
		��ʼ������
		"""
		entityParams = {}
		entityParams[ "belong" ] = params[ "belong" ].asInt
		return entityParams