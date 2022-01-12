# -*- coding: gb18030 -*-
#
# $Id: PetAI.py,v 1.43 2008-08-29 07:09:42 qilan Exp $

"""
This module implements the pet entity.

2007/12/11 : wirten by huangyongwei
"""

import BigWorld
import Math
import csarithmetic
import csdefine
import csconst
import csstatus
import Const
import ECBExtend
import time
import utils
from bwdebug import *
from Function import Functor
from PetFormulas import formulas
from CombatUnit import CombatUnit
from AmbulantObject import AmbulantObject
from SkillTargetObjImpl import createTargetObjEntity
from Resource.SkillLoader import g_skills
from Domain_Fight import g_fightMgr


CONTROL_BORN		= 0												# ����Ȩ״̬������մ���
CONTROL_GIVE_OUT	= 1												# ����Ȩ״̬���Ѿ���������Ȩ
CONTROL_TAKE_BACK	= 2												# ����Ȩ״̬���Ѿ��ջؿ���Ȩ

class PetAI( CombatUnit, AmbulantObject ) :
	def __init__( self ) :
		self.resist_yuanli_base += 500
		self.resist_lingli_base += 500
		self.resist_tipo_base += 500
		AmbulantObject.__init__( self )
		CombatUnit.__init__( self )
		# ���û�м��ܿ���������ʼ�������
		for idx in xrange( csconst.QB_PET_ITEM_COUNT - len( self.__qbItems ) ) :
			defItem = { "skillID" : 0 , "autoUse" : 0 }				# Ĭ�ϵĿ�ݸ���Ϣ
			self.__qbItems.append( defItem )					 	# ��ʼ����ݸ�Ϊָ������
		self.__isForceFollow = False								# ��ʱ����Ƿ�ǿ�ȸ���
		self.__autoAttackTimerID = 0								# �Զ����� timer ID
		self.__isAutoAttack = False									# �Զ��������
		self.__chaseEntityID = 0									# ��¼chaseEntityʧ�ܲ���doRandomRun�ɹ�ʱ��׷�ٵ�Ŀ��ID
		self.__chaseFlatRange = 0.0									# ��¼chaseEntityʧ�ܲ���doRandomRun�ɹ�ʱ������׷��Ŀ���Զʱ��Ϊ���CELL_PRIVATE
		self.__controlPowerStatus = CONTROL_GIVE_OUT				# ��¼����Ȩ��״̬

#	# ������� ------------------------------------------------------
	# ----------------------------------------------------------------
	def actionThinking_( self ) :
		"""
		������Ϊ���ƺ������� Pet �е��������ã�
		"""
		if self.isDead(): return								# ����Ѿ��������򲻽����κζ���
		if self.__teleportDetect(): return						# �Ƿ���Ҫ����
		if self.__forceFollowDetect(): return					# �Ƿ񳬳���ǿ�ȸ��淶Χ
		if self.__fightingDetect(): return						# ս�����
		if self.__normalFollowDetect(): return					# ��ͨ״̬���

	def __teleportDetect( self ):
		"""�������Ƿ���Ҫ���͵�������"""
		# ���ڴ�����
		if self.queryTemp("owner_controlled_before_teleport"):
			return True
		# ��һ��ʱ��Ž�����ת���
		if self.tickCount % Const.PET_TELEPORT_DETECT_CONTROL != 0:
			return False
		# ��ȡ����
		owner = BigWorld.entities.get( self.ownerID, None )			# ��ȡ������ɫ
		if owner is None :											# ���������ɫ�Ѿ����� entities ��
			self.notifyDefOwner_( "pcg_teleportPet" )				# ����ת
			return True												# ���� True �ػ� tick
		# ���ڵ�ͼ���
		if owner.spaceID != self.spaceID :							# ���������������ɫ��ͬ��һ�� space
			self.teleportToOwner()
			return True
		# ������
		if self.__distTo(owner.position) >= csconst.PET_FORCE_TELEPORT_RANGE:
			self.teleportToOwner()
			return True
		return False

	def __forceFollowDetect( self ):
		"""����Ƿ���Ҫǿ�Ƹ�������"""
		if not self.selfControlled():								# @<FOR_CLIENT_CONTROL>
			return False
		if self.tickCount % Const.PET_FOLLOW_DETECT_CONTROL != 0:	# ��һ��ʱ��Ž���ǿ�ȸ������
			return False
		if self.actionMode == csdefine.PET_ACTION_MODE_KEEPING:		# �����ͣ��״̬���򲻽���ǿ�Ƹ���
			return False
		try:
			owner = BigWorld.entities[self.ownerID]					# ��ȡ����
		except KeyError:
			INFO_MSG("May be pet(id:%i) stays different cellapp from owner(id:%i)"%(self.id, self.ownerID))
			return False
		if self.__distTo(owner.position) > csconst.PET_FORCE_FOLLOW_RANGE:
			self.__forceFollowEntity(owner, csconst.PET_ROLE_KEEP_DISTANCE-1.0)	# ����ǿ�ȸ�����룬���ｫ��ǿ�ȸ����ɫ
			return True
		else:
			return False

	def __fightingDetect( self ):
		"""
		ս�����
		"""
		if self.isAttacking(): 										# �����ǰ����ս�����򷵻� True�����Ա� tick
			if not self.selfControlled():							# @<FOR_CLIENT_CONTROL>
				target = BigWorld.entities.get(self.targetID)
				if not self.__enemyIsValid(target):
					self.setTargetID(0)
			return True
		elif self.tussleMode == csdefine.PET_TUSSLE_MODE_PASSIVE:	# ����״̬��ִ�й���
			if self.enemyList:
				self.__findAndCleanEnemy()							# ������Ч����
			return False
		else:
			enemy = self.__findNextEnemy()							# ������һ��Ŀ��
			if enemy:
				if self.selfControlled():							# @<FOR_CLIENT_CONTROL>
					self.__autoAttackEnemy(enemy)
				else:
					self.setTargetID(enemy.id)						# @<FOR_CLIENT_CONTROL>
				return True
			else:
				return False

	def __normalFollowDetect( self ):
		"""
		��ͨ������
		"""
		if not self.selfControlled():								# @<FOR_CLIENT_CONTROL>
			return False
		elif self.actionMode == csdefine.PET_ACTION_MODE_KEEPING:	# �����ͣ��״̬
			return self.__backToKeepPoint()							# ��ص�ͣ����
		elif self.chaseEntityID == 0:								# ���û�и���Ŀ��
			return self.__forceFollowOwner()						# ��ǿ�Ƹ�������
		else:
			return False

