# -*- coding: gb18030 -*-

import csstatus
import csdefine
import csconst
import BigWorld
import keys
import Timer
import utils
import skills as g_skills
from Time import Time
from bwdebug import *
from PetFormulas import formulas
from PetNavigate import PetNavigator, PetChaser
from SkillTargetObjImpl import createTargetObjEntity
from navigate import NavDataMgr


class PetAI:

	def __init__( self ):
		self.navigator = None
		self.hitDelay = 0.0
		self.__tmpSpellID = 0
		self.__forceChasing = False
		self.__autoAttackTimerID = 0
		self.__keepPosition = self.position
		self.__heartBeatTimer = None
		self.__clientControlled = False
		self.isCharging = False

#	# ������� ------------------------------------------------------
	# ---------------------------------------------------------------
	def __onHeartBeat( self ):
		"""
		��������
		"""
		if not self.clientControlled():return
		elif self.__teleportDetect():return
		elif self.__fightingDetect():return
		elif self.__followDetect():return

	def __teleportDetect( self ):
		"""�������Ƿ���Ҫ���͵�������"""
		# ��ȡ����
		owner = BigWorld.entities.get( self.ownerID, None )			# ��ȡ������ɫ
		if owner and owner.spaceID == self.spaceID and\
			self.__distTo(owner.position) >= (csconst.PET_FORCE_TELEPORT_RANGE - 2):
				self.teleportToOwner()
				return True
		return False

	def __fightingDetect( self ):
		"""
		ս�����
		"""
		if self.__forceChasing:
			return False
		elif self.tussleMode == csdefine.PET_TUSSLE_MODE_PASSIVE:
			self.stopAttacking()
			return False
		elif self.targetID != 0:
			if not self.isAttacking():
				self.__autoAttackCurrentTarget()
			return True
		elif self.tussleMode == csdefine.PET_TUSSLE_MODE_ACTIVE:
			enemy = self.__scentEnemy()
			if enemy:
				self.__autoAttackEnemy(enemy)
				return True
		return False

	def __followDetect( self ):
		"""
		��ͨ�������
		"""
		if self.__forceChasing:
			return False
		elif self.actionMode == csdefine.PET_ACTION_MODE_KEEPING:	# �����ͣ��״̬
			return self.backToKeepPoint()							# ��ص�ͣ����
		else:														# ���û�и���Ŀ��
			return self.followOwner()								# ���������

	def resumeHeartBeat( self ):
		"""��������"""
		self.cancelHeartBeat()
		self.__heartBeatTimer = Timer.addTimer( 1.0, 1.0, self.__onHeartBeat )

	def cancelHeartBeat( self ):
		"""ֹͣ����"""
		if self.__heartBeatTimer is not None:
			Timer.cancel( self.__heartBeatTimer )
			self.__heartBeatTimer = None

#	# utils ----------------------------------------------------------
	# ----------------------------------------------------------------
	def __distTo( self, position ):
		"""
		��position�ľ���
		"""
		return self.position.distTo(position)

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

