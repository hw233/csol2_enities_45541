# -*- coding: gb18030 -*-
# $Id: Exp $

# spawnEntity����destroy��֪ͨ��spawnPoint�Լ�������λ�ã���spawnPoint��������λ���ϸ���һ���µ�spawnEntity

import BigWorld
import csdefine
from bwdebug import *
from Monster import Monster

class MonsterReviveCurrentPosition( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		spawnEntity����destroy��֪ͨ��spawnPoint�Լ�������λ�ã���spawnPoint��������λ���ϸ���һ���µ�spawnEntity
		"""
		Monster.__init__( self )
		
	def onDestroy( self, selfEntity ):
		"""
		virtual method
		"""
		if selfEntity.spawnMB:
			# ��spawnMB�Ĺ�����Ҫ֪ͨ���ĳ����㣬(����)���¸���
			if BigWorld.entities.has_key( selfEntity.spawnMB.id ):
				BigWorld.entities[selfEntity.spawnMB.id].remoteCallScript( "wuyaoqiangshao_entityDead", [ selfEntity.position, selfEntity.direction ] )
			else:
				selfEntity.spawnMB.cell.remoteCallScript( "wuyaoqiangshao_entityDead", [ selfEntity.position, selfEntity.direction ] )
