# -*- coding: gb18030 -*-


"""
用于固定整点刷新的功能
"""

import BigWorld
from bwdebug import *
import csdefine
import csconst
import Const
import random
from SpawnPoint import SpawnPoint

class SpawnPointFixTime( SpawnPoint ):
	"""
	整几点刷新怪物。
	支持随机地点。（positions）
	"""
	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		h = time.localtime()[3]
		m = time.localtime()[4]
		
		if self.fixTime == 0:
			self.fixTime = 1
		t1 = h  % self.fixTime
		
		rTime = ( self.fixTime - t1 - 1 ) + ( 60 - m ) * 60

		selfEntity.rediviousTimer = selfEntity.addTimer( rTime, 0, Const.SPAWN_ON_MONSTER_DIED )
	
	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		获取要创建的entity参数
		"""
		args = SpawnPoint.getEntityArgs( selfEntity, params )
		position = None
		if selfEntity.positions != "":
			position = eval( random.choice( selfEntity.positions.split("|") ) )
		else:
			position = tuple( selfEntity.position )
			
		args[ "position" ] = position
		args[ "spawnPos" ] = position
		return args