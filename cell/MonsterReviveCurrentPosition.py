# -*- coding: gb18030 -*-
# $Id: Exp $

# spawnEntity����destroy��֪ͨ��spawnPoint�Լ�������λ�ã���spawnPoint��������λ���ϸ���һ���µ�spawnEntity

from bwdebug import *
from Monster import Monster
import csdefine
import BigWorld

class MonsterReviveCurrentPosition( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		spawnEntity����destroy��֪ͨ��spawnPoint�Լ�������λ�ã���spawnPoint��������λ���ϸ���һ���µ�spawnEntity
		"""
		Monster.__init__( self )
		
	def onDestroy( self ):
		"""
		entity ���ٵ�ʱ����BigWorld.Entity�Զ����ã�spawnEntity����destroy��֪ͨ��spawnPoint�Լ�������λ��
		"""
		self.doAllEventAI( csdefine.AI_EVENT_ENTITY_ON_DESTROY )
		
		DEBUG_MSG( "%i: I dies." % self.id )

		if self.spawnMB:
			# ��spawnMB�Ĺ�����Ҫ֪ͨ���ĳ����㣬(����)���¸���
			if BigWorld.entities.has_key( self.spawnMB.id ):
				BigWorld.entities[self.spawnMB.id].remoteCallScript( "wuyaoqiangshao_entityDead", [ self.position, self.direction ] )
			else:
				self.spawnMB.cell.remoteCallScript( "wuyaoqiangshao_entityDead", [ self.position, self.direction ] )