#	# fighting -------------------------------------------------------
	# ----------------------------------------------------------------
	def __castEnemyOrChase( self, skillID, enemy ):
		"""
		�Ե���ʩչ���ܣ���������̫Զ��׷��Ŀ�꣬
		���ʩչ�ɹ�����һ�ι�������onSkillCastOver
		����
		"""
		state = self.__spellTargetCheck(skillID, enemy)				# ʩչ����
		if state == csstatus.SKILL_TOO_FAR:
			if self.clientControlled():
				spell = g_skills.getSkill(skillID)
				if self.checkAndChase(enemy, spell.getRangeMax(self)-0.5, self.onHuntPursueOver):
					self.__tmpSpellID = skillID						# ����ʹ�õļ���ID
					self.__forceChasing = True
				else:
					state = csstatus.PET_CAN_NOT_CHASE
			else:
				self.cell.attackTarget( enemy.id, skillID )
		elif state == csstatus.SKILL_GO_ON:
			self.cell.attackTarget( enemy.id, skillID )
			if self.clientControlled():
				self.setHitDelay(self.hit_speed)					# ��¼������ʱ
		return state

	def __spellEnemy( self, skillID, enemy ):
		"""ʹ�ü��ܹ�������"""
		if self.isCharging: return False
		state = self.__castEnemyOrChase(skillID, enemy)
		return state == csstatus.SKILL_TOO_FAR or state == csstatus.SKILL_GO_ON

	def __autoSpellEnemy( self, enemy ):
		"""�Զ�ѡ�ü��ܹ�������"""
		# �ȳ���ʹ���Զ�ս�����еļ���
		for qbSkill in BigWorld.player().pcg_getQBItems():
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
		self.__autoSpellEnemy(enemy)
		self.__setMinAttackTimer()									# �ɹ��Ե���ʩչ����������һ�´λص�

	def __autoAttackCurrentTarget( self ):
		"""������ǰ��Ŀ��"""
		try:
			target = BigWorld.entities[self.targetID]				# ��ȡĿ��
		except KeyError:
			INFO_MSG("Pet(id:%i) client can't find target(id:%i),stop attacking target."\
				%(self.id, self.targetID))
			self.stopAttacking()
			return
		if self.__entityAttackable(target):							# ���Ŀ��ɹ���
			self.__autoAttackEnemy(target)
		else:
			self.stopAttacking()

	def __onAutoAttackCallback( self ):
		"""�Զ������ص�����"""
		if self.__forceChasing:										# �������ǿ�ȸ��棬�򲻽��й���
			if self.targetID != 0:
				self.__setMinAttackTimer()
			elif self.isAttacking():
				self.__cancelAutoAttackTimer()
		else:
			self.__autoAttackCurrentTarget()

	def __spellTargetCheck( self, skillID, target ):
		"""����skillID�͹���Ŀ���ȡ��Ӧ�ļ���ʵ����ת�����Ŀ��ʵ��
		��ʩչ״̬"""
		spell = g_skills.getSkill(skillID)								# ��ȡ��Ӧ����
		tcobj = spell.getCastObject().convertCastObject( self, target )	# ��������п���ֻ�ܶ��Լ��ͷ�
		tcobj = createTargetObjEntity( tcobj )							# ��װ����ʩչ����
		return spell.useableCheck(self, tcobj)

	# ------------------------------------------------
	# scant enemy
	# ------------------------------------------------
	def __scentClosestEnemy( self, position, range ):
		"""
		��position��Χ��������ĵ���
		"""
		entities = self.entitiesInRange( range, lambda e: self.__entityAttackable(e), position )
		#entities.sort( key = lambda e : e.position.distTo( position ) )	# ���������ɫ�ľ�������
		enemy = None
		distance = range + 10
		for entity in entities :
			d = entity.position.distTo(position)
			if d < distance:
				distance = d
				enemy = entity
		return enemy

	def __scentEnemy( self ) :
		"""
		����һ������
		"""
		basePos = BigWorld.player().position
		if self.actionMode == csdefine.PET_ACTION_MODE_KEEPING :
			basePos = self.__keepPosition
		return self.__scentClosestEnemy(basePos, csconst.PET_ENMITY_RANGE)

	# ------------------------------------------------
	# set attack timer
	# ------------------------------------------------
	def __setAutoAttackTimer( self, cbTime ) :
		"""
		�����Զ�����ʱ��
		"""
		self.__cancelAutoAttackTimer()
		self.__autoAttackTimerID = BigWorld.callback(cbTime, self.__onAutoAttackCallback)

	def __setNextAttackTimer( self, time ):
		"""
		������һ�ι�����timer
		"""
		#if self.intonating() :										# �������ʩ��
		#	self.__setAutoAttackTimer(self.hit_speed)				# ��������ʱ�ӣ��ȴ���һ�� tick
		#elif self.isMoving() :										# ��������ƶ�
		#	self.__setAutoAttackTimer(self.hit_speed)				# ��������ʱ�ӣ��ȴ���һ�� tick
		#else:
		self.__setAutoAttackTimer(time)								# ����ʱ��

	def __setMinAttackTimer( self ):
		"""
		���öԵ�ǰĿ�����һ�ι���timer
		"""
		try:
			target = BigWorld.entities[self.targetID]				# ��ȡĿ��
		except KeyError:
			INFO_MSG("Pet(id:%i) client can't find target(id:%i),stop attacking target."\
				%(self.id, self.targetID))
			self.__setNextAttackTimer(self.hit_speed)
			return
		self.__setNextAttackTimer(self.__minSpellInterval(target))

	def __minSpellInterval( self, enemy ) :
		"""
		��ȡ�´ο��ü��ܵ���С���
		"""
		skillID = csconst.PET_SKILL_ID_PHYSICS_MAPS.get( self.getPType(), 0 )
		normalSpell = g_skills.getSkill( skillID )					# ��ȡ��ͨ������ spell
		minVal = normalSpell.getCooldownData( self )[1]				# ��ȡ��ʹ����ͨ������ʱ��
		if self.hitDelay > Time.time():								# ȡ��ģ���ֹCD���˻��й����ӳ٣�����ͬ���޷�ʩ��
			minVal = max( minVal, self.hitDelay )

		for qbSkill in BigWorld.player().pcg_getQBItems():
			if not qbSkill["autoUse"] or not qbSkill["skillID"]:
				continue
			state = self.__spellTargetCheck(qbSkill["skillID"], enemy)
			if state != csstatus.SKILL_NOT_READY : continue			# ���������Ϊ����CD���޷�ʩ�ŵģ�����
			spell = g_skills.getSkill(qbSkill["skillID"])
			timeVal = spell.getCooldownData(self)[1]				# ��ȡ��ʹ�øü��ܵ�ʱ��
			if timeVal != 0 :
				minVal = min( minVal, timeVal )						# ��ȡ��С�Ŀ��ü���ʱ��

		return max( minVal - Time.time(), 0.1 )

	def __cancelAutoAttackTimer( self ) :
		"""
		�ر��Զ�����ʱ��
		"""
		if self.__autoAttackTimerID > 0 :
			BigWorld.cancelCallback( self.__autoAttackTimerID )
			self.__autoAttackTimerID = 0

	# ------------------------------------------------
	# public
	# ------------------------------------------------
	def attackTarget( self, enemy, skillID ) :
		"""
		������﹥��Ŀ��Ŀͻ��˿��Žӿ�
		"""
		owner = BigWorld.player()
		if enemy.id == self.targetID and\
			not self.hitDelayOver():								# ��������ͬһ��Ŀ��Ĺ��������鹥����ʱ����ֹ���ƹ����ٶȹ���
				return
		elif skillID not in csconst.SKILL_ID_PHYSICS_LIST and \
			skillID not in owner.pcg_getPetSkillList():				# ���ʹ�õļ��ܲ��ڳ��＼���б���
				HACK_MSG( "The pet(id:%i) dosen't has skill %i!" % (self.id, skillID))
				return

		if self.intonating() :										# �������ʩ�������������ΪʲôҪ��������������
			self.statusMessage( csstatus.SKILL_INTONATING )			# ��ȡ�����ι�������
			return

		distance = owner.position.distTo(enemy.position)
		if distance >= csconst.PET_FORCE_TELEPORT_RANGE or\
			distance >= csconst.PET_FORCE_FOLLOW_RANGE:				# �������Ŀ�����������ɫ�����˳����ǿ�ȸ���������ǿ�ȴ��;���
			self.statusMessage( csstatus.PET_SPELL_TOOL_FAR )		# �򣬾ܾ���������Ϊ�뿪�˸þ��룬����ʼ��Ҫǿ�Ȼص�������ɫ��ߵ�
		elif self.__entityAttackable(enemy):						# ����ǿɹ���Ŀ��
			state = self.__castEnemyOrChase(skillID, enemy)
			if (state != csstatus.SKILL_GO_ON and state != csstatus.SKILL_TOO_FAR):
				if state == csstatus.SKILL_OUTOF_MANA:
					state = csstatus.SKILL_PET_OUTOF_MANA
				self.statusMessage( state )
		else:
			self.statusMessage( csstatus.SKILL_TARGET_CANT_FIGHT )

	def onTargetChanged( self, old ):
		"""
		����Ŀ��ı�
		"""
		if self.clientControlled():
			if self.targetID != 0:
				if not self.__forceChasing:
					self.__autoAttackCurrentTarget()

	def isAttacking( self ) :
		"""
		�Ƿ�����ս����
		"""
		return self.__autoAttackTimerID != 0

	def stopAttacking( self ):
		"""ֹͣս��"""
		self.__cancelAutoAttackTimer()

	def setHitDelay( self, delay ):
		"""
		��¼�����ӳ�
		"""
		self.hitDelay = Time.time() + delay

	def hitDelayOver( self ):
		"""
		������ʱ�Ƿ����
		"""
		return Time.time() > self.hitDelay

