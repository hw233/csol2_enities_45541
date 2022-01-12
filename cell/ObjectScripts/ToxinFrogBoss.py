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
		状态切换。
			@param old	:	更改以前的状态
			@type old	:	integer
			@param new	:	更改以后的状态
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
		死亡通知；当selfEntity的die()被触发时被调用
		"""
		Monster.dieNotify( self, selfEntity, killerID )
		BigWorld.globalData[ "ToxinFrogMgr" ].onBossDie( selfEntity.spawnMB )

	def getBootyOwner( self, selfEntity ):
		"""
		获得战利品的拥有者；
		如果想知道返回的拥有者是否有队伍，需要自己去检查该拥有者的队伍情况；
		如果返回0则表示没有拥有者；如果返回不是0且自己拥有队伍，那么它的值应该是指向队长的teamMailbox's entityID。

		@return: tuple of Entity ID --> (拥有者ID, 拥有者队长ID)，两者只会出现一个,拥有者ID优先，两者为0表示所有人都可以捡；
		@rtype:  TUPLE OF OBJECT_ID
		"""
		bootyOwner = selfEntity.queryTemp( "ToxinFrog_bootyOwner", () )
		if bootyOwner: return bootyOwner
		return Monster.getBootyOwner( self, selfEntity )
		