# -*- coding: gb18030 -*-


import BigWorld
import csdefine
from Monster import Monster
from bwdebug import *
import ECBExtend




class ToxinFrogBoss( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		
	def onStateChanged( self, selfEntity, old, new ):
		"""
		״̬�л���
			@param old	:	������ǰ��״̬
			@type old	:	integer
			@param new	:	�����Ժ��״̬
			@type new	:	integer
		"""
		if new == csdefine.ENTITY_STATE_FREE:
			if old == csdefine.ENTITY_STATE_FIGHT:
				#className = selfEntity.query( "talkNPC_className", 0 )
				BigWorld.globalData[ "ToxinFrogMgr" ].onBossExitFight( selfEntity.spawnMB )
				selfEntity.resetEnemyList()
				selfEntity.popTemp( "ToxinFrog_bootyOwner" )
				selfEntity.addTimer( 0.2, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )

	def dieNotify( self, selfEntity, killerID ):
		"""
		����֪ͨ����selfEntity��die()������ʱ������
		"""
		Monster.dieNotify( self, selfEntity, killerID )
		BigWorld.globalData[ "ToxinFrogMgr" ].onBossDie( selfEntity.spawnMB )

	def getBootyOwner( self, selfEntity ):
		"""
		���ս��Ʒ��ӵ���ߣ�
		�����֪�����ص�ӵ�����Ƿ��ж��飬��Ҫ�Լ�ȥ����ӵ���ߵĶ��������
		�������0���ʾû��ӵ���ߣ�������ز���0���Լ�ӵ�ж��飬��ô����ֵӦ����ָ��ӳ���teamMailbox's entityID��

		@return: tuple of Entity ID --> (ӵ����ID, ӵ���߶ӳ�ID)������ֻ�����һ��,ӵ����ID���ȣ�����Ϊ0��ʾ�����˶����Լ�
		@rtype:  TUPLE OF OBJECT_ID
		"""
		bootyOwner = selfEntity.queryTemp( "ToxinFrog_bootyOwner", () )
		if bootyOwner: return bootyOwner
		return Monster.getBootyOwner( self, selfEntity )
		