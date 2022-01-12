# -*- coding: gb18030 -*-

# added by dqh


# bigworld
import BigWorld
# common
import csdefine
from bwdebug import *
# cell
from Monster import Monster

class NPCPanguNagual( Monster ):
	"""
	盘古守护
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )

	def onMonsterDie( self, selfEntity, killerID ):
		"""
		盘古守护死亡后应该通知地图管理器和主人从召唤列表中删除自己
		"""
		owner = selfEntity.getOwner()
		if hasattr( owner, "cell"):					# 如果得到的主人为BaseMailBox
			owner.cell.removePGNagual( selfEntity.attackType, selfEntity.id )
		else:
			owner.removePGNagual( selfEntity.attackType, selfEntity.id )
			
		Monster.onMonsterDie( self, selfEntity, killerID )
