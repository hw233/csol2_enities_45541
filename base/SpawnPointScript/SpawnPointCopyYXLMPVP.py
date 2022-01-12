# -*- coding: gb18030 -*-
from SpawnPointBelongTeam import SpawnPointBelongTeam

class SpawnPointCopyYXLMPVP( SpawnPointBelongTeam ):
	"""
	Ӣ������PVP BOSSˢ�µ�
	"""
	def initEntity( self, selfEntity ):
		SpawnPointBelongTeam.initEntity( self, selfEntity )
	
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