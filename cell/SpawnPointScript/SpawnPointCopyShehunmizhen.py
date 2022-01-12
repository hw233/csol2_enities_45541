# -*- coding: gb18030 -*-
import Const

from SpawnPointCopyYeWai import SpawnPointCopyYeWai
from ObjectScripts.GameObjectFactory import g_objFactory

class SpawnPointCopyShehunmizhen( SpawnPointCopyYeWai ):
	# # 摄魂迷阵 副本刷新点
	def initEntity( self, selfEntity ):
		SpawnPointCopyYeWai.initEntity( self, selfEntity )
		selfEntity.getCurrentSpaceBase().addSpawnPoint( selfEntity.base, selfEntity.queryTemp( "monsterType", 0 ) )
	
	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		cp = selfEntity.getCurrentSpaceBase()
		if cp is None:
			return
			
		cp.cell.onConditionChange( {"monsterType":selfEntity.queryTemp( "monsterType", 0 )} )
		cp.cell.onCertenMonsterDie( selfEntity.entityName )

		# 小于0则不复活
		if selfEntity.rediviousTime < 0:
			return
			
		selfEntity.currentRedivious += 1
		if not selfEntity.rediviousTimer:
			selfEntity.rediviousTimer = selfEntity.addTimer( selfEntity.rediviousTime, 0, Const.SPAWN_ON_MONSTER_DIED )
