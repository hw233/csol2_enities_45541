# -*- coding: gb18030 -*-

# $Id: Exp $
"""
"""

from bwdebug import *
import csdefine
from ObjectScripts.GameObjectFactory import g_objFactory
import random
import ECBExtend
import BigWorld
from SpawnPointActivity import SpawnPointActivity

class SpawnPointNormalActivity( SpawnPointActivity ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPointActivity.initEntity( self, selfEntity )
		mgrBase = BigWorld.globalData[ selfEntity.queryTemp( "activityManagerKey" ) ]
		mgrBase.addActivityMonsterSpawnPoint( selfEntity.spaceType, selfEntity.base, selfEntity.getCurrentSpaceLineNumber() )

	def getEntityArgs( self, selfEntity, params = {} ):
		return SpawnPointActivity.getEntityArgs( self, selfEntity, params )
		
	def createEntity( self, selfEntity, params = {} ):
		"""
		virtual method.
		"""
		args = self.getEntityArgs( selfEntity, params )
		entitys = self._createEntity( selfEntity, args, 1 )
		if len( entitys ):
			selfEntity.setTemp( 'monsterID', entitys[0].id )

	def entityDead( self, selfEntity ):
		"""
		virtual method.
		怪物死亡通知
		"""
		mgrBase = BigWorld.globalData[selfEntity.queryTemp("activityManagerKey")]
		mgrBase.onMonsterDie( selfEntity.spaceType, selfEntity.base )

	def onActivityEnd( self, selfEntity ):
		"""
		define method
		"""
		id = selfEntity.queryTemp( 'monsterID', 0 )
		monster = BigWorld.entities.get( id, None )
		if monster:
			monster.resetEnemyList()
			monster.destroy()
	
	def onBaseGotCell( self, selfEntity ):
		"""
		由base回调回来，通知spawn point，base已经获得了cell的通知
		"""
		pass
