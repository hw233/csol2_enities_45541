# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from SpawnPointNormalActivity import SpawnPointNormalActivity
from TimeString import TimeString
import random
import csdefine
import csconst
import Const

class SpawnPointLiuWangMuMonster( SpawnPointNormalActivity ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		selfEntity.setTemp( 'activityManagerKey', "LiuWangMuMgr" )
		selfEntity.setTemp( 'monsterClassNames', [selfEntity.entityName] )
		SpawnPointNormalActivity.initEntity( self, selfEntity )

	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		# 小于0则不复活
		if selfEntity.rediviousTime < 0:
			return
			
		selfEntity.currentRedivious += 1
		if not selfEntity.rediviousTimer:
			#自己所在层数与管理器开放的层数一致为1时，才会复活
			if selfEntity.queryTemp( "floorNum" ) == BigWorld.globalData["AS_LiuWangMu"] == 1:
				selfEntity.rediviousTimer = selfEntity.addTimer( selfEntity.rediviousTime, 0, Const.SPAWN_ON_MONSTER_DIED )
	
	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		获取要创建的entity参数
		"""
		args = SpawnPointNormalActivity.getEntityArgs( self, selfEntity, params )
		
		args[ "className" ] = ""
		monsterType = selfEntity.queryTemp( "monsterType", 0 )
		spawnTime = selfEntity.queryTemp( "spawnTime", 0 )
		if monsterType and TimeString( spawnTime ).timeCheck() or not monsterType:#刷出boss
			args[ "className" ] = selfEntity.entityName
		
		return args
	
	def _createEntity( self, selfEntity, args, num ):
		"""
		virtual method.
		创建怪物
		"""
		if args[ "className" ] == "":
			return []
		
		return SpawnPointNormalActivity._createEntity( self, selfEntity, args, num )
	
	def onBaseGotCell( self, selfEntity ):
		"""
		由base回调回来，通知spawn point，base已经获得了cell的通知
		"""
		selfEntity.addTimer( 0.5, 0, Const.SPAWN_ON_SERVER_START  )