#	# following ------------------------------------------------------
	# ----------------------------------------------------------------
	def initPhysics( self ):
		"""
		��ʼ��physics��ֻ���ɿͻ��˿��Ƶ�entity�ž���physics���ԣ�
		BigWorld.controlEntity����ʵ�ֿ���һ�����ͻ���entity
		��cell��entity��Ҫ����cellEntity��controlledByΪbaseMailbox
		"""
		if self.clientControlled():
			self.physics = keys.SIMPLE_PHYSICS
			self.physics.fall = True
			self.physics.collide = False
		else:
			TRACE_MSG( "Only controlled entities have a 'physics' attribute,maybe controlledBy hasnot init" )

	def followOwner( self ):
		"""
		��������
		"""
		owner = BigWorld.player()
		if self.actionSign(csdefine.ACTION_FORBID_MOVE):
			return False
		elif self.position.distTo( owner.position ) <= csconst.PET_ROLE_KEEP_DISTANCE:
			return False
		else:
			# //�޷�ͨ��Ѱ·������ң�ֱ�Ӵ�����ҵ�ǰ����λ�� csol-2080
			if not NavDataMgr.instance().canNavigateTo( self.position, owner.position ):
				self.navigator.teleportPosition( owner.position )
			elif not NavDataMgr.instance().canNavigateTo( owner.position, self.position ):
				self.navigator.teleportPosition( owner.position )
			elif not self.navigator.isFollowing():
				self.navigator.followEntity( owner, csconst.PET_ROLE_KEEP_DISTANCE, self.chaseSpeed() )
			return True

	def forcePursueOwner( self ):
		"""ǿ�Ƹ�������"""
		owner = BigWorld.player()
		if self.isCharging: return
		if not self.actionSign(csdefine.ACTION_FORBID_MOVE):
			# //�޷�ͨ��Ѱ·������ң�ֱ�Ӵ�����ҵ�ǰ����λ�� csol-2080
			if not NavDataMgr.instance().canNavigateTo( self.position, owner.position ):
				self.navigator.teleportPosition( owner.position )
			elif not NavDataMgr.instance().canNavigateTo( owner.position, self.position ):
				self.navigator.teleportPosition( owner.position )
			else:
				self.__forceChasing = True
				self.navigator.chaseEntity( owner, csconst.PET_ROLE_KEEP_DISTANCE, self.chaseSpeed(), self.onForcePursueOver )

	def cancelFollow( self ):
		"""
		ֹͣ����
		"""
		if self.navigator.isFollowing():
			self.navigator.stop()

	def teleportToOwner( self ):
		"""
		���ϴ��͵��������
		"""
		if self.clientControlled():
			self.stopAttacking()
			self.stopMove()
			owner = BigWorld.player()
			dstPos = formulas.getPosition( owner.position, owner.yaw )
			dstPos = utils.posOnGround(owner.spaceID, dstPos, default=owner.position)
			self.navigator.teleportPosition(dstPos)

			self.setFilterYaw(owner.yaw)
			BigWorld.callback(0, self.restartFilterMoving)
			if self.actionMode == csdefine.PET_ACTION_MODE_KEEPING :	# �����תǰ�����ﴦ��ͣ��״̬
				self.cell.setKeepPosition(dstPos)						# ֪ͨ�������ı�ͣ��λ��

	def backToKeepPoint( self ):
		"""
		�ص�ͣ����
		"""
		if not self.clientControlled():								# �����ɿͻ����������ƶ�
			DEBUG_MSG( "I can not controlled by client! ID:%d" % self.id )
			return False
		elif self.actionSign( csdefine.ACTION_FORBID_MOVE ):
			DEBUG_MSG( "I can not move! ID:%d" % self.id )
			return False
		elif self.isCharging:
			DEBUG_MSG( "I am in charging! ID:%d" % self.id )
			return False
		else:
			self.stopMove()
			if self.__distTo(self.__keepPosition) > 1.0:
				self.navigator.chasePosition(self.__keepPosition, 1.0, self.chaseSpeed())
			return True

	def checkAndChase( self, entity, flatRange, callback = lambda o, t, r: None ):
		"""����Ƿ����׷��Ŀ�꣬�����ԣ���׷��
		@param entity		: ׷��Ŀ��
		@param flatRange	: �ھ���Ŀ���Զ�ķ�Χ����Ϊ�ǵ�����Ŀ�ĵ�
		"""
		if not self.clientControlled():								# �����ɿͻ����������ƶ�
			DEBUG_MSG( "I can not controlled by client! ID:%d" % self.id )
			return False
		elif self.actionSign( csdefine.ACTION_FORBID_MOVE ):
			DEBUG_MSG( "I can not move! ID:%d" % self.id )
			return False
		elif self.__distTo(entity.position) > flatRange:
			self.pursueEntity( entity, flatRange, callback )
			return True
		else:
			return False

	def pursueEntity( self, entity, nearby, callback = lambda o, t, r: None ):
		"""
		pursue entity
		@type		entity			  : instance
		@param		entity			  : entity you want to pursue
		@type		nearby			  : float
		@param		nearby			  : move to the position nearby target
		@type		callback		  : �ص�����
		@param		callback		  : ������������һ����׷����, һ����׷��Ŀ�꣬һ����׷�ٽ��
		@return						  : None
		"""
		self.navigator.chaseEntity( entity, nearby, self.chaseSpeed(), callback )

	def onHuntPursueOver( self, owner, target, success ):
		"""
		׷��һ��Ŀ�����
		"""
		self.__forceChasing = False
		if target and self.__tmpSpellID:
			if BigWorld.entities.has_key(target.id):						# �������׷��Ŀ��
				if self.__entityAttackable(target):
					self.__castEnemyOrChase(self.__tmpSpellID, target)		# ����Ŀ��ɹ��������������Ŀ��
					self.__setMinAttackTimer()								# ���ù���timer
				else:
					self.__setAutoAttackTimer(self.hit_speed)				# ���ù���timer
			else:
				INFO_MSG("Pet(id:%i) client can't find target(id:%i),stop attacking target."\
					%(self.id, target.id))
				if self.isAttacking():
					self.stopAttacking()
		else:
			INFO_MSG("Pet(id:%i) client chase target(%s) over, with spell %s."\
				%(self.id, target.id if target else target, self.__tmpSpellID))

	def onForcePursueOver( self, owner, target, success ):
		"""ǿ�Ƹ��浽��"""
		self.__forceChasing = False

	def isMoving( self ):
		"""�Ƿ������ƶ�"""
		return self.navigator.isMoving()

	def isForceChasing( self ):
		"""�Ƿ�����ǿ��׷��"""
		return self.__forceChasing

	def stopMove( self ) :
		"""
		ֹͣ�ƶ�
		"""
		self.__forceChasing = False
		self.navigator.stop()
		if self.isCharging:	# �������
			self.onChargeOver()

	def onChargeOver( self ):
		"""
		������
		"""
		self.isCharging = False
		self.updateChaseSpeed()		# �����ٶ�
		self.resumeHeartBeat()		# ���������ָ�����
		if self.tussleMode == csdefine.PET_TUSSLE_MODE_PASSIVE:
			self.stopAttacking()

	def chaseSpeed( self ):
		"""׷���ٶ�"""
		if self.isAttacking():
			return self.move_speed
		else:
			return BigWorld.player().move_speed * 1.2

	def updateChaseSpeed( self ):
		"""����׷���ٶ�"""
		if self.isCharging: return	# ���ڳ��
		self.navigator.updateSpeed(self.chaseSpeed())

