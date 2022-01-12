# -*- coding: gb18030 -*-
import BigWorld
from SpawnPointNormalActivity import SpawnPointNormalActivity

class SpawnPointActivityHundun( SpawnPointNormalActivity ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		selfEntity.setTemp( 'activityManagerKey', "HundunMgr" )
		selfEntity.setTemp( 'monsterClassNames', [selfEntity.entityName] )
		SpawnPointNormalActivity.initEntity( self, selfEntity )
