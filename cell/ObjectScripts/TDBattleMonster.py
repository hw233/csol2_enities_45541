# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
import csdefine
import csconst
from Monster import Monster

class TDBattleMonster( Monster ):
	"""
	仙魔论战怪物
	"""
	def receiveDamage( self, selfEntity, casterID, skillID, damageType, damage ):
		"""
		virtual method.
		接受伤害。
		"""
		entity = BigWorld.entities.get( casterID )
		if not entity:
			return
		
		player = None
		entityType = entity.getEntityType()
		if entityType == csdefine.ENTITY_TYPE_ROLE:
			player = entity
		elif entityType == csdefine.ENTITY_TYPE_PET:
			owner = entity.getOwner()
			earg, eOwner = owner.etype, owner.entity
			if earg != "MAILBOX" :		# 一般不会是mailbox
				player = eOwner
		
		if not player:
			return
		
		changeDamage = min( selfEntity.HP, damage )
		BigWorld.globalData[ "TaoismAndDemonBattleMgr" ].recordDamageData( selfEntity.className, player.getCamp(), player.base, player.getName(), player.level, player.tongName, changeDamage )
		
	def onChangeTarget( self, selfEntity, oldEnemyID ):
		"""
		virtual method
		目标改变
		"""
		target = BigWorld.entities.get( selfEntity.targetID )
		if target and target.getEntityType() == csdefine.ENTITY_TYPE_ROLE: 
			target.addFightMonster( selfEntity.id )
			
		oldTarget = BigWorld.entities.get( oldEnemyID )
		if oldTarget and oldTarget.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
			oldTarget.removeFightMonster( selfEntity.id )
			
	def onStateChanged( self, selfEntity, old, new ):
		"""
		状态切换。
			@param old	:	更改以前的状态
			@type old	:	integer
			@param new	:	更改以后的状态
			@type new	:	integer
		"""
		if new == csdefine.ENTITY_STATE_FREE and self.isBoss( selfEntity ):
			BigWorld.globalData[ "TaoismAndDemonBattleMgr" ].onBossChangeFree( selfEntity.className )
		
	def onMonsterDie( self, selfEntity, killerID ):
		"""
		virtual method.

		怪物死亡相关处理
		"""
		if self.isBoss( selfEntity ):
			BigWorld.globalData[ "TaoismAndDemonBattleMgr" ].onBossDie( selfEntity.className )
		Monster.onMonsterDie( self, selfEntity, killerID )
		
	def isBoss( self, selfEntity ):
		"""
		是boss吗
		"""
		return selfEntity.className in [ csconst.TDB_BOSS_CLASSNAME_T, csconst.TDB_BOSS_CLASSNAME_D ]
