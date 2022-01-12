# -*- coding: gb18030 -*-

from SpawnPointCopy import SpawnPointCopy

class SpawnPointYXLMBoss( SpawnPointCopy ):
	"""
	英雄联盟PVP BOSS刷新点
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopy.initEntity( self, selfEntity )
		selfEntity.belong = selfEntity.cellData[ "entityParams" ][ "belong" ]

	def initEntityParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化一下参数
		"""
		entityParams = {}
		belong = params[ "belongTeamID" ].asInt
		teamID = 0
		if belong < len( spaceEntity.teamInfos ):
			teamID = spaceEntity.teamInfos[ belong ]
				
		entityParams[ "belong" ] = teamID
		return entityParams