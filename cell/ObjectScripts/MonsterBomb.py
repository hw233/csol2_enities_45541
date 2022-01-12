# -*- coding: gb18030 -*-
# $Id: Exp $

from Monster import Monster
import ECBExtend


class MonsterBomb( Monster ):
	"""
	爆炸怪物：支持出生后自曝，死亡后自曝
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		Monster.initEntity( self, selfEntity )
		selfEntity.addTimer( 30.0, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )

	def onMonsterDie( self, selfEntity, killerID ):
		"""
		virtual method.

		死亡事情处理。
		
		"""
		for i in selfEntity.entitiesInRangeExt( 30.0, "Role", selfEntity.position ):
			i.setHP( int( i.HP * 0.85 ) )
		for i in selfEntity.entitiesInRangeExt( 30.0, "Pet", selfEntity.position ):
			i.setHP( int( i.HP * 0.85 ) )

		Monster.onMonsterDie( self, selfEntity, killerID )

	def onDestroySelfTimer( self, selfEntity ):
		"""
		DESTROY_SELF_TIMER_CBID的callback函数；
		"""
		for i in selfEntity.entitiesInRangeExt( 30.0, "Role", selfEntity.position ):
			i.setHP( int( i.HP * 0.85 ) )
		for i in selfEntity.entitiesInRangeExt( 30.0, "Pet", selfEntity.position ):
			i.setHP( int( i.HP * 0.85 ) )