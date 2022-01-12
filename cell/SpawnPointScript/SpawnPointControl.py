# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
import csdefine
import csconst
import Const
from interface.GameObject import GameObject
from ObjectScripts.GameObjectFactory import g_objFactory
import random
from SpawnPoint import SpawnPoint

class SpawnPointControl( SpawnPoint ):
	"""
	这个刷新点新增了3个功能：1.怪可控制不停的刷新；2.这个刷新点的怪死亡后，可以改变它的刷新时间；3.由AI控制它不再刷怪
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPoint.initEntity( self, selfEntity  )
		selfEntity.getCurrentSpaceBase().addSpawnPointControl( selfEntity.base )
		
	def entityDead( self, selfEntity ):
		"""
		"""
		# 小于0则不复活
		if selfEntity.rediviousTime < 0:
			return
		
		elif self.PlotMonsterType == 1:		# 地编配置的值为1时不需要通过死亡来处理刷新
			return
		
		elif not selfEntity.rediviousTimer:					# 按正常流程：怪物死亡后按地编配置时间刷新
			selfEntity.currentRedivious += 1
			selfEntity.rediviousTimer = selfEntity.addTimer( selfEntity.rediviousTime, 0, Const.SPAWN_ON_MONSTER_DIED )
			return
		
	def createEntity( self, selfEntity, params = {} ):
		"""
		define method
		"""
		SpawnPoint.createEntity( self, selfEntity, params )
		
		if self.PlotMonsterType == 1:
			# 刷怪类型由策划配置，值为1时无论怪物死亡与否，都会不停的刷新
			selfEntity.addTimer( self.PlotRediviousTime, 0.0, Const.SPAWN_ON_SERVER_START )