# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
import csdefine
import csconst
from Monster import Monster

class TDBattleMonster( Monster ):
	"""
	��ħ��ս����
	"""
	def receiveDamage( self, selfEntity, casterID, skillID, damageType, damage ):
		"""
		virtual method.
		�����˺���
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
			if earg != "MAILBOX" :		# һ�㲻����mailbox
				player = eOwner
		
		if not player:
			return
		
		changeDamage = min( selfEntity.HP, damage )
		BigWorld.globalData[ "TaoismAndDemonBattleMgr" ].recordDamageData( selfEntity.className, player.getCamp(), player.base, player.getName(), player.level, player.tongName, changeDamage )
		
	def onChangeTarget( self, selfEntity, oldEnemyID ):
		"""
		virtual method
		Ŀ��ı�
		"""
		target = BigWorld.entities.get( selfEntity.targetID )
		if target and target.getEntityType() == csdefine.ENTITY_TYPE_ROLE: 
			target.addFightMonster( selfEntity.id )
			
		oldTarget = BigWorld.entities.get( oldEnemyID )
		if oldTarget and oldTarget.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
			oldTarget.removeFightMonster( selfEntity.id )
			
	def onStateChanged( self, selfEntity, old, new ):
		"""
		״̬�л���
			@param old	:	������ǰ��״̬
			@type old	:	integer
			@param new	:	�����Ժ��״̬
			@type new	:	integer
		"""
		if new == csdefine.ENTITY_STATE_FREE and self.isBoss( selfEntity ):
			BigWorld.globalData[ "TaoismAndDemonBattleMgr" ].onBossChangeFree( selfEntity.className )
		
	def onMonsterDie( self, selfEntity, killerID ):
		"""
		virtual method.

		����������ش���
		"""
		if self.isBoss( selfEntity ):
			BigWorld.globalData[ "TaoismAndDemonBattleMgr" ].onBossDie( selfEntity.className )
		Monster.onMonsterDie( self, selfEntity, killerID )
		
	def isBoss( self, selfEntity ):
		"""
		��boss��
		"""
		return selfEntity.className in [ csconst.TDB_BOSS_CLASSNAME_T, csconst.TDB_BOSS_CLASSNAME_D ]