#	# utils ----------------------------------------------------------
	# ----------------------------------------------------------------
	def __distTo( self, position ):
		"""
		��position�ľ���
		"""
		return self.position.distTo(position)

	def __enemyIsValid( self, enemy ):
		"""
		������Ч�Լ�飬�������Ƿ����Ϊһ��
		��Ч�Ĺ�����������������Ŀ�������Ч��
		"""
		if enemy is None :
			return False
		elif enemy.spaceID != self.spaceID :
			return False
		elif self.__distTo(enemy.position) > csconst.ROLE_AOI_RADIUS :
			return False
		elif enemy.state == csdefine.ENTITY_STATE_DEAD :
			return False
		return True

	def __entityAttackable( self, entity ):
		"""
		entity �Ƿ���Թ�������������޵�buff
		��Ŀ����ǲ��ܹ����ģ�������Ȼ��������Ч
		�ĵ��ˣ����޵�buffȥ���ˣ����ֿ��Թ�����
		"""
		if getattr(entity, "state", csdefine.ENTITY_STATE_DEAD) == csdefine.ENTITY_STATE_DEAD:
			# �����ģ�����û��state���Ե�entity����Ϊ���ɹ���
			return False
		elif entity.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ) and\
			entity.getEntityType() != csdefine.ENTITY_TYPE_ROLE:		# Ӧ�ÿ��ǽ���Щ��Ǽӵ�queryRelation�ж���
				return False
		elif entity.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ):			# Ӧ�ÿ��ǽ���Щ��Ǽӵ�queryRelation�ж���
			pid, tid = entity.ownerVisibleInfos							# ownerVisibleInfos����ָ�����ü�����һ��߶���
			if pid != self.ownerID:										# �����˲��ɼ�
				teamMailbox = self.getTeamMailbox()
				if teamMailbox is None or tid != teamMailbox.id:		# �����ڵĶ���Ҳ���ɼ�
					return False										# ���ܹ���
		return self.queryRelation(entity) == csdefine.RELATION_ANTAGONIZE

	def __clearEnemyList( self ):
		"""
		��յ����б�
		"""
		g_fightMgr.breakGroupEnemyRelationByIDs( self, self.enemyList.keys() )


	def __setAutoAttack( self, auto ):
		"""
		�����Զ��������
		"""
		if self.__isAutoAttack != auto:
			self.__isAutoAttack = auto

