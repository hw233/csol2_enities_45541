# -*- coding: gb18030 -*-
# $Id: Exp $

# spawnEntity死亡destroy后，通知其spawnPoint自己死亡的位置，让spawnPoint在死亡的位置上复活一个新的spawnEntity

import BigWorld
import csdefine
from bwdebug import *
from Monster import Monster

class MonsterReviveCurrentPosition( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		spawnEntity死亡destroy后，通知其spawnPoint自己死亡的位置，让spawnPoint在死亡的位置上复活一个新的spawnEntity
		"""
		Monster.__init__( self )
		
	def onDestroy( self, selfEntity ):
		"""
		virtual method
		"""
		if selfEntity.spawnMB:
			# 有spawnMB的怪物需要通知它的出生点，(可能)重新复活
			if BigWorld.entities.has_key( selfEntity.spawnMB.id ):
				BigWorld.entities[selfEntity.spawnMB.id].remoteCallScript( "wuyaoqiangshao_entityDead", [ selfEntity.position, selfEntity.direction ] )
			else:
				selfEntity.spawnMB.cell.remoteCallScript( "wuyaoqiangshao_entityDead", [ selfEntity.position, selfEntity.direction ] )
