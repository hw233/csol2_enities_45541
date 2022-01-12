# -*- coding: gb18030 -*-
import BigWorld
from Monster import Monster
from bwdebug import *
import csconst
import csdefine
import Language

class Monster_NotifyHPToSpace(Monster):
	"""
	����Ѫ���仯ͨ��space
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		Monster.__init__( self )
		
		
	def dieNotify( self, selfEntity, killerID ):
		"""
		����֪ͨ��selfEntity��die()������ʱ������
		"""
		Monster.dieNotify( self, selfEntity, killerID )
		selfEntity.getCurrentSpaceBase().cell.onNotifySpaceMonsterDie( self.className, killerID )
	
	def onHPChanged( self, selfEntity ):
		"""
		Ѫ�������ı�
		"""
		spaceBaseMailbox = selfEntity.getCurrentSpaceBase()
		if spaceBaseMailbox:
			if BigWorld.entities.has_key( spaceBaseMailbox.id ):
				BigWorld.entities[ spaceBaseMailbox.id ].onNotifySpaceMonsterHP( self.className, selfEntity.HP, selfEntity.HP_Max )
			else:
				spaceBaseMailbox.cell.onNotifySpaceMonsterHP( self.className, selfEntity.HP, selfEntity.HP_Max )
