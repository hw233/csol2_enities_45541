# -*- coding: gb18030 -*-
# $Id: Exp $

from Monster import Monster
import ECBExtend


class MonsterBomb( Monster ):
	"""
	��ը���֧�ֳ��������أ�����������
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		Monster.initEntity( self, selfEntity )
		selfEntity.addTimer( 30.0, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )

	def onMonsterDie( self, selfEntity, killerID ):
		"""
		virtual method.

		�������鴦��
		
		"""
		for i in selfEntity.entitiesInRangeExt( 30.0, "Role", selfEntity.position ):
			i.setHP( int( i.HP * 0.85 ) )
		for i in selfEntity.entitiesInRangeExt( 30.0, "Pet", selfEntity.position ):
			i.setHP( int( i.HP * 0.85 ) )

		Monster.onMonsterDie( self, selfEntity, killerID )

	def onDestroySelfTimer( self, selfEntity ):
		"""
		DESTROY_SELF_TIMER_CBID��callback������
		"""
		for i in selfEntity.entitiesInRangeExt( 30.0, "Role", selfEntity.position ):
			i.setHP( int( i.HP * 0.85 ) )
		for i in selfEntity.entitiesInRangeExt( 30.0, "Pet", selfEntity.position ):
			i.setHP( int( i.HP * 0.85 ) )