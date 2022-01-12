# -*- coding: gb18030 -*-
import BigWorld

from SpawnPoint import SpawnPoint

class SpawnPointChallenge( SpawnPoint ):
	"""
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def initEntityParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化一下参数
		"""
		entityParams = {}
		level = spaceEntity.params[ "spaceChallengeGate" ]
		if spaceEntity.params[ "spaceChallengeGate" ]  == 400:
			if BigWorld.globalData.has_key( "SCC_piShanNPC_%s" % spaceEntity.params[ "spaceChallengeKey" ] ):
				level = BigWorld.globalData[ "SCC_piShanNPC_%s" % spaceEntity.params[ "spaceChallengeKey" ] ]
			else:
				level = 1
			
		entityParams[ "level" ] = level
		return entityParams
	
	def initTempParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化参数
		"""
		tempMapping = {}
		tempMapping[ "monsterType" ] = eval( params["monsterType"].asString )
		return tempMapping