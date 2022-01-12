# -*- coding: gb18030 -*-
import BigWorld
from Monster import Monster
from bwdebug import *
import csconst
import csdefine
import Language

class Monster_NotifyHPToSpace(Monster):
	"""
	怪物血量变化通过space
	"""
	def __init__( self ):
		"""
		初始化
		"""
		Monster.__init__( self )
		
		
	def dieNotify( self, selfEntity, killerID ):
		"""
		死亡通知；selfEntity的die()被触发时被调用
		"""
		Monster.dieNotify( self, selfEntity, killerID )
		selfEntity.getCurrentSpaceBase().cell.onNotifySpaceMonsterDie( self.className, killerID )
	
	def onHPChanged( self, selfEntity ):
		"""
		血量发生改变
		"""
		spaceBaseMailbox = selfEntity.getCurrentSpaceBase()
		if spaceBaseMailbox:
			if BigWorld.entities.has_key( spaceBaseMailbox.id ):
				BigWorld.entities[ spaceBaseMailbox.id ].onNotifySpaceMonsterHP( self.className, selfEntity.HP, selfEntity.HP_Max )
			else:
				spaceBaseMailbox.cell.onNotifySpaceMonsterHP( self.className, selfEntity.HP, selfEntity.HP_Max )
