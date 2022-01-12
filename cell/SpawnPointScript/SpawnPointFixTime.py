# -*- coding: gb18030 -*-


"""
���ڹ̶�����ˢ�µĹ���
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
	������ˢ�¹��
	֧������ص㡣��positions��
	"""
	def entityDead( self, selfEntity ):
		"""
		Define method.
		��������֪ͨ
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
		��ȡҪ������entity����
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