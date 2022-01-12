# -*- coding: gb18030 -*-
import BigWorld
from SpawnPointNormalActivity import SpawnPointNormalActivity
from Resource.MonsterActivityMgr import MonsterActivityMgr

class SpawnPointActivityMonster( SpawnPointNormalActivity ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		selfEntity.setTemp( "activityManagerKey", "MonsterActivityManager" )
		selfEntity.setTemp( 'monsterClassNames', MonsterActivityMgr.instance().activityMonsterBossIDs )
		SpawnPointNormalActivity.initEntity( self, selfEntity )