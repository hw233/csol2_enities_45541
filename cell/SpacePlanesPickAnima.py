# -*- coding: gb18030 -*-
from SpacePlanes import SpacePlanes

import Const
REPEAT_HAS_ADDITION_TIME = 5.0	#�ظ�ʰȡ�мӳ�ʱ��
REPEAT_REWARD_POTENTIAL = 2

class SpacePlanesPickAnima( SpacePlanes ):
	"""
	���˵�ͼ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpacePlanes.__init__( self )
	
	def onTriggerTrap( self, planesID, pickRole, pickTime, rewardPotential ):
		"""
		define method
		��¼����ݷ������ʱ��
		"""
		self.pickAnimaData.pickAnima( planesID, pickRole, pickTime, rewardPotential )
	
	def resertAddition( self, planesID, role ):
		"""
		define method.
		ȥ��ĳλ���ʰȡ�ӳɵ���״̬
		"""
		self.pickAnimaData.resertAddition( planesID, role )
		role.client.pickAnima_triggerZhaDan()
	
	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpacePlanes.onEnter( self, baseMailbox, params )
		baseMailbox.client.pickAnima_enterSpace()
		baseMailbox.cell.systemCastSpell( Const.ACTIVITY_STOP_MOVE_SKILL ) #�����һ������BUFF
	
	def onGameOver( self, planesID, role ):
		"""
		define method.
		��Ϸ����,���Ž�������ʱû�н�������
		"""
		r = self.pickAnimaData.getPlanesRecord( planesID )
		if r:
			role.client.pickAnima_overReport( len( r.pickAnimaList ), r.potentialCount)