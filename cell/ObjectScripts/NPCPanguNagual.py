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
	�̹��ػ�
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )

	def onMonsterDie( self, selfEntity, killerID ):
		"""
		�̹��ػ�������Ӧ��֪ͨ��ͼ�����������˴��ٻ��б���ɾ���Լ�
		"""
		owner = selfEntity.getOwner()
		if hasattr( owner, "cell"):					# ����õ�������ΪBaseMailBox
			owner.cell.removePGNagual( selfEntity.attackType, selfEntity.id )
		else:
			owner.removePGNagual( selfEntity.attackType, selfEntity.id )
			
		Monster.onMonsterDie( self, selfEntity, killerID )
