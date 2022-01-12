# -*- coding: gb18030 -*-

from bwdebug import *
from Monster import Monster

class MonsterYXLM( Monster ):
	"""
	Ӣ�����˹���������أ�
	"""
	def __init__( self ):
		Monster.__init__( self )
		
	def onMonsterDie( self, selfEntity, killerID ):
		"""
		yxlm�������еĲ�������
		"""
		self.dieNotify( selfEntity, killerID )
		selfEntity.getSpaceCell().unRegistMonster( selfEntity.className, selfEntity )
		bootyOwner = selfEntity.getBootyOwner()					# ����ӵ����
		if bootyOwner[0] != 0:							# ��õ���ɱ������
			killers = selfEntity.gainSingleReward( bootyOwner[0] )
			for entity in killers:
				entity.client.onShowAccumPoint( selfEntity.id, selfEntity.accumPoint )
		else:
			INFO_MSG( "%s(%i): I died, but no booty owner." % ( selfEntity.className, selfEntity.id ) )
