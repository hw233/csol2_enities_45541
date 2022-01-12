# -*- coding: gb18030 -*-
import BigWorld
import csdefine
from SpawnPointNormalActivity import SpawnPointNormalActivity


class SpawnPointToxinMonster( SpawnPointNormalActivity ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		selfEntity.setTemp( 'activityManagerKey', "ToxinFrogMgr" )
		SpawnPointNormalActivity.initEntity( self, selfEntity )

	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		获取要创建的entity参数
		"""
		args = SpawnPointNormalActivity.getEntityArgs( self, selfEntity, params )
		classNameList = selfEntity.entityName.split(";")
		className = classNameList[ 0 ]
		args[ "className" ] = className
		args[ "level" ] = 0
		return args
		
	def spawnAndDestroyMonster( self, selfEntity, playerMB, level, index ):
		"""
		define method
		"""
		args = self.getEntityArgs( selfEntity )
		args[ "level" ] = level
		classNameList = selfEntity.entityName.split(";")
		className = classNameList[ index ]
		args[ "className" ] = className
		
		entity = self._createEntity( selfEntity, args, 1 )[0]
		playerEntity = BigWorld.entities.get( playerMB.id, None )
		bootyOwner = ()
		if playerEntity:
			getEnemyTeam = getattr( playerEntity, "getTeamMailbox", None )
			if getEnemyTeam and getEnemyTeam():
				bootyOwner = ( playerEntity.id, getEnemyTeam().id )
				entity.addCombatRelationIns( csdefine.RELATION_DYNAMIC_TEAM_ANTAGONIZE, getEnemyTeam().id )
			else:
				bootyOwner = ( playerEntity.id, 0 )
				entity.addCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_ANTAGONIZE_ID, playerEntity.id )
				
		entity.setTemp( "ToxinFrog_bootyOwner", bootyOwner )	# 设置战利品拥有者
		id = selfEntity.queryTemp( 'monsterID', 0 )
		monster = BigWorld.entities.get( id, None )
		if monster:
			monster.resetEnemyList()
			monster.destroy()