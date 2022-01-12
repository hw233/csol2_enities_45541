# -*- coding: gb18030 -*-

import csdefine
from bwdebug import *
from SpawnPointCopy import SpawnPointCopy
from ObjectScripts.GameObjectFactory import g_objFactory

class SpawnPointCityWarFinal( SpawnPointCopy ):
	"""
	���ս����ˢ�µ�
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopy.initEntity( self, selfEntity )
		
	def createEntity( self, selfEntity, params = {} ):
		"""
		"""
		monsterType = selfEntity.queryTemp( "monsterType", 0 )
		if monsterType == csdefine.CITY_WAR_FINAL_LIGHT_WALL:	# ��ǽ���ô���base
			args = self.getEntityArgs( selfEntity, params )
			e = self._createEntity( selfEntity, args, 1 )[0]#ֻ����һ��
			spawnMonsterIDs = selfEntity.queryTemp( "spawnMonsterIDs", [] )
			spawnMonsterIDs.append( e.id )
			selfEntity.setTemp( "spawnMonsterIDs", spawnMonsterIDs )
			
			spaceBase = selfEntity.getCurrentSpaceBase()
			if spaceBase:
				spaceBase.cell.onCityWarBaseCreated( selfEntity.base, csdefine.CITY_WAR_FINAL_LIGHT_WALL, 0, "" )
		else:
			args = self.getEntityArgs( selfEntity, params )
			selfEntity.base.createBaseEntity( selfEntity.entityName, args )

	def destroySpawnMonster( self, selfEntity ):
		"""
		����ˢ�µĹ���
		"""
		for id in selfEntity.queryTemp( "spawnMonsterIDs", [] ):
			e = BigWorld.entities.get( id )
			if e:
				e.destroy()
		
		selfEntity.setTemp( "spawnMonsterIDs", [] )