#	# fighting -------------------------------------------------------
	# ----------------------------------------------------------------
	def addEnemyCheck( self, entityID ):
		"""
		extend method.
		"""
		if not CombatUnit.addEnemyCheck( self, entityID ):
			return False

		if entityID == self.ownerID :
			return False

		return True


	def onAddEnemy( self, entityID ):
		"""
		extend method.
		"""
		CombatUnit.onAddEnemy( self, entityID )

		if entityID == 0:												# entityID��0��������Ƿ�ֹͬһ��tick��ν��롢�˳�ս�������⴦����ϸ�뿴CombatSpell.py
			return

		if not self.selfControlled():							# �����ǰ�����ڹ���״̬��Ҳ������ǿ�ȸ�������״̬ @<FOR_CLIENT_CONTROL>
			return

		if self.isAttacking():
			return

		if self.__isForceFollow:
			return

		if self.tussleMode == csdefine.PET_TUSSLE_MODE_PASSIVE :
			return

		enemy = BigWorld.entities.get(entityID, None)
		if not enemy:
			INFO_MSG("May be pet(id:%i) stays different cellapp from enemy(id:%i)."%(self.id, entityID))
			return

		self.__autoAttackEnemy( enemy )							# �򣬶��¼ӵ��˷�������


	def __findAndCleanEnemy( self ) :
		"""
		˳������б��ҵ���һ����Ч�ҿɹ����ĵ��ˣ�
		�����ڼ����������Ч�����Ƴ�
		"""
		for enemyID, atime in self.enemyList.items() :
			enemy = BigWorld.entities.get( enemyID, None )
			if self.__enemyIsValid(enemy):
				if self.__entityAttackable(enemy):
					return enemy
			elif enemy is None:
				g_fightMgr.removeEnemyByID(self, enemyID)
			else:
				g_fightMgr.breakEnemyRelation(self, enemy)
		return None

	def __scentClosestEnemy( self, position, range ):
		"""
		��position��Χ��������ĵ���
		"""
		entities = self.entitiesInRangeExt( range, None, position )
		entities.sort( key = lambda e : e.position.distTo( position ) )	# ���������ɫ�ľ�������
		for entity in entities :
			if self.__entityAttackable(entity):
				return entity
		return None

	def __scentEnemy( self ) :
		"""
		����һ������
		"""
		try:
			owner = BigWorld.entities[self.ownerID]
		except KeyError:
			INFO_MSG("May be pet(id:%i) stays different cellapp from owner(id:%i),stop scenting."\
				%(self.id, self.ownerID))
			return None
		basePos = owner.position
		if self.actionMode == csdefine.PET_ACTION_MODE_KEEPING :
			basePos = self.__keepPosition
		return self.__scentClosestEnemy(basePos, csconst.PET_ENMITY_RANGE)

	def __findNextEnemy( self ):
		"""
		��ȡ��һ������Ŀ��
		"""
		enemy = self.__findAndCleanEnemy()							# ����ѡȡ�����б���ĵ���
		if enemy is not None:
			return enemy
		elif self.selfControlled() and\
			self.tussleMode == csdefine.PET_TUSSLE_MODE_ACTIVE:		# �������������ģʽ		@<FOR_CLIENT_CONTROL>
				return self.__scentEnemy()							# ���Զ�Ѱ����Χ�ĵ���
		else:
			return None

	def __castEnemyOrChase( self, skillID, enemy ):
		"""
		�Ե���ʩչ���ܣ���������̫Զ��׷��Ŀ�꣬
		���ʩչ�ɹ�����һ�ι�������onSkillCastOver
		����
		"""
		self.setTargetID(enemy.id)									# ���ù���Ŀ��
		state = self.spellTarget(skillID, enemy.id)					# ʩչ����
		if state == csstatus.SKILL_TOO_FAR:
			if self.selfControlled():								# ����Ƿ���������		@<FOR_CLIENT_CONTROL>
				spell = g_skills[skillID]
				if self.checkAndChase(enemy, spell.getRangeMax(self)):
					self.__tmpSpellID = skillID						# ����ʹ�õļ���ID
				else:
					state = csstatus.PET_CAN_NOT_CHASE
		elif state == csstatus.SKILL_GO_ON:
			if enemy.state != csdefine.ENTITY_STATE_DEAD:			# �������û�б���ɱ
				self.changeState( csdefine.ENTITY_STATE_FIGHT )		# ����Ϊ����ս��״̬
		else:
			self.setTargetID(0)										# ����ʧ�ܣ��Ƴ�Ŀ��
		return state

	def __spellEnemy( self, skillID, enemy ):
		"""ʹ�ü��ܹ�������"""
		state = self.__castEnemyOrChase(skillID, enemy)
		return state == csstatus.SKILL_TOO_FAR or state == csstatus.SKILL_GO_ON

	def __autoSpellEnemy( self, enemy ):
		"""�Զ�ѡ�ü��ܹ�������"""
		# �ȳ���ʹ���Զ�ս�����еļ���
		for qbSkill in self.__qbItems:
			if not qbSkill["autoUse"] or not qbSkill["skillID"]:
				continue
			if self.__spellEnemy(qbSkill["skillID"], enemy):
				return True
		# ����ʹ����ͨ������
		skillID = csconst.PET_SKILL_ID_PHYSICS_MAPS.get( self.getPType(), 0 )
		return self.__spellEnemy(skillID, enemy)

	def __autoAttackEnemy( self, enemy ) :
		"""
		�����Զ�������ǿ�ȸ���͹����ǻ���ģ����
		������﹥�����ͻ�ȡ��ǿ�ȸ��棬�������ǿ
		�ȸ��棬�Ͳ��ܽ��й���
		"""
		if self.__isForceFollow : return							# �������ǿ�ȸ��棬�򲻽��й���
		self.__setAutoAttack(True)									# �����Զ��������
		if not self.__autoSpellEnemy(enemy):						# �������ʧ��
			self.__setNextAttackTimer(self.hit_speed)				# ���˲��ɹ���������������ص�

	def __autoAttackCurrentTarget( self ):
		"""������ǰ��Ŀ��"""
		try:
			target = BigWorld.entities[self.targetID]				# ��ȡĿ��
		except KeyError:
			INFO_MSG("May be pet(id:%i) stays different cellapp from target(id:%i),stop attacking target."\
				%(self.id, self.targetID))
			self.setTargetID(0)										# ����Ϊ��ǰû�й���Ŀ�꣬�ȴ���һ��tick
			return
		if self.__entityAttackable(target):							# ���Ŀ��ɹ���
			if self.selfControlled():								# @<FOR_CLIENT_CONTROL>
				self.__autoAttackEnemy(target)
		else:
			self.setTargetID(0)										# ����Ϊ��ǰû�й���Ŀ�꣬�ȴ���һ��tick

	def __setAutoAttackTimer( self, cbTime ) :
		"""
		�����Զ�����ʱ��
		"""
		# ����Timer�Ļص�������onPetAttackTimer
		self.__cancelAutoAttackTimer()
		self.__autoAttackTimerID = self.addTimer( cbTime, 0, ECBExtend.PET_ATTACK_CBID )

	def __setNextAttackTimer( self, time ):
		"""
		������һ�ι�����timer
		"""
		if self.intonating() :										# �������ʩ��
			self.__setAutoAttackTimer(self.hit_speed)				# ��������ʱ�ӣ��ȴ���һ�� tick
		elif self.isMoving() :										# ��������ƶ�
			self.__setAutoAttackTimer(self.hit_speed)				# ��������ʱ�ӣ��ȴ���һ�� tick
		else:
			self.__setAutoAttackTimer(time)							# ����ʱ��

	def __setMinAttackTimer( self ):
		"""
		���öԵ�ǰĿ�����һ�ι���timer
		"""
		try:
			target = BigWorld.entities[self.targetID]				# ��ȡĿ��
		except KeyError:
			INFO_MSG("May be pet(id:%i) stays different cellapp from target(id:%i),stop attacking target."\
				%(self.id, self.targetID))
			DEBUG_MSG("attacking: %s, has enemy: %s, callbacking: %s, force following: %s, moving: %s"%\
				(self.isAttacking(), len(self.enemyList), self.__autoAttackTimerID != 0, self.__isForceFollow,\
				self.isMoving()))
			self.__setNextAttackTimer(self.hit_speed)
			return
		self.__setNextAttackTimer(self.__minSpellInterval(target))

	def __minSpellInterval( self, enemy ) :
		"""
		��ȡ�´ο��ü��ܵ���С���
		"""
		skillID = csconst.PET_SKILL_ID_PHYSICS_MAPS.get( self.getPType(), 0 )
		normalSpell = g_skills[skillID]								# ��ȡ��ͨ������ spell
		minVal = normalSpell.getMaxCooldown( self )					# ��ȡ��ʹ����ͨ������ʱ��
		hitDelay = self.hitDelay - BigWorld.time()					# ��ȡ�����ӳ�
		if hitDelay > 0 :											# ȡ��ģ���ֹCD���˻��й����ӳ٣�����ͬ���޷�ʩ��
			minVal = max( minVal, time.time() + hitDelay )

		for qbSkill in self.__qbItems:
			if not qbSkill["autoUse"] or not qbSkill["skillID"]:
				continue
			state = self.__spellTargetCheck(qbSkill["skillID"], enemy)
			if state != csstatus.SKILL_NOT_READY : continue			# ���������Ϊ����CD���޷�ʩ�ŵģ�����
			timeVal = g_skills[qbSkill["skillID"]].getMaxCooldown( self )	# ��ȡ��ʹ�øü��ܵ�ʱ��
			if timeVal != 0 :
				minVal = min( minVal, timeVal )						# ��ȡ��С�Ŀ��ü���ʱ��

		return max( minVal - time.time(), 0.1 )

	def __cancelAutoAttackTimer( self ) :
		"""
		�ر��Զ�����ʱ��
		"""
		if self.__autoAttackTimerID > 0 :
			self.cancel( self.__autoAttackTimerID )
			self.__autoAttackTimerID = 0

	def __spellTargetCheck( self, skillID, target ):
		"""����skillID�͹���Ŀ���ȡ��Ӧ�ļ���ʵ����ת�����Ŀ��ʵ��
		��ʩչ״̬"""
		spell = g_skills[skillID]										# ��ȡ��Ӧ����
		tcobj = spell.getCastObject().convertCastObject( self, target )	# ��������п���ֻ�ܶ��Լ��ͷ�
		tcobj = createTargetObjEntity( tcobj )							# ��װ����ʩչ����
		if self.intonating():
			return csstatus.SKILL_INTONATING
		if self.inHomingSpell():
			return csstatus.SKILL_CANT_CAST
		return spell.useableCheck(self, tcobj)

