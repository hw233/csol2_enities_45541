# -*- coding: gb18030 -*-

"""This module implements the Enmity AI.

"""
# $Id: RoleEnmity.py,v 1.51 2008-09-01 03:33:34 zhangyuxing Exp $

"""
���ڹ���ĳ�޶���ش���
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
		��ʼ����
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
				self.base.triggerAntiRobot()	# ������֤
		
		self.setTemp( "fight_lastTime_record", BigWorld.time() )

		if self.getState() != csdefine.ENTITY_STATE_FIGHT:
			self.changeState( csdefine.ENTITY_STATE_FIGHT )

		actPet = self.pcg_getActPet()
		if actPet and enemy:												# ����г�ս����
			g_fightMgr.buildEnemyRelation( actPet.entity, enemy )


	def onRemoveEnemy( self, entityID ):
		"""
		"""
		# ���û�й�����˶��Ҳ����Ҳ�����δ��״̬����ô״̬�ָ�Ϊ����״̬
		actPet = self.pcg_getActPet()
		entity = BigWorld.entities.get( entityID )
		if actPet and entity:
			g_fightMgr.breakEnemyRelation( actPet.entity, entity )



	def cureToEnemy( self, entity, cure ):
		"""
		define method.
		�������ж��������(����)�Ĺ����ָ����Entity�ӳ�޶ȣ�����

		@param entity: Ŀ��entity
		@type  entity: CELL MAILBOX
		@param enmity: ��޶�
		@type  enmity: INT32
		@return: ��
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		entity = BigWorld.entities[ entity.id ]
		
		for entityID in self.enemyList.keys():
			mon = BigWorld.entities.get( entityID )
			if mon:
				#������ӳ��
				if mon.isEntityType( csdefine.ENTITY_TYPE_MONSTER ):
					mon.addCureList( entity.id, cure )

	def onStateChanged( self, old, new ):
		"""
		״̬�л���
			@param old	:	������ǰ��״̬
			@type old	:	integer
			@param new	:	�����Ժ��״̬
			@type new	:	integer
		"""
		# ��֪ͨ�ײ�
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
			# �ɵ�״̬��ս��״̬����ô����˵���ﲻ�ٴ�����
			self.resetEnemyList()

	def onSkillCastOver( self, spellInstance, target ):
		"""
		virtual method.
		�ͷż�����ɡ�

		@param  spellInstance: ����ʵ��
		@type   spellInstance: SPELL
		@param  target: ����Ŀ��
		@type   target: SkillImplTargetObj
		"""
		if isinstance( spellInstance, CombatSpell ) or ( hasattr( spellInstance, "isMalignant" ) and spellInstance.isMalignant() ):
			self.setTemp( "fight_lastTime_record", BigWorld.time() )
		CombatUnit.onSkillCastOver( self, spellInstance, target )

	def onSkillArriveReceiver( self, spellInstance, receiver ):
		"""
		virtual method.
		����Ч���Ѿ�����ĳ��Ŀ��

		@param  spellInstance: ����ʵ��
		@type   spellInstance: SPELL
		@param  receiver: �ܵ��������Ӱ���entity
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
			#���������ǲ��ǽ����д�
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
		��ս��״̬ÿ1�봥��һ�Ρ�
		"""
		eids = []
		fight_lastTime_record = self.queryTemp( "fight_lastTime_record", 0.0 )
		actPet = self.pcg_getActPet()
		if actPet and actPet.etype != "MAILBOX" :					# ���ҵ���������
			isPetFighting = actPet.entity.getState() == csdefine.ENTITY_STATE_FIGHT
		else:
			isPetFighting = False
			
		if BigWorld.time() - fight_lastTime_record <= Const.FIGHT_CHECK_TIMER or isPetFighting:
			isFighting = True				#�ж��Ƿ���ս��״̬
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
		�����˺���
		@param   casterID: ʩ����ID
		@type    casterID: OBJECT_ID
		@param    skillID: ����ID
		@type     skillID: INT
		@param damageType: �˺����ͣ�see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: INT
		@param     damage: �˺���ֵ
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
						#�д��������ֱ�ӵ��ã�����ᵼ�º���
						self.setTemp( "QIECUO_END", True )
					return

			self.HP = max( 0, self.HP - damage )

			if self.HP == 0:
				self.MP = 0
				self.die( casterID )
		

# RoleEnmity.py
