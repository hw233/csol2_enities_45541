# -*- coding: gb18030 -*-
import BigWorld
from SpawnPointNormalActivity import SpawnPointNormalActivity

class SpawnPointActivityTianjiangqishou( SpawnPointNormalActivity ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		selfEntity.setTemp( 'activityManagerKey', "TianjiangqishouMgr" )
		selfEntity.setTemp( 'monsterClassNames', [selfEntity.entityName] )
		SpawnPointNormalActivity.initEntity( self, selfEntity )