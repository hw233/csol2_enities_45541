# -*- coding: gb18030 -*-

from SpawnPointCopy import SpawnPointCopy
import BigWorld
from SpawnPointNormalActivity import SpawnPointNormalActivity

class SpawnPointActivityPig( SpawnPointNormalActivity ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		selfEntity.setTemp( 'activityManagerKey', "DuDuZhuMgr" )
		selfEntity.setTemp( 'monsterClassNames', [selfEntity.entityName] )
		SpawnPointNormalActivity.initEntity( self, selfEntity )