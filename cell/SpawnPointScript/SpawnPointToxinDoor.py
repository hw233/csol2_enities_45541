# -*- coding: gb18030 -*-

from SpawnPointCopy import SpawnPointCopy
import BigWorld
from ObjectScripts.GameObjectFactory import g_objFactory
from SpawnPointNormalActivity import SpawnPointNormalActivity

AI_COMMAND_ID = 1000

class SpawnPointToxinDoor( SpawnPointNormalActivity ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		selfEntity.setTemp( 'activityManagerKey', "ToxinFrogMgr" )
		selfEntity.setTemp( 'monsterClassNames', [selfEntity.entityName] )
		SpawnPointNormalActivity.initEntity( self, selfEntity )
		BigWorld.globalData[selfEntity.queryTemp("activityManagerKey")].addActivityDoorSpawnPoint( selfEntity.spaceType, selfEntity.base )

	def onActivityEnd( self, selfEntity ):
		"""
		define method
		"""
		id = selfEntity.queryTemp( 'monsterID', 0 )
		monster = BigWorld.entities.get( id, None )
		if monster:
			monster.sendAICommand( id, AI_COMMAND_ID )
			monster.destroy()
