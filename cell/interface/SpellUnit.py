# -*- coding: gb18030 -*-
#
#$Id: SpellUnit.py,v 1.41 2008-08-06 03:29:05 kebiao Exp $


"""
��ʩ����λ����ģ��
spell��buff��cooldown���ڴ�ģ�鴦��
"""

import BigWorld
import csdefine
import csconst
import csstatus
import Const
import ECBExtend
import items
import math
import SkillTargetObjImpl
from bwdebug import *
import time
from Resource.SkillLoader import g_skills

from CPUCal import CPU_CostCal

class SpellUnit:
	def __init__( self ):
		"""
		��ʼ����
		"""
		pass


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onAddBuff( self, buff ) :
		"""
		���һ�� buff
		"""
		#����Ƿ���Ҫ�ͻ�����ʾ����������
		if buff["sourceType"] == csdefine.BUFF_ORIGIN_SYSTEM:
			return
		self.planesAllClients( "onAddBuff", ( buff, ) )

	def onRemoveBuff( self, buff ) :
		"""
		ɾ��һ�� buff
		"""
		self.planesAllClients( "onRemoveBuff", ( buff[ "index" ], ) )


	# ----------------------------------------------------------------
	# spell about
	# ----------------------------------------------------------------
	def castSpellOnReal( self, skill, targetEntityID ):
		"""
		define method.
		ʹ��һ�����ܣ������Լ����ܲ�����realʱ��ʩ��
		"""
		try:
			targetEntity = BigWorld.entities[targetEntityID]
		except KeyError:
			ERROR_MSG( "%i: I target %i not found." % (self.id, targetEntityID) )		# ֻ�������ĳЩ�������
			return

		skill.use( self, SkillTargetObjImpl.createTargetObjEntity( targetEntity ) )

	def beforeSpellUse( self, spell, target ):
		"""
		��ʹ�ü���֮ǰҪ��������
		@param  spell:	Ҫʹ�õļ���
		@type   spell:	skill
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_MONSTER_FLY ):
			return
		if target.getType() == csdefine.SKILL_TARGET_OBJECT_ENTITY and hasattr( self, "stopMoving" ):
			self.stopMoving()

	def castSpell( self, skillID, target ):
		"""
		ʹ��һ�����ܣ��ڲ�ʹ�á�

		@param  skillID:	Ҫʹ�õļ��ܱ�ʶ
		@type   skillID:	SKILLID
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT, csdefine/SKILL_*
		"""
		try:
			spell = g_skills[skillID]
		except KeyError:
			printStackTrace()
			ERROR_MSG( "%i: skill %i not exist." % ( self.id, skillID ) )
			return csstatus.SKILL_NOT_EXIST
		
		className = self.className if self.className != "" else self.id
		CPU_CostCal( csdefine.CPU_COST_SKILL, csdefine.CPU_COST_SKILL_CHECK, skillID, className )
		state = self.useableCheck( skillID, target )
		CPU_CostCal( csdefine.CPU_COST_SKILL, csdefine.CPU_COST_SKILL_CHECK, skillID, className )
		if state != csstatus.SKILL_GO_ON:
			#INFO_MSG( "%i: skill %i use state = %i." % ( self.id, skillID, state ) )
			return state
		self.beforeSpellUse( spell, target )
		CPU_CostCal( csdefine.CPU_COST_SKILL, csdefine.CPU_COST_SKILL_USE, skillID, className )
		spell.use( self, target )
		CPU_CostCal( csdefine.CPU_COST_SKILL, csdefine.CPU_COST_SKILL_USE, skillID, className )
		return csstatus.SKILL_GO_ON
		
	def useableCheck( self, skillID, target ):
		"""
		�ͷż��ܵ�����״̬�ж�
		
		@param  skillID:	Ҫʹ�õļ��ܱ�ʶ
		@type   skillID:	SKILLID
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		state = self.entityStateCheck( target )
		if state != csstatus.SKILL_GO_ON:
			return state
		
		spell = g_skills[skillID]
		return spell.useableCheck( self, target )
		
	def entityStateCheck( self, target ):
		"""
		virtual method
		�ͷż��ܵ�״̬�жϣ���ͬentity����ͨ����д�˷���ʵ�ֲ�ͬ�������ж�
		"""
		# ʩ�����ж�
		if self.intonating():
			return csstatus.SKILL_INTONATING
		#if self.inHomingSpell():
		#	return csstatus.SKILL_CANT_CAST
		
		# ��ϵ�ж�
		if target.getType() == csdefine.SKILL_TARGET_OBJECT_ENTITY:
			
			entity = target.getObject()
			caster = self
			
			if entity.isEntityType( csdefine.ENTITY_TYPE_PET ):
				entity = entity.getOwner().entity
				if entity is None: 
					return csstatus.SKILL_CANT_CAST
					
			if self.isEntityType( csdefine.ENTITY_TYPE_PET ):
				caster = self.getOwner().entity
				if caster is None:
					return csstatus.SKILL_CANT_CAST
					
			if hasattr( entity, "qieCuoState" ) and caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				if entity.qieCuoState != csdefine.QIECUO_NONE and not entity.isQieCuoTarget( caster.id ) and entity.id != caster.id:
					return csstatus.SKILL_TARGET_IS_QIECUO
		
		return csstatus.SKILL_GO_ON
		
	def getRangeBias( self ):
		"""
		��ò�ͬentity�ļ����ͷ�ƫ��ֵ��ģ�巽��

		ƫ�����������ڿͻ��˴����ͷż��ܵ�entity�����壬����entityĿǰֻ�н�ɫ��
		"""
		return 0.0

	def receiveSpell( self, casterID, skillID, damageType, damage, param3 ):
		"""
		Define method.
		���ܼ��ܴ���

		@type   casterID: OBJECT_ID
		@type    skillID: INT
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		try:
			caster = BigWorld.entities[casterID]
		except KeyError:
			ERROR_MSG( "casterID %i not found." % (casterID) )		# ֻ�������ĳЩ�������
			caster = None
		if damage > 0 and caster and caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			caster.addComboCount(  )

		try:
			self.planesAllClients( "receiveSpell", ( casterID, skillID, damageType, damage ) )
		except TypeError:
			EXCEHOOK_MSG( "thow error Data: casterID=%i, skillID=%i, damageType=%i, damage=%i " % \
			( casterID, skillID, damageType, damage ) )

	def intonate( self, skill, target, time ):
		"""
		�����ȥ����һ�����ܣ����㲥��allClients��

		@param    skill: instance of Spell
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: BOOL������Ѿ��������򷵻�False�����򷵻�True
		"""
		if self.actionSign( csdefine.ACTION_FORBID_INTONATING ):
			self.statusMessage( csstatus.SKILL_FORBID_INTONATING )
			return False

		if self.attrIntonateTimer > 0:
			return False

		if self.attrHomingSpell:
			self.delHomingSpell( csstatus.SKILL_INTERRUPTED_BY_SPELL_2 )
		
		intonateTime = time
		self.attrIntonateTimer = self.addTimer( intonateTime, 0, ECBExtend.INTONATE_TIMER_CBID )

		# ��¼intonate��������Ҫ�õ��Ĳ���
		self.attrIntonateSkill = skill
		self.attrIntonateTarget = target

		# ֪ͨall client
		self.planesAllClients( "intonate", ( skill.getID(), intonateTime, target ) )
		return True

	def intonating( self ):
		"""
		����Ƿ�����������
		"""
		return self.attrIntonateTimer != 0

	def interruptSpell( self, reason ):
		"""
		define method.
		�жϷ�����ʩ�ţ���֪ͨclient��

		@param reason: �жϵ�ԭ��
		"""
		if self.attrIntonateSkill:
			INFO_MSG( "spell %i interrupted. reason: %s" % (self.attrIntonateSkill.getID(), reason) )
			if self.attrIntonateSkill.interruptCheck( self, reason ):
				if self.attrIntonateTimer > 0:
					self.cancel( self.attrIntonateTimer )
					self.attrIntonateTimer = 0

					# ʩ���ж�֪ͨ
					self.onSpellInterrupted()
					# ֪ͨall client��������ǰ��ʩ������
					self.planesAllClients( "spellInterrupted", ( self.attrIntonateSkill.getID(), reason ) )
					# ����attrIntonateSkill(����)���ܣ�
					# ����attrIntonateTarget�������ƺ�Ҳ���ԣ�������ʱû��������Щ���ԡ�
					self.attrIntonateSkill = None

		if self.attrHomingSpell:
			if self.attrHomingSpell.canInterruptSpell( reason ):
				INFO_MSG( "HomingSpell %i interrupted. reason: %s" % (self.attrHomingSpell.getID(), reason) )
				self.planesAllClients( "spellInterrupted", ( self.attrHomingSpell.getID(), reason ) )
				self.delHomingSpell( reason )



	def onSpellInterrupted( self ):
		"""
		��ʩ�������ʱ��֪ͨ��
		����ͨ��self.attrIntonateTarget��self.attrIntonateSkill��õ�ǰ��ʩ��Ŀ�ꡢλ���Լ�����ʵ��
		"""
		self.attrIntonateSkill.onSpellInterrupted( self )

	def addCastQueue( self, skill, target, delay ):
		"""
		���ڷ�����ʩ���п��ܲ�����Ŀ�ֻ꣨��λ�ã���������һ���������˺��ӳپ��޷���λĿ���ˣ�
		��˼��ܵ��ӳ�ֻ�ܷ���ʩ�������ϣ�����ֻ�����ӳ�ʱ�䵽���Ժ���ܿ�ʼ�����˺���
		��Ȼ����������ڼ�Ŀ�겻������������Ը�spell��

		����spellID��position��ʵֻ�����һ����������ôʹ����spell�Լ�������

		@type     skill: SKILL
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@type     delay: float
		return: None
		"""
		controllerID = self.addTimer( delay , 0, ECBExtend.DELAY_DAMAGE_TIMER_CBID )
		self.attrDelayList.append( {"skill" : skill, "target" : target,  "delayID" : controllerID } )

	def onReceiveDelayOver( self, controllerID, userData ):
		"""
		timer callback.
		see also Entity.onTimer() method.
		"""
		className = self.className if self.className != "" else self.id

		for index, delayData in enumerate( self.attrDelayList ):
			if delayData["delayID"] == controllerID:
				self.attrDelayList.pop( index )
				# ��ȡreceiver
				target = delayData["target"]
				# ��ȡspellʵ��
				spell = delayData["skill"]
				# ���ﲻ���жϷ��������ľ���ȼ���ˡ�
				CPU_CostCal( csdefine.CPU_COST_SKILL, csdefine.CPU_COST_SKILL_ARRIVE, spell.getID(), className )
				spell.onArrive( self, target )
				CPU_CostCal( csdefine.CPU_COST_SKILL, csdefine.CPU_COST_SKILL_ARRIVE, spell.getID(), className )
				return	# ֻ�����һ���ҵ���

	def cancelSpellMoveEffect( self, casterID, skillID ):
		"""
		ȡ������Ч���ƶ����ܵĽ�������Timmer�ص�
		��֪ͨ�ͻ���
		add by wuxo 2012-4-23
		"""
		cancelL = []
		for index, delayData in enumerate( self.attrDelayList ):
			if delayData["skill"].getID() == skillID:
				self.cancel( delayData["delayID"] )
				cancelL.append( delayData )
		for i in cancelL:
			self.attrDelayList.remove( i )
		self.planesAllClients( "onEndSpellMove", ( casterID, ) )

	def onIntonateOver( self, controllerID, userData ):
		"""
		timer callback.
		see also Entity.onTimer() method.

		�ڴ˴���������Ҫ�ҵ���Ӧ��skill��������skill.use()��������ʩ�ŷ�����
		"""
		target = self.attrIntonateTarget

		#INFO_MSG( "--> %i: spellID = %i, targetID = %i, position =" % ( self.id, self.attrIntonateSkill.getID(), targetID ), position  )
		skill = self.attrIntonateSkill
		state = skill.castValidityCheck( self, target )
		if state != csstatus.SKILL_GO_ON:
			self.interruptSpell( state )
			return

		# ����attrIntonateSkill(����)���ܣ�
		# ����attrIntonateTarget�������ƺ�Ҳ���ԣ�������ʱû��������Щ���ԡ�
		self.attrIntonateSkill = None
		self.attrIntonateTimer = 0

		# ��ʼʩ��Ч��
		skill.cast( self, target )

	def onSkillCastOver( self, spellInstance, target ):
		"""
		virtual method.
		�ͷż�����ɡ�

		@param  spellInstance: ����ʵ��
		@type   spellInstance: SPELL
		@param  target: ����Ŀ��
		@type   target: SkillImplTargetObj
		"""
		pass	# Ĭ��ɶ������

	def onSkillArrive( self, spellInstance, receivers ):
		"""
		virtual method.
		����Ч���Ѿ���������Ŀ��

		@param  spellInstance: ����ʵ��
		@type   spellInstance: SPELL
		@param  receivers: �����ܵ��������Ӱ���entity
		@type   receivers: List
		"""
		for receiver in receivers:
			self.onSkillArriveReceiver( spellInstance, receiver )

	def onSkillArriveReceiver( self, spellInstance, receiver ):
		"""
		virtual method.
		����Ч���Ѿ�����ĳ��Ŀ��

		@param  spellInstance: ����ʵ��
		@type   spellInstance: SPELL
		@param  receiver: �ܵ��������Ӱ���entity
		@type   receiver: entity
		"""
		pass

	def onSkillCastOverTarget( self, spellInstance, target ):
		"""
		virtual method.
		�ͷż�����ɡ�

		@param  spellInstance: ����ʵ��
		@type   spellInstance: SPELL
		@param  target: Ŀ��entity
		@type   target: Entity
		"""
		pass

	def receiveOnReal( self, casterID, skill ):
		"""
		Define and virtual method.
		����ĳ��spell��Ч����

		@param casterID: ʩ����
		@type  casterID: Entity
		@param    skill: ����ʵ��
		@type     skill: SKILL
		"""
		try:
			caster = BigWorld.entities[casterID]
		except KeyError:
			caster = None
		skill.receive( caster, self )

	def onChargeOver( self, controllerID, userData ):
		"""
		�Ŷӳ��������ɵ��ٶ���ɽ���
		"""
		self.calcMoveSpeed()

	def requestPlaySkill( self, sourceID, skillID):
		"""
		define method
		�ͻ������벥�ż���
		"""
		if not self.hackVerify_( sourceID ) : return
		skillIDs = self.queryTemp("TEL_SKILLS",[])
		if skillID in skillIDs and self.hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT ) :
			self.spellTarget( skillID, self.id )

	def requestClearBuffer( self, sourceID ):
		"""
		define method
		�ͻ����������buff Ŀǰֻ���ڽ������贫��buff
		"""
		if not self.hackVerify_( sourceID ) : return
		self.clearBuff( [ csdefine.BUFF_INTERRUPT_TELEPORT_FLY ] )
	# --------------------------------------------------------
	# HomingSpell about
	# --------------------------------------------------------
	def addHomingSpell( self, skill ):
		"""
		���һ����������
		"""
		if self.attrHomingSpell:
			return False

		self.attrHomingSpell = skill
		self._addHomingSpellTimer()

		if self.client:
			self.client.onStartHomingSpell( skill.getPersistent() )
		return True

	def _addHomingSpellTimer( self ):
		if self.attrHomingSpell is None: return
		tick = self.attrHomingSpell.getTickInterval()
		if self.attrHomingSpellTickTimer:
			self.cancel( self.attrHomingSpellTickTimer )
			self.attrHomingSpellTickTimer = 0
		self.attrHomingSpellTickTimer = self.addTimer( tick, 0, ECBExtend.HOMING_SPELL_TICK_CBID )

	def onHomingSpellTick( self, controllerID, userData ):
		"""
		�������ܵ�tick��Ӧ
		"""
		if not self.attrHomingSpell.isTimeout():
			state = self.attrHomingSpell.onTick( self )
			if state != csstatus.SKILL_GO_ON:
				self.interruptSpell( state )
			else:
				self._addHomingSpellTimer()
		else:
			self.delHomingSpell( csstatus.SKILL_INTERRUPTED_BY_TIME_OVER )


	def delHomingSpell( self, reason ):
		"""
		ɾ��һ����������
		"""
		if self.attrHomingSpell:
			if self.attrHomingSpellTickTimer > 0:
				self.cancel( self.attrHomingSpellTickTimer )
				self.attrHomingSpellTickTimer = 0
			self.attrHomingSpell.onInterrupted( self, reason )
			self.attrHomingSpell = None
			if self.client:
				self.client.onFiniHomingSpell()
		else:
			ERROR_MSG("Homing Spell is not using when delete!!")
			printStackTrace()

	def delHomingOnCast( self, skillInstance ):
		"""
		�ͷż��ܼ���Ƿ�ɾ����������
		"""
		if not self.attrHomingSpell: return
		# �������ܱ�����Լ��ܴ�����ɾ����������
		if skillInstance.getID() in self.attrHomingSpell.getChildSpellIDs(): return
		self.delHomingSpell( csstatus.SKILL_INTERRUPTED_BY_SPELL_2 )

	def inHomingSpell( self ):
		"""
		����Ƿ���������������
		"""
		return self.attrHomingSpellTickTimer != 0

	# --------------------------------------------------------
	#triggerSpell about �µĴ����������� add by wuxo 2012-2-8
	# --------------------------------------------------------

	def addTriggerSpell( self, skillParentID, skillID ):
		"""
		���һ����������
		"""
		if not self.attrTriggerSpell.has_key(skillParentID):
			self.attrTriggerSpell[skillParentID] = {}
		self.attrTriggerSpell[skillParentID]["skillID"] = skillID

		if self.attrTriggerSpell[skillParentID].has_key("timerID") and self.attrTriggerSpell[skillParentID]["timerID"] !=0:
			self.cancel( self.attrTriggerSpell[skillParentID]["timerID"] )
			self.attrTriggerSpell[skillParentID]["timerID"] = 0
		if skillID != 0:
			self._addTriggerSpellTimer(skillParentID)

		if self.client:
			self.client.onTriggerSpell( skillParentID, skillID )


	def _addTriggerSpellTimer( self, skillParentID):
		if self.attrTriggerSpell[skillParentID].has_key("timerID") and self.attrTriggerSpell[skillParentID]["timerID"]!=0 :
			self.cancel(self.attrTriggerSpell[skillParentID]["timerID"])
			self.attrTriggerSpell[skillParentID]["timerID"] = 0
		skillID = self.attrTriggerSpell[skillParentID]["skillID"]
		timeData = g_skills[skillID].getTriggerTime()
		timerid = 0
		if timeData > 0:
			timerid = self.addTimer( timeData, 0, ECBExtend.TRIGGER_SPELL_CBID )
		self.attrTriggerSpell[skillParentID]["timerID"] = timerid

	def onTriggerSpell( self, controllerID, userData ):
		"""
		�������ܵĳ���ʱ�䵽
		"""
		for skillid in self.attrTriggerSpell:
			if self.attrTriggerSpell[skillid].has_key("timerID") and self.attrTriggerSpell[skillid]["timerID"] == controllerID:
				self.addTriggerSpell( skillid, 0 )
				self.attrTriggerSpell[skillid]["timerID"] = 0
	# --------------------------------------------------------
	# cooldown about
	# --------------------------------------------------------
	def changeCooldown( self, typeID, lastTime, totalTime, endTimeVal ):
		"""
		virtual method.
		�ı�һ��cooldown������

		@type  typeID: INT16
		@type timeVal: INT32
		"""
		self.attrCooldowns[typeID] = ( lastTime, totalTime, endTimeVal )

	def getCooldown( self, typeID ):
		"""
		virtual method.
		��ȡһ��cooldown��ʱ��ֵ�����ָ�����Ͳ������򷵻�0

		@rtype: ����ʱ��INT32
		"""
		try:
			return self.attrCooldowns[typeID][2]
		except KeyError:
			return 0

	def requestCooldowns( self, srcEntityID ):
		"""
		Exposed method.
		�����������е�Cooldown�����������ڵ�client
		"""
		if srcEntityID == self.id:
			client = self.client	# ����Լ�����
		else:
			try:
				entity = BigWorld.entities[srcEntityID]
			except KeyError:
				return
			client = entity.clientEntity( self.id )

		for typeID, timeVal in self.attrCooldowns.iteritems():
			client.cooldownChanged( typeID, timeVal[0], timeVal[1] )

	def requestSelfCooldowns( self ) :
		"""
		�����Լ��� colldown�����¿ͻ���( hyw -- 2008.06.10 )
		"""
		self.requestCooldowns( self.id )
		self.client.onInitialized( csdefine.ROLE_INIT_COLLDOWN )


	# --------------------------------------------------------
	# buff about
	# --------------------------------------------------------
	def requestSelfBuffs( self ) :
		"""
		�����Լ��� buff�����¿ͻ���( hyw -- 2008.06.10 )
		"""
		self.requestBuffs( self.id )
		self.client.onInitialized( csdefine.ROLE_INIT_BUFFS )

	def requestBuffs( self, srcEntityID ):
		"""
		Exposed method.
		�����������е�buff�����������ڵ�client
		"""
		if srcEntityID == self.id:
			client = self.client	# ����Լ�����
		else:
			try:
				entity = BigWorld.entities[srcEntityID]
			except KeyError:
				return
			client = entity.clientEntity( self.id )

		for buff in self.attrBuffs:
			#����Ƿ���Ҫ�ͻ�����ʾ����������
			if buff["sourceType"] != csdefine.BUFF_ORIGIN_SYSTEM:
				client.onReceiveBuff( buff )


	def buffReload( self ):
		"""
		����ʹBuff��Ч������Role��ʼ�������Ժ󣬽������buff���
		"""
		assert self.isReal()
		#DEBUG_MSG( "-->", self.attrBuffs )
		for idx, buff in enumerate( self.attrBuffs ):
			spell = buff["skill"]
			if not self.hasState( buff, csdefine.BUFF_STATE_DISABLED | csdefine.BUFF_STATE_HAND ):
				spell.doReload( self, buff )

		if len( self.attrBuffs ) > 0:
			self.buffTimer = self.addTimer( 1, 1, ECBExtend.BUFF_TIMER_CBID )

	def addBuffState( self, index, state ):
		"""
		�ı�ĳ������λ�õ�BUFF״̬
		@param index: ��BUFF����λ��
		@param state:״̬
		"""
		assert self.isReal(), "attrBuffs index %i, addState:%i" % ( index, state )
		DEBUG_MSG( "attrBuffs index %i, addState:%i" % ( index, state ) )
		buffData = self.attrBuffs[ index ]
		buffData[ "skill" ].onAddState( self, buffData, state )
		buffData[ "skill" ] = buffData[ "skill" ]	# ���¸�ֵ��ʹ�������¹㲥��������ghost��������ܻ�������
		buffData[ "state" ] |= state

	def removeBuffState( self, index, state ):
		"""
		�ı�ĳ������λ�õ�BUFF״̬
		@param index: ��BUFF����λ��
		@param state:״̬
		"""
		assert self.isReal(), "attrBuffs index %i, removeState:%i" % ( index, state )
		DEBUG_MSG( "attrBuffs index %i, removeState:%i" % ( index, state ) )
		buffData = self.attrBuffs[ index ]
		buffData[ "skill" ].onRemoveState( self, buffData, state )
		buffData[ "skill" ] = buffData[ "skill" ]	# ���¸�ֵ��ʹ�������¹㲥��������ghost��������ܻ�������
		buffData[ "state" ] &= ~state

	def hasState( self, buff, state ):
		"""
		�Ƿ���ڱ�ǡ�
			@return	:	�����
			@rtype	:	bool
		"""
		return buff[ "state" ] & state != 0

	def clearBuff( self, reasons ):
		"""
		define method
		ȥ������Buff�� BUFF_INTERRUPT_NONE ������ִ��
		"""
		assert self.isReal(), "%s" % str( reasons )
		for idx in xrange( len( self.attrBuffs ) - 1, -1, -1 ):
			try:
				self.removeBuff( idx, reasons )
			except IndexError:
				continue

	def onBuffTick( self, timerID, cbID ):
		"""
		Ч��ÿ�����á�
		"""
		self.currBuffTickIndex = len( self.attrBuffs ) - 1
		while self.currBuffTickIndex >= 0:
			buff = self.attrBuffs[ self.currBuffTickIndex ]

			if self.hasState( buff, csdefine.BUFF_STATE_HAND ):
				self.currBuffTickIndex -= 1
				continue

			spell = buff["skill"]
			# index = buff["index"]
			buff["currTick"] = spell.doTick( buff["currTick"] )
			if spell.isTimeout( buff["persistent"] ):
				self.removeBuff( self.currBuffTickIndex, [csdefine.BUFF_INTERRUPT_NONE] )
				return

			if not self.hasState( buff, csdefine.BUFF_STATE_DISABLED ) and buff["currTick"] == 0:
				#INFO_MSG( "Before doLoop, buff: %s"%buff[ "skill" ].getBuffID() )
				if not spell.doLoop( self, buff ):
					self.removeBuff( self.currBuffTickIndex, [csdefine.BUFF_INTERRUPT_NONE] )
					self.currBuffTickIndex -= 1
					continue

			# �ڴ˴���һ���ݴ������ǲ��ܱ�֤��buff��doLoop()�ﲻ�����һЩ��Ҫ�ģ�����Ϊʧ��ģ����ͣ�
			# ��ˣ���������������������д������ȷʵ���������������������ֱ�ӷ��أ����ڴ��´εĴ���
			# ��assert������if����Ϊ����ͨ���򵥵���־���˷�ʽ�������⡣
			try:
				assert self.isReal(), "%s" % str( dict( buff ) )
			except:
				EXCEHOOK_MSG( "onBuffTick warning" )
				return

			self.currBuffTickIndex -= 1

	def removeBuff( self, index, reasons ):
		"""
		���б���ȥ��һ��Buff��֪ͨ�ͻ��ˡ�
		@param index: BUFF���ڵ�����
		@param reasons:����ȡ����BUFF������ [�ж���]
		"""
		assert self.isReal(), "remove a buff, index:%i, reasons:%s" % ( index, str( reasons ) )
		if self.isDestroyed:
			return False

		# ���ĳ��buff A��doLoop���Ƴ���buff B,Ȼ��buff A��doLoop���ؼ�ʱ���ͻ�������������
		# �����������־���������κ���������Ϊ����һ��buffTick��buff A�ᱻ�����Ƴ� by mushuang
		if index >= len( self.attrBuffs ):
			ERROR_MSG( "Buff already removed( idx: %s, len( attrBuffs ) = %s )"%( index, len( self.attrBuffs ) ) )
			ERROR_MSG( "Entity type: %s, id: %s"%( self, self.id ) )
			return False

		buff = self.getBuff( index )
		spell = buff["skill"]

		if csdefine.BUFF_INTERRUPT_NONE not in reasons: # BUFF_INTERRUPT_NONE ������ִ��
			if not spell.cancelBuff( reasons ):			# ȡ��BUFFʧ�� ������Ϣ
				return False

		# ����onBuffTick->doLoop�п��ܻᵼ����һ��buff��ɾ������ôѭ����ʹ��ԭʼ��idx��������ɾ���Ϳ϶��Ǵ������
		# �����﷢��Ҫɾ����indexС��ѭ���ĵ�ǰindexʱ�ͱ䶯ƫ����
		if index < self.currBuffTickIndex:
			self.currBuffTickIndex -= 1

		self.attrBuffs.pop( index )
		spell.doEnd( self, buff )
		self.onRemoveBuff( buff )

		DEBUG_MSG( "remove a buff[%i], index:%i" % ( spell.getBuffID(), buff["index"] ) )

		# ���timer�Ƿ��д��ڵı�Ҫ, ���û����ᱻȥ��
		if self.buffTimer != 0:
			if self.state == csdefine.ENTITY_STATE_DEAD or len( self.attrBuffs ) == 0:
				self.cancel( self.buffTimer )
				self.buffTimer = 0

		return True

	def removeBuffByID( self, skillID, reasons ):
		"""
		ɾ����һ����skillID��ͬ��buff
		@param reasons:����ȡ����BUFF������
		"""
		for index, buff in enumerate( self.attrBuffs ):
			if buff["skill"].getID() == skillID:
				self.removeBuff( index, reasons )
				return

		ERROR_MSG( "%i: skillID %i not found in buffs." % (self.id, skillID) )

	def removeBuffByBuffID( self, buffID, reasons ):
		"""
		ɾ����һ�����buffID��ͬ��buff
		@buffID��buff��ID
		@reasons: �Ƴ���ԭ�򣬲ο�csdefine.BUFF_INTERRUPT_XXX��ע�⣬�˲���������һ���ɱ����Ľṹ����list����tuple
		"""
		for index, buff in enumerate( self.attrBuffs ):
			if buff["skill"].getBuffID() == buffID:
				res = self.removeBuff( index, reasons )
				if res: INFO_MSG( "Buff: %s removed for reasons: %s"%( buffID, str( reasons ) ) )
				else: INFO_MSG( "Buff: %s is not removable for reasons: %s"%( buffID, str( reasons ) ) )
				return res

		WARNING_MSG( "No such buff found with buffID: %s"%buffID )

	def removeBuffByUID( self, uid, reasons ):
		"""
		ɾ����һ����skillID��ͬ��uid
		@param reasons:����ȡ����BUFF������
		"""
		for index, buff in enumerate( self.attrBuffs ):
			if buff["skill"].getUID() == uid:
				self.removeBuff( index, reasons )
				return

		ERROR_MSG( "%i: skillUID %i not found buff." % (self.id, uid) )

	def removeBuffByIndex( self, index, reasons ):
		"""
		����buff����ɾ��һ��buff
		@param reasons:����ȡ����BUFF������
		"""
		for idx, buff in enumerate( self.attrBuffs ):
			if buff["index"] == index:
				self.removeBuff( idx, reasons )
				return
		ERROR_MSG( "%i: skillUID index: %i not found buff." % (self.id, index) )

	def removeAllBuffByID( self, skillID, reasons ):
		"""
		ɾ��������skillID��ͬ��buff
		@param reasons:����ȡ����BUFF������
		"""
		for idx in xrange( len( self.attrBuffs ) - 1, -1, -1 ):
			try:
				buff = self.attrBuffs[ idx ]
			except IndexError:
				continue

			if buff["skill"].getID() == skillID:
				self.removeBuff( idx, reasons )

	def removeAllBuffsBySkillID( self, skillID, reasons ) :
		"""
		ɾ��������ID��skillID�ļ��ܴ�����buff
		"""
		# ע��self.attrBuffs��<type 'PyArrayDataInstance'>������ʹ��������Ƭ���ƣ�
		# ����self.attrBuffs[:]�õ������䱾����ͬһ��ʵ��������ͨ�б�һ����
		for idx in xrange( len(self.attrBuffs)-1, -1, -1 ):
			buff = self.attrBuffs[ idx ]
			if buff["skill"].getSourceSkillID() == skillID:
				self.removeBuff( idx, reasons )

	def removeBuffBySkillIDAndSourceIndex( self, skillID, index, reasons ):
		"""
		ɾ����һ����id��skillID��ӵ����ڼ����е�������index��buff
		"""
		for idx in xrange( len(self.attrBuffs)-1, -1, -1 ):
			buff = self.attrBuffs[ idx ]
			if buff["skill"].getSourceSkillID() == skillID\
			and buff["skill"].getSourceSkillIndex() == index:
				self.removeBuff( idx, reasons )
				break

	def removeSkillLinkBuffs( self, skillID, reasons ):
		"""
		ɾ����ID��skillID�ļ�����ӵ�buff
		ע��ʹ�ô˷���ʱҪע�⣬����buff���д����������Ƶ�
		"""
		for buffData in g_skills[skillID].getBuffsLink():
			sourceIndex = buffData.getBuff().getSourceSkillIndex()
			self.removeBuffBySkillIDAndSourceIndex( skillID, sourceIndex, reasons )

	def addBuff( self, buff ):
		"""
		���һ��Buff��

		@param buff			:	instance of BUFF
		@type  buff			:	BUFF
		"""
		assert self.isReal(), "add a buff, %s" % str( dict( buff ) )
		# phw 2009-10-15: Ϊ�˲���buffż�����ʱ�䳬����ԭ���ڴ˴������жϵ�����Ϣ��
		# ��������������Ĵ�����Ҫɾ��
		# �����������ұ���buff�����⣬������û�м�������
		# ��˵��bigworld.time()�ܿ�����bug����ĳһʱ����ڻ�ͻȻ���һ���ܴ��ֵ��
		"""
		try:
			# �������ʱ�����24Сʱ�����������־ 3600 * 24 * csconst.SERVER_TIME_AMEND
			assert buff["persistent"] - time.time() <= 8640000
		except:
			EXCEHOOK_MSG( "calculate time error: %s, %s, persistent %s" % ( self.getName(), str( dict( buff ) ), str( buff["persistent"] - BigWorld.time() * 100 ) ) )
		"""
		buff[ "index" ] = self.newBuffIndex()
		casterID = buff["caster"]
		spell = buff[ "skill" ]

		if not self.hasState( buff, csdefine.BUFF_STATE_DISABLED | csdefine.BUFF_STATE_HAND ):
			spell.doBegin( self, buff )

		self.attrBuffs.append( buff )
		buff["caster"] = casterID
		self.onAddBuff( buff )

		if self.buffTimer == 0:
			self.buffTimer = self.addTimer( 1, 1, ECBExtend.BUFF_TIMER_CBID )

	def newBuffIndex( self ):
		"""
		����һ���µ�buffindex
		"""
		index = self.lastBuffIndex
		self.lastBuffIndex += 1
		return index

	def getBuffIndexsByType( self, buffType, effectType ):
		"""
		����ָ�����͵�����buff������

		@return: �ҵ��򷵻���Ӧ�������б��Ҳ����򷵻�[]
		"""
		buffs = []
		for index, buff in enumerate( self.attrBuffs ):
			if buff["skill"].getBuffType() == buffType and buff["skill"].getEffectState() == effectType:
				buffs.append( index )

		return buffs

	def getBuffIndexByType( self, buffType ):
		"""
		����ָ�����͵ĵ�һ��buff������

		@return: �ҵ��򷵻���Ӧ�������б��Ҳ����򷵻�-1
		"""
		for index, buff in enumerate( self.attrBuffs ):
			if buff["skill"].getBuffType() == buffType:
				return index

		return -1

	def getBuffIndexsBySourceType( self, buffSourceType ):
		"""
		����ָ�����͵�����buff������ BUFFС��

		@return: �ҵ��򷵻���Ӧ�������б��Ҳ����򷵻�[]
		"""
		buffs = []
		for index, buff in enumerate( self.attrBuffs ):
			if buff["skill"].getSourceType() == buffSourceType:
				buffs.append( index )

		return buffs

	def getBuffIndexsByEffectType( self, effectType ):
		"""
		����ָ�����͵�����buff������ BUFF��������  ���Ի�����

		@return: �ҵ��򷵻���Ӧ�������б��Ҳ����򷵻�[]
		"""
		buffs = []
		for index, buff in enumerate( self.attrBuffs ):
			if buff["skill"].getEffectState() == effectType:
				buffs.append( index )

		return buffs

	def findBuffsByBuffID( self, buffID ):
		"""
		����ָ�����͵�����buff������ ͨ��BUFFIDѰ��

		@return: �ҵ��򷵻���Ӧ�������б��Ҳ����򷵻�[]
		"""
		buffs = []
		for index, buff in enumerate( self.attrBuffs ):
			if buff["skill"].getBuffID() == buffID:
				buffs.append( index )

		#buffs.reverse() �ײ㲻���д˲���
		return buffs

	def removeAllBuffByBuffID( self, buffID, reasons ):
		"""
		ɾ��������skillID��ͬ��buff
		@param reasons:����ȡ����BUFF������
		"""
		for idx in xrange( len( self.attrBuffs ) - 1, -1, -1 ):
			try:
				buff = self.attrBuffs[ idx ]
			except IndexError:
				continue

			if buff["skill"].getBuffID() == buffID:
				self.removeBuff( idx, reasons )

	def findRemainTimeMinByIndexs( self, indexs ):
		"""
		��һ�������в���ʣ��ʱ����̵�BUFF����

		@return: �ҵ��򷵻���Ӧ������
		"""
		timeVal = int( time.time() )
		rm = 0
		index = indexs[0]

		for idx in indexs:
			t = self.getBuff( idx )["persistent"]

			if t == 0:
				continue #��������ʱ���

			rm1 = t - timeVal
			if rm > rm1:
				rm = rm1
				index = idx

		return index

	def getBuff( self, index ):
		"""
		ȡ��ĳ��λ�õ�buff

		@return: instance of BUFF
		"""
		return self.attrBuffs[index]

	def getBuffByIndex( self, index ):
		"""
		���� index ����ȡ��buff

		@return: instance of BUFF
		"""
		for idx, buff in enumerate( self.attrBuffs ):
			if buff["index"] == index:
				return self.attrBuffs[idx]

	def getBuffs( self ):
		"""
		ȡ������buffs

		@return: instance of BUFF
		"""
		return self.attrBuffs

	def getBuffByType( self, buffType ):
		"""
		����buff type��ȡ��һ��buff����

		@return: instance of buff or None if buff not found.
		@rtype:  BUFF
		"""
		for buff in self.attrBuffs:
			if buff["skill"].getBuffType() == buffType:
				return buff

		return None

	def getVehicleBuffs( self ):
		"""
		���������ϵ�ȫ�����buffʵ��
		"""
		buffs = []
		for index in self.currentVehicleBuffIndexs:
			buff = self.getBuffByIndex( index )
			buffs.append(buff)
		return buffs

	def getVehicleBuffByIndex( self, idx ):
		"""
		�����������������ϵĵ������buffʵ��
		"""
		for index in self.currentVehicleBuffIndexs:
			if index != idx:
				continue
			return self.getBuffByIndex( index )

	def spellNone( self, skillID ):
		"""
		����ҪĿ���λ�õ�ʩ����ʽ�����Լ�Ϊ����ʩ����
		@param  skillID: ������ʶ��
		@type   skillID: INT16
		"""
		return self.castSpell( skillID, SkillTargetObjImpl.createTargetObjPosition( self.position ) )

	def spellTarget( self, skillID, targetID ):
		"""
		��һ��entityʩ��
		@param  skillID: ������ʶ��
		@type   skillID: INT16
		@param targetID: Ŀ��entityID
		@type  targetID: OBJECT_ID
		"""
		try:
			receiver = BigWorld.entities[targetID]
		except:
			ERROR_MSG( "%s(%s): target not found. %s" % ( self.getName(), self.id, targetID ) )
			return csstatus.SKILL_UNKNOW

		if receiver.spaceID != self.spaceID:
			ERROR_MSG( "%s(%s): object %s is lost." % ( self.getName(), self.id, targetID ) )
			return csstatus.SKILL_UNKNOW
		return self.castSpell( skillID, SkillTargetObjImpl.createTargetObjEntity( receiver ) )

	def spellPosition( self, skillID, position ):
		"""
		��һ��λ��ʩ��
		@param  skillID: ������ʶ��
		@type   skillID: INT16
		@param position: Ŀ��λ��
		@type  position: VECTOR3
		"""
		return self.castSpell( skillID, SkillTargetObjImpl.createTargetObjPosition( position ) )

	def systemCastSpell( self, skillID ) :
		"""
		defined method
		ϵͳҪ��Ŀ��ʩ��ĳ�����ܣ����༼����ϵͳ�����ʩ�ŵļ��ܣ���ʩ����
		@param	skillID		: ����ID
		@type	skillID		: int64
		"""
		try:
			spell = g_skills[skillID]
		except KeyError:
			ERROR_MSG( "%i: skill %i not exist." % ( self.id, skillID ) )
			return
		
		CPU_CostCal( csdefine.CPU_COST_SKILL, csdefine.CPU_COST_SKILL_CHECK, "" )
		state = spell.useableCheck( None, self )
		CPU_CostCal( csdefine.CPU_COST_SKILL, csdefine.CPU_COST_SKILL_CHECK, "" )
		
		if state != csstatus.SKILL_GO_ON:
			INFO_MSG( "%i: skill %i use state = %i." % ( self.id, skillID, state ) )
			return

		try:
			CPU_CostCal( csdefine.CPU_COST_SKILL, csdefine.CPU_COST_SKILL_USE, skillID, "" )
			spell.use( None, SkillTargetObjImpl.createTargetObjEntity( self ) )
			CPU_CostCal( csdefine.CPU_COST_SKILL, csdefine.CPU_COST_SKILL_USE, skillID, "" )
		except:
			EXCEHOOK_MSG( "use skill %i is error!" % skillID)

	def attachSkillOnReal( self, skill ):
		"""
		Define mehtod.
		Զ��װ��һ������
		"""
		skill.attach( self )

	def detachSkillOnReal( self, skill ):
		"""
		Define method.
		Զ��ж��һ������
		"""
		skill.detach( self )

	def findBuffByBuffID( self, buffID ):
		"""
		ͨ��buffid�ҵ�ĳ��buff
		"""
		for buffData in self.attrBuffs:
			if buffData["skill"].getBuffID() == buffID:
				return buffData
		return None


	def findBuffByID( self, id ):
		"""
		����ָ�����ܶ�Ӧ��BUFF��ID��

		@return: buffʵ��
		"""
		for index, buff in enumerate( self.attrBuffs ):
			if buff["skill"].getID() == id:
				return buff
		return None

	def onFuncSpell( self, controllerID, userData )	:
		skillinfo = self.queryTemp( "talkfuncskill", None )
		if skillinfo != None :
			self.spellTarget( skillinfo[0], skillinfo[1] )


	def homingSpellResist( self, id ):
		"""
		�������ܱ�Ŀ��ֿ�
		"""
		self.client.onHomingSpellResist( id )

	def onBuffMiss( self, receiver, skill ):
		"""
		buffδ����
		"""
		pass

	def onBuffResist( self, receiver, buff ):
		"""
		buff���ֿ�
		"""
		pass

	def onBuffResistHit( self, buff ):
		"""
		�ֿ���buffЧ��
		"""
		pass
		
	def rotateToSpellTarget( self, target ):
		"""
		��ת����
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_CANT_ROTATE_IN_FIGHT_STATE ):
			return

		# ת����, ��Ҫ��ȷ�ķ���
		position = target.getObjectPosition()
		disPos = position - self.position

		if math.fabs( disPos.yaw ) > 0.0:
			self.rotateToPos( position )

	# --------------------------------------------------------
	# һЩ�����buff����
	# --------------------------------------------------------
	def getFlameWay( self, loopTime ):
		"""
		���ɻ���·����Buff_299004��
		"""
		if self.flameWayTimer == 0:
			self.flameWayTimer = self.addTimer( 0, loopTime, ECBExtend.FLAME_WAY_TIMER_CBID )

	def onFlameWayTimer( self, timerID, cbID ):
		"""
		ÿ������Tick
		"""
		if self.isDestroyed: return
		if not self.queryTemp( "FLAME_MOVE_EFFECTIVE", False ):	 # ֻ���ƶ�����Ч
			if not self.isMoving(): return
		dict = self.queryTemp( "FLAME_TRAP_DICT", {} )
		if not dict: return			#���getFlameWay�ص�ʱ�Ѿ�doEnd������·���Ѿ���ɾ�����ͻᱨ����Ϊ��ɾ���Ļ��Ͳ�����ִ���ˡ�GRL
		trap = BigWorld.createEntity( "SkillTrap", self.spaceID, self.position, self.direction, dict )
		skillID = self.queryTemp( "FLAME_SKILLID", 0 )
		if not skillID: return
		trap.trapSpellTarget( skillID, trap, trap )	# ������ʹ�ü���

	def delFlameWay( self ):
		"""
		���ٻ���·����Buff_299004��
		"""
		if self.flameWayTimer != 0:
			self.cancel( self.flameWayTimer )
			self.flameWayTimer = 0
		self.removeTemp( "FLAME_TRAP_DICT" )
		self.removeTemp( "FLAME_SKILLID" )
		self.removeTemp( "FLAME_MOVE_EFFECTIVE" )

	def detachNotNeedManaEffect( self ):
		"""
		�Ƴ�����Ҫ����ħ�����
		"""
		if not self.queryTemp( "NOT_NEED_MANA", False ): return
		self.removeTemp( "NOT_NEED_MANA" )

# SpellUnit.py
