# -*- coding: gb18030 -*-
# $Id: Exp $

# spawnEntity死亡destroy后，通知其spawnPoint自己死亡的位置，让spawnPoint在死亡的位置上复活一个新的spawnEntity

from bwdebug import *
from Monster import Monster
import csdefine
import BigWorld

class MonsterReviveCurrentPosition( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		spawnEntity死亡destroy后，通知其spawnPoint自己死亡的位置，让spawnPoint在死亡的位置上复活一个新的spawnEntity
		"""
		Monster.__init__( self )
		
	def onDestroy( self ):
		"""
		entity 销毁的时候由BigWorld.Entity自动调用；spawnEntity死亡destroy后，通知其spawnPoint自己死亡的位置
		"""
		self.doAllEventAI( csdefine.AI_EVENT_ENTITY_ON_DESTROY )
		
		DEBUG_MSG( "%i: I dies." % self.id )

		if self.spawnMB:
			# 有spawnMB的怪物需要通知它的出生点，(可能)重新复活
			if BigWorld.entities.has_key( self.spawnMB.id ):
				BigWorld.entities[self.spawnMB.id].remoteCallScript( "wuyaoqiangshao_entityDead", [ self.position, self.direction ] )
			else:
				self.spawnMB.cell.remoteCallScript( "wuyaoqiangshao_entityDead", [ self.position, self.direction ] )