#	# others --------------------------------------------------------
	# ---------------------------------------------------------------
	def enterWorld( self ):
		"""
		"""
		if self.ownerID == BigWorld.player().id:
			self.navigator = PetChaser( self, PetNavigator(self) )
			if self.clientControlled():
				self.resumeHeartBeat()
			else:
				self.cell.onClientReady()
			self.onWaterPosToServer( self.position )

	def leaveWorld( self ):
		"""
		"""
		self.cancelHeartBeat()
		self.cancelFollow()
		self.stopMove()

	def onControlled( self, isControlled ):
		"""
		�Ƿ��ɿͻ��˿��ƣ����������
		���Ѳ���ʹ�ã�
		"""
		INFO_MSG("Pet(%i) is controlled by client: %s"%(self.id, isControlled))
		if isControlled:
			self.initPhysics()
			self.resumeHeartBeat()
		else:
			self.cancelHeartBeat()
			self.stopMove()

	def clientControlled( self ):
		"""
		�Ƿ��ɿͻ��˿����ƶ�
		"""
		#return hasattr(self, "physics")
		return self.__clientControlled

	def onClientControlled( self, isControlled ):
		"""
		������֪ͨ�ͻ��˽��п���
		<Defined method>
		"""
		INFO_MSG("Pet(%i) is controlled by client: %s"%(self.id, isControlled))
		self.__clientControlled = isControlled
		if isControlled:
			self.resumeHeartBeat()
		else:
			self.cancelHeartBeat()
			self.stopMove()

	def setActionMode( self, mode ):
		"""������Ϊģʽ������ǿͻ��˵���Ϊ��δ������
		�����Ƿ�ɹ����ø���Ϊģʽ�����������ǰ����һ��
		�ɹ�������������޸����󣬷������ض�������ͻ���
		������"""
		self.onSetActionMode(mode)

	def onSetActionMode( self, mode ):
		"""��Ϊģʽ�ı�"""
		if self.clientControlled():
			if mode == csdefine.PET_ACTION_MODE_FOLLOW :
				self.forcePursueOwner()								# ǿ�ȳ���ص��������
			elif mode == csdefine.PET_ACTION_MODE_KEEPING :
				self.backToKeepPoint()

	def onSetTussleMode( self, mode ):
		"""ս��ģʽ�ı�"""
		if mode == csdefine.PET_TUSSLE_MODE_PASSIVE:
			if self.clientControlled():
				if self.actionMode == csdefine.PET_ACTION_MODE_KEEPING:
					self.backToKeepPoint()
				else:
					self.forcePursueOwner()

	def onSetKeepPosition( self, position ):
		"""
		<Defined method>
		����ͣ��λ��
		"""
		DEBUG_MSG("Pet(%i) set keep point to %s" % (self.id, position))
		self.__keepPosition = position

	def onActWordChanged( self, old ):
		"""
		��Ϊ���Ʊ�ʶ�ı�
		"""
		if self.actionSign(csdefine.ACTION_FORBID_MOVE):
			self.stopMove()

#	# client move -------------------------------------------------
	def syncPositionToServer( self, pos ):
		"""�������ͬ��λ��"""
		self.cell.synchronisePositionFromClient(pos)

	def onWaterPosToServer( self, position ):
		"""
		��ˮ����ײ��ˢ��λ��
		"""
		pos = utils.posOnGround( self.spaceID, position, default=position )
		dstPos = BigWorld.toWater( pos )
		if dstPos is not None:
			pos = dstPos
		self.syncPositionToServer( pos )
