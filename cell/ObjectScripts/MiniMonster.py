# -*- coding: gb18030 -*-

"""
���������
"""
from MiniMonster_Mini import MiniMonster_Mini
import BigWorld
import csdefine
import csstatus
from bwdebug import *
import time

class MiniMonster( MiniMonster_Mini ):
	"""
	������������࣬��Ҫ�����У�
	1��������Ч�Լ��
	2����������Ұ��Χ�ĵ���
	3��ÿ��4��ѡ������˺�ΪĿ��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		MiniMonster_Mini.__init__( self )
		self.skillID = 0
		
	def onFightAIHeartbeat( self, selfEntity ):
		"""
		ս��״̬��AI �� ����
		"""
		MiniMonster_Mini.onFightAIHeartbeat( self, selfEntity )
		
		# ÿ��3��ѡ������˺�ΪĿ��
		if selfEntity.fightStartTime > 0 and  int( ( time.time() - selfEntity.fightStartTime ) ) % 3 == 1:
			self.getFirstDamage( selfEntity )
			if selfEntity.hasEnemy( selfEntity.aiTargetID ) and BigWorld.entities.has_key( selfEntity.aiTargetID ) and selfEntity.targetID != selfEntity.aiTargetID:
				selfEntity.changeAttackTarget( selfEntity.aiTargetID )

	def getFirstDamage( self, selfEntity ):
		"""
		ѡ������˺�Ŀ��
		"""
		eid = 0
		rval = 0
		for id, val in selfEntity.damageList.iteritems():
			if val > rval:
				rval = val
				eid = id
		if eid > 0:
			 selfEntity.aiTargetID = eid