# -*- coding: gb18030 -*-

"""This module implements the Enmity AI.

"""
# $Id: RoleEnmity.py,v 1.51 2008-09-01 03:33:34 zhangyuxing Exp $

"""
用于怪物的仇恨度相关处理
"""

import BigWorld
from bwdebug import *
import csdefine
import csconst
from CombatUnit import CombatUnit
from Resource.Skills.SpellBase.CombatSpell import *
import ECBExtend
import random
import Const
from config.server.BackFireBuffID import Datas as backFireBuffIDs
from Domain_Fight import g_fightMgr

class RoleEnmity( CombatUnit ):
	"An RoleEnmity class."

	def __init__( self ):
		"""
		初始化。
		"""
		self.resist_yuanli_base += 500
		self.resist_lingli_base += 500
		self.resist_tipo_base += 500
		CombatUnit.__init__( self )

	def onAddEnemy( self, enemyID ):
		"""
		extend method.
		"""
		CombatUnit.onAddEnemy( self, enemyID )

		enemy = BigWorld.entities.get( enemyID, None )
		if enemy is not None:
			if enemy.isEntityType( csdefine.ENTITY_TYPE_MONSTER ) and random.random() < BigWorld.globalData["AntiRobotVerify_rate"] and not self.isInAutoFight():
				self.base.triggerAntiRobot()	# 触发验证
		
		self.setTemp( "fight_lastTime_record", BigWorld.time() )

		if self.getState() != csdefine.ENTITY_STATE_FIGHT:
			self.changeState( csdefine.ENTITY_STATE_FIGHT )

		actPet = self.pcg_getActPet()
		if actPet and enemy:												# 如果有出战宠物
			g_fightMgr.buildEnemyRelation( actPet.entity, enemy )


	def onRemoveEnemy( self, entityID ):
		"""
		"""
		# 如果没有怪物或人对我不满且不处于未决状态，那么状态恢复为自由状态
		actPet = self.pcg_getActPet()
		entity = BigWorld.entities.get( entityID )
		if actPet and entity:
			g_fightMgr.breakEnemyRelation( actPet.entity, entity )



	def cureToEnemy( self, entity, cure ):
		"""
		define method.
		告诉所有对我有意见(敌意)的怪物，给指定的Entity加仇恨度，哈哈

		@param entity: 目标entity
		@type  entity: CELL MAILBOX
		@param enmity: 仇恨度
		@type  enmity: INT32
		@return: 无
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		entity = BigWorld.entities[ entity.id ]
		
		for entityID in self.enemyList.keys():
			mon = BigWorld.entities.get( entityID )
			if mon:
				#给怪物加仇恨
				if mon.isEntityType( csdefine.ENTITY_TYPE_MONSTER ):
					mon.addCureList( entity.id, cure )

	def onStateChanged( self, old, new ):
		"""
		状态切换。
			@param old	:	更改以前的状态
			@type old	:	integer
			@param new	:	更改以后的状态
			@type new	:	integer
		"""
		# 先通知底层
		CombatUnit.onStateChanged( self, old, new )
		if new == csdefine.ENTITY_STATE_FIGHT:
			if self.fightTimerID != 0:
				ERROR_MSG("fightTimerID can't be set in fight state!")
				printStackTrace()
				return
			self.fightTimerID = self.addTimer( 1, 1, ECBExtend.FIGHT_TIMER_CBID )
		elif old == csdefine.ENTITY_STATE_FIGHT:
			self.cancel( self.fightTimerID )
			self.fightTimerID = 0
			# 旧的状态是战斗状态，那么就是说怪物不再打我了
			self.resetEnemyList()

	def onSkillCastOver( self, spellInstance, target ):
		"""
		virtual method.
		释放技能完成。

		@param  spellInstance: 技能实例
		@type   spellInstance: SPELL
		@param  target: 技能目标
		@type   target: SkillImplTargetObj
		"""
		if isinstance( spellInstance, CombatSpell ) or ( hasattr( spellInstance, "isMalignant" ) and spellInstance.isMalignant() ):
			self.setTemp( "fight_lastTime_record", BigWorld.time() )
		CombatUnit.onSkillCastOver( self, spellInstance, target )

	def onSkillArriveReceiver( self, spellInstance, receiver ):
		"""
		virtual method.
		技能效果已经到达某个目标

		@param  spellInstance: 技能实例
		@type   spellInstance: SPELL
		@param  receiver: 受到这个技能影响的entity
		@type   receiver: entity
		"""
		CombatUnit.onSkillArriveReceiver( self, spellInstance, receiver )

		className = ""
		if hasattr( receiver, "className" ):
			className = receiver.className
		self.questIncreaseSkillUsed( spellInstance.getID(), className )

		if not receiver.isDestroyed:
			if receiver.isEntityType( csdefine.ENTITY_TYPE_PET ):
				targetID = receiver.getOwner().entity.id
			elif receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				targetID = receiver.id
			elif receiver.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ):
				targetID = receiver.getOwnerID()
			else:
				return

			state = spellInstance.isMalignant()
			self.pkAttackStateCheck( targetID, state )
			#在这里检测是不是结束切磋
			if receiver.popTemp( "QIECUO_END", False ):
				receiver.loseQieCuo()
				actPet = self.pcg_getActPet()
				if actPet:
					pet = actPet.entity
					pet.setActionMode( self.id, csdefine.PET_ACTION_MODE_FOLLOW )
				
	def onFightTimer( self, controllerID, userData ):
		"""
		Timer Callback
		ECBExtend.PK_FIGHT_TIMER_CBID
		在战斗状态每1秒触发一次。
		"""
		eids = []
		fight_lastTime_record = self.queryTemp( "fight_lastTime_record", 0.0 )
		actPet = self.pcg_getActPet()
		if actPet and actPet.etype != "MAILBOX" :					# 能找到出征宠物
			isPetFighting = actPet.entity.getState() == csdefine.ENTITY_STATE_FIGHT
		else:
			isPetFighting = False
			
		if BigWorld.time() - fight_lastTime_record <= Const.FIGHT_CHECK_TIMER or isPetFighting:
			isFighting = True				#判断是否处于战斗状态
		else:
			isFighting = False
			
		for entityID in self.enemyList:
			entity = BigWorld.entities.get( entityID, None )
			if entity == None:
				if entityID != 0:
					DEBUG_MSG( "The entity  %s has Lost" % entityID )
				eids.append( entityID )
				continue

			if isFighting:
				if entity.spaceID != self.spaceID:
					print "The entity %s has leave space form %s" %( entity.id, self.id )
					eids.append( entityID )
			else:
				if entity.utype not in [csdefine.ENTITY_TYPE_MONSTER,csdefine.ENTITY_TYPE_PET] or entity.getState() == csdefine.ENTITY_STATE_FREE:
					eids.append( entityID )
						
		if not isFighting and len(self.enemyList) <= 0:
			self.removeTemp( "fight_lastTime_record" )

		g_fightMgr.breakGroupEnemyRelationByIDs( self, eids )
		
		if len( self.enemyList ) == 0:
			state = self.getState()
			if state != csdefine.ENTITY_STATE_DEAD and len( self.enemyList ) == 0 and state != csdefine.ENTITY_STATE_PENDING and state != csdefine.ENTITY_STATE_QUIZ_GAME:
				self.changeState( csdefine.ENTITY_STATE_FREE )


	def receiveDamage( self, casterID, skillID, damageType, damage ):
		"""
		Define and virtual method.
		接受伤害。
		@param   casterID: 施法者ID
		@type    casterID: OBJECT_ID
		@param    skillID: 技能ID
		@type     skillID: INT
		@param damageType: 伤害类型；see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: INT
		@param     damage: 伤害数值
		@type      damage: INT
		"""
		
		if self.state == csdefine.ENTITY_STATE_DEAD:
			return
		self.clearBuff( [csdefine.BUFF_INTERRUPT_GET_HIT] )
		entity = BigWorld.entities.get( casterID, None )

		if entity is not None:
			self.tempMapping[ "fight_lastTime_record"] = BigWorld.time() 
			
			if entity.utype == csdefine.ENTITY_TYPE_PET :
				owner = entity.getOwner()
				entity = owner.entity
			elif entity.utype == csdefine.ENTITY_TYPE_SLAVE_MONSTER or entity.utype == csdefine.ENTITY_TYPE_VEHICLE_DART :
				entity = BigWorld.entities.get( entity.getOwnerID(), entity )
				
			if damageType & csdefine.DAMAGE_TYPE_FLAG_BUFF != csdefine.DAMAGE_TYPE_FLAG_BUFF:
				self.addDamageList( casterID, damage )
			g_fightMgr.buildEnemyRelation( self, entity )
			if entity.utype == csdefine.ENTITY_TYPE_ROLE :
				if self.isQieCuoTarget( entity.id ):
					self.HP = max( 1, self.HP - damage )
					if self.HP == 1:
						g_fightMgr.breakEnemyRelation( self, entity )
						#切磋结束不能直接调用，否则会导致褐名
						self.setTemp( "QIECUO_END", True )
					return

			self.HP = max( 0, self.HP - damage )

			if self.HP == 0:
				self.MP = 0
				self.die( casterID )
		

# RoleEnmity.py