#	# following ------------------------------------------------------
	# ----------------------------------------------------------------
	def __forceFollowOwner( self ) :
		"""
		ǿ�ȸ�������
		"""
		try:
			owner = BigWorld.entities[self.ownerID]					# ��ȡ����
		except KeyError:
			INFO_MSG("May be pet(id:%i) stays different cellapp from owner(id:%i),stop force follow."\
				%(self.id, self.ownerID))
			return False
		keepDistance = csconst.PET_ROLE_KEEP_DISTANCE
		if self.__distTo(owner.position) > keepDistance :
			return self.__forceFollowEntity( owner, keepDistance-1.0 )
		else:
			return True

	def __forceFollowEntity( self, entity, flatRange ):
		"""
		ǿ�Ƹ���ָ����Ŀ��
		@param entity : �����Ŀ��
		@param flatRange : ����׷��Ŀ���Զʱ��Ϊ����
		"""
		if self.chaseEntityID == entity.id:
			return True												# �����ǰ�Ѿ����ڸ����У��򷵻�
		self.stopMoving()											# ����ǿ��ֹͣ��ǰ�ƶ���Ϊ
		self.stopAttacking()										# ǿ��ֹͣ��ǰ������Ϊ
		if self.checkAndChase( entity, flatRange ):					# ׷��Ŀ��
			self.__isForceFollow = True
			return True
		else:
			return False

	def __backToKeepPoint( self ):
		"""
		�ص�ͣ����
		"""
		self.stopMoving()											# ��ֹͣ�ƶ�
		if self.__distTo(self.__keepPosition) <= 0.1:
			return False
		elif self.actionSign( csdefine.ACTION_FORBID_MOVE ):
			return False
		else:
			self.gotoPosition( self.__keepPosition )
			return True

	def __setKeepPosition( self, position ):
		"""
		����ͣ��λ�ã���֪ͨ�ͻ���
		"""
		if self.__keepPosition != position:
			self.__keepPosition = position
			self.notifyMyClient_("onSetKeepPosition", position)		# @<FOR_CLIENT_CONTROL>

