# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
import random
from SpawnPointNormalActivity import SpawnPointNormalActivity

class SpawnPointActivityTDBattle( SpawnPointNormalActivity ):
	"""
	仙魔论战活动刷新点
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		selfEntity.setTemp( "activityManagerKey", "TaoismAndDemonBattleMgr" )
		selfEntity.setTemp( 'monsterClassNames', [ selfEntity.entityName ] )
		SpawnPointNormalActivity.initEntity( self, selfEntity )

	def onActivityEnd( self, selfEntity ):
		"""
		define method
		"""
		id = selfEntity.queryTemp( 'monsterID', 0 )
		monster = BigWorld.entities.get( id, None )
		if monster:
			monster.resetEnemyList()
			monster.die( 0 )
	
	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		获取要创建的entity参数
		"""
		args = SpawnPointNormalActivity.getEntityArgs( self, selfEntity, params )
		classNameList = selfEntity.entityName.split(";")
		className = classNameList[ 0 ]
		args[ "className" ] = random.choice( selfEntity.queryTemp("monsterClassNames") )
		args[ "level" ] = 60
		return args