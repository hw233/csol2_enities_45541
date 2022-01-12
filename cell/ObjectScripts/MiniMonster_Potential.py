# -*- coding: gb18030 -*-

"""
���������
"""
from MiniMonster import MiniMonster
import csstatus
from bwdebug import *

class MiniMonster_Potential(	MiniMonster	):
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
		self._potential = 0
		
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
		
	def dieNotify( self, selfEntity, killerID ):
		"""
		����֪ͨ����selfEntity��die()������ʱ������
		"""
		spaceBase = selfEntity.queryTemp( "space", None )
		spaceEntity = None
		
		try:
			spaceEntity = BigWorld.entities[ spaceBase.id ]
		except:
			DEBUG_MSG( "not find the spaceEntity!" )
			
		try:
			killer = BigWorld.entities[ killerID ]
		except KeyError:
			DEBUG_MSG( "not find the Entity! %i" % killerID )
			killer = None
			
		if spaceEntity and spaceEntity.isReal():
			spaceEntity.getScript().onKillMonster( spaceEntity, False )
		elif spaceBase:
			spaceBase.cell.remoteScriptCall( "onKillMonster", ( False, ) )