#	# public ---------------------------------------------------------
	# -------------------------------------------------
	# ׷�ٸ���
	# -------------------------------------------------
	def chaseTarget( self, entity, flatRange ):
		"""
		׷��һ��entity
		ע��: AmbulantObject���chaseEntity��petAI�㲻��ֱ��ʹ�ã�pet׷��һ��Ŀ��Ӧ��ʹ�ñ��ӿ�
		@param   entity: ��׷�ϵ�Ŀ��
		@type    entity: Entity
		@param flatRange: ��Ŀ��entity��Զ�ľ���ͣ����
		@type  flatRange: FLOAT
		@return: ���ش˴νӿڵ����Ƿ�ɹ�
		@rtype:  BOOL
		"""
		if self.chaseEntity( entity, flatRange ):					# �ȳ���׷��
			self.__chaseEntityID = 0
			self.__chaseFlatRange = 0.0
			return True
		elif self.doRandomRun( entity.position, flatRange ):		# �ٳ����ߵ�Ŀ��㸽�����λ��
			DEBUG_MSG("Can't chase entity(id:%i), doRandomRun."%entity.id)
			self.__chaseEntityID = entity.id
			self.__chaseFlatRange = flatRange
			return True
		else:
			DEBUG_MSG("Can't chase entity(id:%i), also not doRandomRun."%entity.id)
			return False

	def checkAndChase( self, entity, flatRange ):
		"""����Ƿ����׷��Ŀ�꣬�����ԣ���׷��
		@param entity		: ׷��Ŀ��
		@param flatRange	: �ھ���Ŀ���Զ�ķ�Χ����Ϊ�ǵ�����Ŀ�ĵ�
		"""
		if self.actionSign( csdefine.ACTION_FORBID_MOVE ):
			DEBUG_MSG( "I can not move! ID:%d" % self.id )
			return False
		elif not self.selfControlled():								# @<FOR_CLIENT_CONTROL>
			DEBUG_MSG( "I(id:%d) am not self controlled." % self.id )
			return False
		else:
			return self.chaseTarget( entity, flatRange )

	def stopMoving( self ):
		"""
		Overwrited from AmbulantObject
		ֹͣ�ƶ������ø÷��������ᴥ��onChaseOver
		"""
		AmbulantObject.stopMoving(self)
		self.__isForceFollow = False
		if not self.selfControlled():								# @<FOR_CLIENT_CONTROL>
			self.openVolatileInfo()									# @<FOR_CLIENT_CONTROL>

	def onMovedOver( self, success ) :
		"""
		gotoPosition �Ļص�����ǰ�Ĳ��������chaseEntityʧ�ܣ�
		������doRandomRun�ƶ���Ŀ��㸽�����ɹ����ټ���׷��
		Ŀ��
		"""
		if self.__chaseEntityID != 0:
			try:
				en = BigWorld.entities[self.__chaseEntityID]
				self.checkAndChase( en, self.__chaseFlatRange )		# go on chasing Target
			except:
				self.__chaseEntityID = 0

	def onChaseOver( self, entity, success ) :
		"""
		chaseEntity �Ļص�
		��Ҫ���ǵ���׷�ٹ��̻���ս�������У�׷��Ŀ��
		״̬�����ı䵼���޷��������������޷�������Ϊ
		���Թ��������
		"""
		AmbulantObject.onChaseOver( self, entity, success )
		if entity and self.__tmpSpellID:							# �������׷��Ŀ��
			if self.__entityAttackable(entity):
				self.__castEnemyOrChase(self.__tmpSpellID, entity)	# ����Ŀ��ɹ��������������Ŀ��
			else:
				self.setTargetID(0)									# ��������Ϊû�й���Ŀ�꣬�ȴ���һ��tick
		else:
			if self.isAttacking():
				self.stopAttacking()								# ���׷��ʧ�ܻ���û�й������ܣ���ֹͣ����
			if self.selfControlled():								# @<FOR_CLIENT_CONTROL>
				if self.actionMode == csdefine.PET_ACTION_MODE_KEEPING:
					self.__backToKeepPoint()
				elif not self.__forceFollowOwner():					# �������ͣ��״̬����ǿ�Ƹ�������
					self.teleportToOwner()							# ���ǿ�Ƹ�������ʧ�ܣ����͵����˴�

	def teleportToOwner( self ):
		"""���͵��������"""
		try:
			owner = BigWorld.entities[self.ownerID]					# ��ȡ������ɫ
		except KeyError:
			INFO_MSG("May be pet(id:%i) stays different cellapp from owner(id:%i)"%(self.id, self.ownerID))
			self.notifyDefOwner_( "pcg_teleportPet" )				# ����ת
			return
		pos = formulas.getPosition( owner.position, owner.yaw )		# ��������λ��
		if self.spaceID == owner.spaceID:							# Ŀ����⣬��ֹ���ﴫ���ص���
			properPos = self.canNavigateTo(pos)
			if properPos:
				pos = properPos
		pos = utils.navpolyToGround(owner.spaceID, pos, 5.0, 5.0)	# ȡ�����ϵĵ�
		self.teleportToEntity(owner.spaceID, owner, pos, owner.direction)	# ע�⣬���������һ��ghost���������Զ�̵���

	def teleportToEntity( self, spaceID, entityMB, position, direction ):
		"""
		<Defined method>
		���͵�entity���ڿռ�
		"""
		if self.isAttacking() : self.stopAttacking()				# ֹͣ����
		self.stopMoving()											# ֹͣ�κ��ƶ�
		if self.actionMode == csdefine.PET_ACTION_MODE_KEEPING :	# �����תǰ�����ﴦ��ͣ��״̬
			self.__setKeepPosition(position)
		self.onBeforeTeleport( spaceID, position )					# ֪ͨ�ص�
		if self.spaceID == spaceID:
			self._teleport(spaceID, None, position, direction)		# ͬ��ͼ��ת����ɫ���
		else:
			self._teleport(spaceID, entityMB, position, direction)	# ��ͬ��ͼ��ת����ɫ���

	def _teleport( self, spaceID, entityMB, position, direction ):
		"""
		����
		"""
		if self.selfControlled():
			self.teleport( entityMB, position, direction )
			self.teleportOver()
		else:
			prev_tid = self.queryTemp("teleport_timerID")			# �ر��ϴεĴ���
			if prev_tid:
				self.cancel(prev_tid)
			self.takeBackControlPower()
			self.setTemp("owner_controlled_before_teleport", True)
			self.setTemp("teleport_args", (entityMB, position, direction))
			tid = self.addTimer(1.0, 0.0, ECBExtend.PET_TELEPORT_CBID)			# �ص�������onTeleportTimer
			self.setTemp("teleport_timerID", tid)

	def onTeleportTimer( self, timerID, userData ):
		"""
		����timer����
		"""
		tid = self.popTemp("teleport_timerID")
		if tid != timerID:
			ERROR_MSG("Unknown timerID %s callback, expected %s"%(timerID, tid))
		else:
			# BIGWORD_ERROR:���ݲ��Խ��������������timer�ص�ʱ����entity�Ļ����ص����ٴ���һ��
			# Ϊ��ֹ���ֲ���Ԥ�ϵ�������ڻص��󣬴���֮ǰ�����ֶ�ȡ��timer
			self.cancel(tid)
		args = self.popTemp("teleport_args")
		if args is None:
			ERROR_MSG("Got invalid teleport args of %s" % args)
			self.removeTemp("owner_controlled_before_teleport")
		else:
			self.teleport(*args)
			self.teleportOver()

	def teleportOver( self ):
		"""
		<Defined method>
		������ɻص�
		"""
		if self.popTemp("owner_controlled_before_teleport", False):
			self.giveControlToOwner()
		else:
			self.openVolatileInfo()

	def setKeepPosition( self, srcEntityID, position ):
		"""
		<Exposed method>
		�ͻ�������ͣ��λ��
		"""
		if self.hackVerify_(srcEntityID):
			if self.selfControlled():
				INFO_MSG("Pet(%i) is self controlled currently, client(%i) sets keep position is not allowed."\
					%(self.id, srcEntityID))
			else:
				self.__setKeepPosition(position)
		else:
			WARNING_MSG("Client cheat detected! id is %s" % srcEntityID)

	# ------------------------------------------------
	# ����
	# ------------------------------------------------
	def attackTarget( self, srcEntityID, enemyID, skillID ) :
		"""
		<Exposed method>
		������﹥��Ŀ��Ŀͻ��˿��Žӿ�
		"""
		if not self.hackVerify_( srcEntityID ) : return				# �������������ɫ����������

		if skillID in csconst.SKILL_ID_PHYSICS_LIST:
			if enemyID == self.targetID and\
				not self.hitDelayOver():							# ��������ͬһ��Ŀ��Ĺ��������鹥����ʱ����ֹ���ƹ����ٶȹ���
					return
		elif skillID not in self.attrSkillBox:						# ���ʹ�õļ��ܲ��ڳ��＼���б���
			HACK_MSG( "The pet(id:%i) dosen't has skill %i!" % (self.id, skillID))
			return

		if self.intonating() :										# �������ʩ�������������ΪʲôҪ��������������
			self.statusMessage( csstatus.SKILL_INTONATING )			# ��ȡ�����ι�������
			return

		enemy = BigWorld.entities.get( enemyID, None )
		if enemy is None or enemy.spaceID != self.spaceID :			# ���Ŀ�겻���ڣ�������ﲻͬһ�� space
			self.statusMessage( csstatus.SKILL_TARGET_NOT_EXIST )
			return

		try:
			owner = BigWorld.entities[self.ownerID]
		except KeyError:
			INFO_MSG("May be pet(id:%i) stays different cellapp from owner(id:%i),stop attacking."\
				%(self.id, self.ownerID))
			return

		distance = owner.position.distTo(enemy.position)
		if distance >= csconst.PET_FORCE_TELEPORT_RANGE or\
			distance >= csconst.PET_FORCE_FOLLOW_RANGE:				# �������Ŀ�����������ɫ�����˳����ǿ�ȸ���������ǿ�ȴ��;���
			self.statusMessage( csstatus.PET_SPELL_TOOL_FAR )		# �򣬾ܾ���������Ϊ�뿪�˸þ��룬����ʼ��Ҫǿ�Ȼص�������ɫ��ߵ�
		elif self.__entityAttackable(enemy):						# ����ǿɹ���Ŀ��
			self.__setAutoAttack(True)								# ���������Զ�ս�������Ϊ��������ڽ��еĹ���ѭ�����Է�һ�����ι���ʧ�ܣ�����Ͳ��ٽ��й���
			state = self.__castEnemyOrChase(skillID, enemy)
			if (state != csstatus.SKILL_GO_ON and state != csstatus.SKILL_TOO_FAR):
				if state == csstatus.SKILL_OUTOF_MANA:
					state = csstatus.SKILL_PET_OUTOF_MANA
				self.statusMessage( state )
			self.setTargetID(enemyID)								# ǿ�ƽ�����Ŀ������Ϊ��Ŀ��
		else:
			self.statusMessage( csstatus.SKILL_TARGET_CANT_FIGHT )


	def onRemoveEnemy( self, entityID ):
		"""
		"""
		if len( self.enemyList ) == 0:
			self.enterFreeState()

	def setTargetID( self, targetID ):
		"""���ó����Ŀ��"""
		if self.targetID != targetID:
			self.targetID = targetID

	def isAttacking( self ) :
		"""
		�Ƿ�����ս����
		"""
		return self.targetID != 0

	def isAutoAttacking( self ) :
		"""
		�Ƿ����Զ�������
		"""
		return self.__isAutoAttack

	def stopAttacking( self ) :
		"""
		ֹͣ��ǰս��
		"""
		if self.attrIntonateSkill :									# �������ʩ��
			self.interruptSpell( csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 )# ��ֹͣʩ��
		self.setTargetID(0)											# �������Ŀ��
		self.__setAutoAttack(False)									# �ر��Զ�������־
		self.__cancelAutoAttackTimer()								# �ر��Զ�����ʱ��
		self.__tmpSpellID = 0										# �������

	def enterFreeState( self ):
		"""
		��������״̬
		"""
		self.stopAttacking()										# ֹͣ��ǰս��
		self.__clearEnemyList()										# ��յ����б�
		if self.state != csdefine.ENTITY_STATE_DEAD and\
			self.state != csdefine.ENTITY_STATE_PENDING:			# ������ﻹû��������û��δ��״̬
				self.changeState( csdefine.ENTITY_STATE_FREE )		# �򣬸�Ϊ����״̬

	def onPetAttackTimer( self, timerID, cbid ) :
		"""
		�Զ����� timer
		"""
		self.__autoAttackCurrentTarget()

	def receiveDamage( self, casterID, skillID, damageType, damage ):
		"""
		Define and virtual method.
		�����˺���
		@param			casterID   : ʩ����ID
		@type			casterID   : OBJECT_ID
		@param			skillID	   : ����ID
		@type			skillID	   : INT
		@param			damageType : �˺����ͣ�see also csdefine.py/DAMAGE_TYPE_*
		@type			damageType : INT
		@param			damage	   : �˺���ֵ
		@type			damage	   : INT
		"""
		CombatUnit.receiveDamage( self, casterID, skillID, damageType, damage )
		try : caster = BigWorld.entities[casterID]
		except : caster = None

		if caster and caster.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = caster.getOwner()
			if owner.etype !="MAILBOX" :
				caster = owner.entity

		if caster and not caster.state == csdefine.ENTITY_STATE_DEAD:
			if not self.state == csdefine.ENTITY_STATE_DEAD and (damageType & csdefine.DAMAGE_TYPE_FLAG_BUFF == csdefine.DAMAGE_TYPE_FLAG_BUFF):
				return
			self.addDamageList( casterID, damage )

	def onSkillCastOver( self, spellInstance, target ) :
		"""
		virtual method.
		�ͷż�����ɡ�

		@param  spellInstance: ����ʵ��
		@type   spellInstance: SPELL
		@param  target: ����Ŀ��
		@type   target: SkillImplTargetObj
		"""
		CombatUnit.onSkillCastOver( self, spellInstance, target )
		if self.selfControlled():									#@<FOR_CLIENT_CONTROL>
			if self.isAutoAttacking() :								# ��������Զ�����
				self.__setMinAttackTimer()
		else:
			self.__setNextAttackTimer(self.hit_speed)				#@<FOR_CLIENT_CONTROL>

	def onSpellInterrupted( self ):
		"""
		���⼼�ܱ�����ж��Զ�ս��timer
		"""
		CombatUnit.onSpellInterrupted( self )
		self.__setNextAttackTimer( 1.5 )

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
			self.getOwner().entity.pkAttackStateCheck( targetID, state )

			#���������ǲ��ǽ����д�
			if receiver.popTemp( "QIECUO_END", False ):
				qiecuoTarget = BigWorld.entities.get( receiver.id )
				if qiecuoTarget:
					g_fightMgr.breakEnemyRelation( self, qiecuoTarget )
				receiver.loseQieCuo()
				self.setActionMode( self.ownerID, csdefine.PET_ACTION_MODE_FOLLOW )

	# ------------------------------------------------
	# ���ܿ����
	# ------------------------------------------------
	def requestQBItems( self, srcEntityID ) :
		"""
		<Exposed/>
		�����ܿ����
		"""
		self.notifyClient_( "pcg_onInitPetQBItems", self.__qbItems )

	def updateQBItem( self, srcEntityID, index, qbItem ) :
		"""
		<Exposed/>
		���¿����
		"""
		if not self.hackVerify_( srcEntityID ) : return
		skillID = qbItem["skillID"]
		if skillID and skillID not in self.attrSkillBox :
			HACK_MSG( "pet dosen't contain skill: %i!" )
		else :
			try :
				self.__qbItems[index] = qbItem
				self.notifyClient_( "pcg_onUpdatePetQBItem", index, qbItem )
			except IndexError :
				HACK_MSG( "index '%i' out of quick items' max range '%i'" % ( index, len( self.__qbItems ) ) )

	def autoAddQBItem( self, skillID ):
		"""
		�¼Ӽ��ܣ��Զ��������õ��������
		"""
		for e in self.__qbItems:
			if e["skillID"] == 0:	# ����ҵ��յģ�����õ���������������
				e["skillID"] = skillID
				e["autoUse"] = 1
				self.notifyClient_( "pcg_onInitPetQBItems", self.__qbItems )		# ���¿ͻ��˿����
				break

	def removeSkill( self, skillID ):
		"""
		�Ƴ�һ�����ܣ�ɾ����صĿ��������
		"""
		for qbItem in self.__qbItems:
			if qbItem["skillID"] == skillID:
				qbItem["skillID"] = 0
				qbItem["autoUse"] = 0
				return

	def onUpdateSkill( self, oldSkillID, newSkillID ) :
		"""
		�����ܸ���ʱ������
		"""
		for qbItem in self.__qbItems :
			if oldSkillID == qbItem["skillID"] :						# ����ɵļ��� ID �ڿ���б���
				qbItem["skillID"] = newSkillID							# ����ζ�ż�������, ��˽��ɼ��ܸ���Ϊ�µȼ��ļ���
		self.notifyClient_( "pcg_onInitPetQBItems", self.__qbItems )	# ���¿ͻ��˿����

	# -------------------------------------------------
	# ģʽ����
	# -------------------------------------------------
	def setActionMode( self, srcEntityID, mode ) :
		"""
		<Exposed/>
		������Ϊģʽ
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if mode not in [ \
			csdefine.PET_ACTION_MODE_FOLLOW, \
			csdefine.PET_ACTION_MODE_KEEPING] :
				HACK_MSG( "error motion! from %i" % srcEntityID )
				return
		if mode == csdefine.PET_ACTION_MODE_FOLLOW :
			self.__forceFollowOwner()								# ǿ�ȳ���ص���ɫ���
		elif mode == csdefine.PET_ACTION_MODE_KEEPING :
			self.__setKeepPosition(Math.Vector3(self.position))
			if self.isMoving():
				self.stopMoving()
			if self.isAttacking():
				self.stopAttacking()
		self.actionMode = mode
		self.baseOwner.pcg_setActionMode( mode )

	def setTussleMode( self, srcEntityID, mode ) :
		"""
		<Exposed/>
		����ս��ģʽ
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.removeTemp("Snake_buff")
		if mode not in [ \
			csdefine.PET_TUSSLE_MODE_ACTIVE, \
			csdefine.PET_TUSSLE_MODE_PASSIVE, \
			csdefine.PET_TUSSLE_MODE_GUARD] :
				HACK_MSG( "error tussle! from %i" % srcEntityID )
				return
		self.tussleMode = mode
		self.baseOwner.pcg_setTussleMode( mode )
		if mode == csdefine.PET_TUSSLE_MODE_PASSIVE:
			if self.isAttacking():
				self.stopAttacking()
			if self.selfControlled():								#@<FOR_CLIENT_CONTROL>
				if self.actionMode == csdefine.PET_ACTION_MODE_KEEPING:
					self.__backToKeepPoint()
				else:
					self.__forceFollowOwner()

	# ------------------------------------------------
	# others
	# ------------------------------------------------
	def onDestroy( self ) :
		"""
		�����ٵ�ʱ����������
		"""
		self.enterFreeState()
		self.stopMoving()
		self.takeBackControlPower()		# controlledBy��ΪNoneʱ���ͻ��˲������ٳ���

	def getDaoheng( self ):
		# ��ȡ�������ֵ
		return self.wuxue / 2.0

	def onStateChanged( self, old, new ):
		"""
		״̬�л���
		@param			old : ������ǰ��״̬
		@type			old : integer
		@param			new : �����Ժ��״̬
		@type			new : integer
		"""
		CombatUnit.onStateChanged( self, old, new )
		# �߼���˵������Ӧ������Ϊֹͣ��ս�����ܽ�������״̬��
		# ��������Ϊ����������״̬���Ծ�Ҫֹͣս�������ﻹ��
		# �����Ϊ���ݴ���
		if new == csdefine.ENTITY_STATE_DEAD :
			if self.isMoving():
				self.stopMoving()
			if self.isAttacking():
				self.enterFreeState()
		elif new == csdefine.ENTITY_STATE_FREE :
			if self.isAttacking():
				self.stopAttacking()

	def effectStateChanged( self, estate, disabled ):
		"""
		Ч���ı�.
		@param estate		:	Ч����ʶ(�����)
		@type estate		:	integer
		@param disabled		:	Ч���Ƿ���Ч
		@param disabled		:	bool
		"""
		if self.effect_state & csdefine.EFFECT_STATE_PROWL :		# ����ʱ ����������������״̬
			if self.tussleMode == csdefine.PET_TUSSLE_MODE_ACTIVE:
				self.setTemp( "Snake_buff", csdefine.PET_TUSSLE_MODE_ACTIVE )
				self.tussleMode = csdefine.PET_TUSSLE_MODE_GUARD

