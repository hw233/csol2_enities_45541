# -*- coding: gb18030 -*-

from SpawnPointCopy import SpawnPointCopy

class SpawnPointYXLMBoss( SpawnPointCopy ):
	"""
	Ӣ������PVP BOSSˢ�µ�
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopy.initEntity( self, selfEntity )
		selfEntity.belong = selfEntity.cellData[ "entityParams" ][ "belong" ]

	def initEntityParams( self, spaceEntity, params ):
		"""
		virtual method.
		��ʼ��һ�²���
		"""
		entityParams = {}
		belong = params[ "belongTeamID" ].asInt
		teamID = 0
		if belong < len( spaceEntity.teamInfos ):
			teamID = spaceEntity.teamInfos[ belong ]
				
		entityParams[ "belong" ] = teamID
		return entityParams