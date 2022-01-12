# -*- coding: gb18030 -*-

"""
���������
"""
from MiniMonster import MiniMonster
import csstatus
from bwdebug import *

class MiniMonster_CallPartner(	MiniMonster	):
	"""
	������������࣬��Ҫ�����У�
	1��������Ч�Լ��
	2����������Ұ��Χ�ĵ���
	3��ÿ��4��ѡ������˺�ΪĿ��
	4������ͬ��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		MiniMonster.__init__( self )
		
	def onFightAIHeartbeat( self, selfEntity ):
		"""
		ս��״̬��AI �� ����
		"""
		MiniMonster.onFightAIHeartbeat( self, selfEntity )
		
		# �������ͬ�鹦��
		if selfEntity.queryTemp( "callSign", True ):
			return
		if selfEntity.callRange:
			selfEntity.setTemp( "callSign", True )
			for e in selfEntity.entitiesInRangeExt( selfEntity.callRange, None, selfEntity.position ):
				if e.className in self.callList:
					e.onFightCall( selfEntity.targetID, selfEntity.className )
		