#	# client control -------------------------------------------------
	def selfControlled( self ):
		"""
		������Ϊ�Ƿ����Լ��ڿ���
		"""
		#return self.controlledBy == None
		return self.__controlPowerStatus != CONTROL_GIVE_OUT

	def onClientReady( self, srcEntityID ):
		"""
		<Exposed method>
		�ͻ���׼������
		"""
		if self.hackVerify_(srcEntityID):
			if self.__controlPowerStatus != CONTROL_TAKE_BACK:
				self.giveControlToOwner()
			else:
				INFO_MSG("Control powner is taken back currently")
		else:
			WARNING_MSG("Client cheat detected! id is %s" % srcEntityID)

	def giveControlToOwner( self ):
		"""
		������Ȩ��������
		"""
		self.openVolatileInfo()
		# ��ֹ�첽����£��Ѿ����ù�controlledBy���ǿͻ���û���յ���
		# ���ſͻ����ٴ��������Ȩ�������������Ѿ����ù��������ٴ�
		# ������Ч�����������������ΪNone�����������ÿ���Ȩ
		#self.controlledBy = None
		#self.controlledBy = self.baseOwner
		self.notifyMyClient_("onClientControlled", True)
		self.__controlPowerStatus = CONTROL_GIVE_OUT

	def takeBackControlPower( self ):
		"""
		ȡ�ؿ���Ȩ
		"""
		if not self.selfControlled():
			#self.controlledBy = None
			self.notifyMyClient_("onClientControlled", False)
			self.__controlPowerStatus = CONTROL_TAKE_BACK

#	# synchronise position ---------------------------------
	def synchronisePositionFromClient( self, srcEntityID, position ):
		"""
		<Exposed method>
		"""
		if not self.hackVerify_(srcEntityID):
			return
		if not self.selfControlled():
			self.rotateToPos(position)
			self.position = position
