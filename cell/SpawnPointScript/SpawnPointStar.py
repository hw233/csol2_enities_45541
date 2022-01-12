# -*- coding: gb18030 -*-

from bwdebug import *
from SpawnPoint import SpawnPoint
from ObjectScripts.GameObjectFactory import g_objFactory
import random
import time

import csdefine
import Const

class SpawnPointStar( SpawnPoint ):
	"""
	根据与策划的沟通,怪物死亡时一次性复活,即第一个怪物死亡后开始计时,计时结束时后面有怪物死亡时一次性复活.
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity  )
	
	def createEntity( self, selfEntity, params = {} ):
		"""
		"""
		selfEntity.rediviousTimer = 0
		SpawnPoint.createEntity( self, selfEntity, params )
		selfEntity.currentRedivious = 0

	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		selfEntity.currentRedivious += 1
		
		h = time.localtime()[3]
		m = time.localtime()[4]
		
		if h  % 2 == 0:
			rt = 3600 + ( 60 - m ) * 60
		else:
			rt = ( 60 - m ) * 60
		
		if not selfEntity.rediviousTimer:				#整2个小时刷新
			selfEntity.rediviousTimer = selfEntity.addTimer( rt, 0, Const.SPAWN_ON_MONSTER_DIED )
