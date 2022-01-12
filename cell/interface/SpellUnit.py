# -*- coding: gb18030 -*-
#
#$Id: SpellUnit.py,v 1.41 2008-08-06 03:29:05 kebiao Exp $


"""
可施法单位基础模块
spell、buff、cooldown都在此模块处理
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
		初始化。
		"""
		pass


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onAddBuff( self, buff ) :
		"""
		添加一个 buff
		"""
		#检查是否需要客户端显示等其他操作
		if buff["sourceType"] == csdefine.BUFF_ORIGIN_SYSTEM:
			return
		self.planesAllClients( "onAddBuff", ( buff, ) )

	def onRemoveBuff( self, buff ) :
		"""
		删除一个 buff
		"""
		self.planesAllClients( "onRemoveBuff", ( buff[ "index" ], ) )


	# ----------------------------------------------------------------
	# spell about
	# ----------------------------------------------------------------
	def castSpellOnReal( self, skill, targetEntityID ):
		"""
		define method.
		使用一个技能，用于自己可能不处于real时的施法
		"""
		try:
			targetEntity = BigWorld.entities[targetEntityID]
		except KeyError:
			ERROR_MSG( "%i: I target %i not found." % (self.id, targetEntityID) )		# 只会出现在某些极端情况
			return

		skill.use( self, SkillTargetObjImpl.createTargetObjEntity( targetEntity ) )

	def beforeSpellUse( self, spell, target ):
		"""
		在使用技能之前要做的事情
		@param  spell:	要使用的技能
		@type   spell:	skill
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_MONSTER_FLY ):
			return
		if target.getType() == csdefine.SKILL_TARGET_OBJECT_ENTITY and hasattr( self, "stopMoving" ):
			self.stopMoving()

	def castSpell( self, skillID, target ):
		"""
		使用一个技能，内部使用。

		@param  skillID:	要使用的技能标识
		@type   skillID:	SKILLID
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
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
		释放技能的所有状态判断
		
		@param  skillID:	要使用的技能标识
		@type   skillID:	SKILLID
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		state = self.entityStateCheck( target )
		if state != csstatus.SKILL_GO_ON:
			return state
		
		spell = g_skills[skillID]
		return spell.useableCheck( self, target )
		
	def entityStateCheck( self, target ):
		"""
		virtual method
		释放技能的状态判断，不同entity可以通过重写此方法实现不同的条件判断
		"""
		# 施法者判断
		if self.intonating():
			return csstatus.SKILL_INTONATING
		#if self.inHomingSpell():
		#	return csstatus.SKILL_CANT_CAST
		
		# 关系判断
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
		获得不同entity的技能释放偏移值，模板方法

		偏移量仅对于在客户端触发释放技能的entity有意义，此类entity目前只有角色。
		"""
		return 0.0

	def receiveSpell( self, casterID, skillID, damageType, damage, param3 ):
		"""
		Define method.
		接受技能处理

		@type   casterID: OBJECT_ID
		@type    skillID: INT
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		try:
			caster = BigWorld.entities[casterID]
		except KeyError:
			ERROR_MSG( "casterID %i not found." % (casterID) )		# 只会出现在某些极端情况
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
		让玩家去吟唱一个技能，并广播给allClients；

		@param    skill: instance of Spell
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: BOOL；如果已经在吟唱则返回False，否则返回True
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

		# 记录intonate结束后需要用到的参数
		self.attrIntonateSkill = skill
		self.attrIntonateTarget = target

		# 通知all client
		self.planesAllClients( "intonate", ( skill.getID(), intonateTime, target ) )
		return True

	def intonating( self ):
		"""
		检查是否正在吟唱中
		"""
		return self.attrIntonateTimer != 0

	def interruptSpell( self, reason ):
		"""
		define method.
		中断法术的施放，并通知client。

		@param reason: 中断的原因
		"""
		if self.attrIntonateSkill:
			INFO_MSG( "spell %i interrupted. reason: %s" % (self.attrIntonateSkill.getID(), reason) )
			if self.attrIntonateSkill.interruptCheck( self, reason ):
				if self.attrIntonateTimer > 0:
					self.cancel( self.attrIntonateTimer )
					self.attrIntonateTimer = 0

					# 施法中断通知
					self.onSpellInterrupted()
					# 通知all client，结束当前的施法动作
					self.planesAllClients( "spellInterrupted", ( self.attrIntonateSkill.getID(), reason ) )
					# 重置attrIntonateSkill(吟唱)技能，
					# 属性attrIntonateTarget不重置似乎也可以，所以暂时没有重置这些属性。
					self.attrIntonateSkill = None

		if self.attrHomingSpell:
			if self.attrHomingSpell.canInterruptSpell( reason ):
				INFO_MSG( "HomingSpell %i interrupted. reason: %s" % (self.attrHomingSpell.getID(), reason) )
				self.planesAllClients( "spellInterrupted", ( self.attrHomingSpell.getID(), reason ) )
				self.delHomingSpell( reason )



	def onSpellInterrupted( self ):
		"""
		当施法被打断时的通知；
		可以通过self.attrIntonateTarget、self.attrIntonateSkill获得当前的施法目标、位置以及法术实例
		"""
		self.attrIntonateSkill.onSpellInterrupted( self )

	def addCastQueue( self, skill, target, delay ):
		"""
		由于法术的施放有可能不存在目标（只有位置），对于这一类的情况下伤害延迟就无法定位目标了，
		因此技能的延迟只能放在施法者身上，而且只有在延迟时间到了以后才能开始计算伤害，
		当然，如果在这期间目标不见了我们则忽略该spell。

		参数spellID和position其实只会存在一个，具体怎么使用由spell自己决定。

		@type     skill: SKILL
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
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
				# 获取receiver
				target = delayData["target"]
				# 获取spell实例
				spell = delayData["skill"]
				# 这里不再判断法术到达后的距离等检测了。
				CPU_CostCal( csdefine.CPU_COST_SKILL, csdefine.CPU_COST_SKILL_ARRIVE, spell.getID(), className )
				spell.onArrive( self, target )
				CPU_CostCal( csdefine.CPU_COST_SKILL, csdefine.CPU_COST_SKILL_ARRIVE, spell.getID(), className )
				return	# 只处理第一个找到的

	def cancelSpellMoveEffect( self, casterID, skillID ):
		"""
		取消作用效果移动技能的接下来的Timmer回调
		并通知客户端
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

		在此处，我们需要找到相应的skill，并调用skill.use()方法进行施放法术。
		"""
		target = self.attrIntonateTarget

		#INFO_MSG( "--> %i: spellID = %i, targetID = %i, position =" % ( self.id, self.attrIntonateSkill.getID(), targetID ), position  )
		skill = self.attrIntonateSkill
		state = skill.castValidityCheck( self, target )
		if state != csstatus.SKILL_GO_ON:
			self.interruptSpell( state )
			return

		# 重置attrIntonateSkill(吟唱)技能，
		# 属性attrIntonateTarget不重置似乎也可以，所以暂时没有重置这些属性。
		self.attrIntonateSkill = None
		self.attrIntonateTimer = 0

		# 开始施放效果
		skill.cast( self, target )

	def onSkillCastOver( self, spellInstance, target ):
		"""
		virtual method.
		释放技能完成。

		@param  spellInstance: 技能实例
		@type   spellInstance: SPELL
		@param  target: 技能目标
		@type   target: SkillImplTargetObj
		"""
		pass	# 默认啥都不做

	def onSkillArrive( self, spellInstance, receivers ):
		"""
		virtual method.
		技能效果已经到达所有目标

		@param  spellInstance: 技能实例
		@type   spellInstance: SPELL
		@param  receivers: 所有受到这个技能影响的entity
		@type   receivers: List
		"""
		for receiver in receivers:
			self.onSkillArriveReceiver( spellInstance, receiver )

	def onSkillArriveReceiver( self, spellInstance, receiver ):
		"""
		virtual method.
		技能效果已经到达某个目标

		@param  spellInstance: 技能实例
		@type   spellInstance: SPELL
		@param  receiver: 受到这个技能影响的entity
		@type   receiver: entity
		"""
		pass

	def onSkillCastOverTarget( self, spellInstance, target ):
		"""
		virtual method.
		释放技能完成。

		@param  spellInstance: 技能实例
		@type   spellInstance: SPELL
		@param  target: 目标entity
		@type   target: Entity
		"""
		pass

	def receiveOnReal( self, casterID, skill ):
		"""
		Define and virtual method.
		接收某个spell的效果。

		@param casterID: 施法者
		@type  casterID: Entity
		@param    skill: 技能实例
		@type     skill: SKILL
		"""
		try:
			caster = BigWorld.entities[casterID]
		except KeyError:
			caster = None
		skill.receive( caster, self )

	def onChargeOver( self, controllerID, userData ):
		"""
		排队冲锋给玩家造成的速度提成结束
		"""
		self.calcMoveSpeed()

	def requestPlaySkill( self, sourceID, skillID):
		"""
		define method
		客户端申请播放技能
		"""
		if not self.hackVerify_( sourceID ) : return
		skillIDs = self.queryTemp("TEL_SKILLS",[])
		if skillID in skillIDs and self.hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT ) :
			self.spellTarget( skillID, self.id )

	def requestClearBuffer( self, sourceID ):
		"""
		define method
		客户端申请结束buff 目前只用在结束飞翔传送buff
		"""
		if not self.hackVerify_( sourceID ) : return
		self.clearBuff( [ csdefine.BUFF_INTERRUPT_TELEPORT_FLY ] )
	# --------------------------------------------------------
	# HomingSpell about
	# --------------------------------------------------------
	def addHomingSpell( self, skill ):
		"""
		添加一个引导技能
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
		引导技能的tick响应
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
		删除一个引导技能
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
		释放技能检测是否删除引导技能
		"""
		if not self.attrHomingSpell: return
		# 引导技能本身的自己能触发不删除引导技能
		if skillInstance.getID() in self.attrHomingSpell.getChildSpellIDs(): return
		self.delHomingSpell( csstatus.SKILL_INTERRUPTED_BY_SPELL_2 )

	def inHomingSpell( self ):
		"""
		检查是否正在引导技能中
		"""
		return self.attrHomingSpellTickTimer != 0

	# --------------------------------------------------------
	#triggerSpell about 新的触发连续技能 add by wuxo 2012-2-8
	# --------------------------------------------------------

	def addTriggerSpell( self, skillParentID, skillID ):
		"""
		添加一个引导技能
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
		触发技能的持续时间到
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
		改变一个cooldown的类型

		@type  typeID: INT16
		@type timeVal: INT32
		"""
		self.attrCooldowns[typeID] = ( lastTime, totalTime, endTimeVal )

	def getCooldown( self, typeID ):
		"""
		virtual method.
		获取一类cooldown的时间值，如果指定类型不存在则返回0

		@rtype: 结束时间INT32
		"""
		try:
			return self.attrCooldowns[typeID][2]
		except KeyError:
			return 0

	def requestCooldowns( self, srcEntityID ):
		"""
		Exposed method.
		发送自身所有的Cooldown到请求者所在的client
		"""
		if srcEntityID == self.id:
			client = self.client	# 玩家自己请求
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
		请求自己的 colldown，更新客户端( hyw -- 2008.06.10 )
		"""
		self.requestCooldowns( self.id )
		self.client.onInitialized( csdefine.ROLE_INIT_COLLDOWN )


	# --------------------------------------------------------
	# buff about
	# --------------------------------------------------------
	def requestSelfBuffs( self ) :
		"""
		请求自己的 buff，更新客户端( hyw -- 2008.06.10 )
		"""
		self.requestBuffs( self.id )
		self.client.onInitialized( csdefine.ROLE_INIT_BUFFS )

	def requestBuffs( self, srcEntityID ):
		"""
		Exposed method.
		发送自身所有的buff到请求者所在的client
		"""
		if srcEntityID == self.id:
			client = self.client	# 玩家自己请求
		else:
			try:
				entity = BigWorld.entities[srcEntityID]
			except KeyError:
				return
			client = entity.clientEntity( self.id )

		for buff in self.attrBuffs:
			#检查是否需要客户端显示等其他操作
			if buff["sourceType"] != csdefine.BUFF_ORIGIN_SYSTEM:
				client.onReceiveBuff( buff )


	def buffReload( self ):
		"""
		重新使Buff生效。用于Role初始化完属性后，将保存的buff激活。
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
		改变某个索引位置的BUFF状态
		@param index: 该BUFF索引位置
		@param state:状态
		"""
		assert self.isReal(), "attrBuffs index %i, addState:%i" % ( index, state )
		DEBUG_MSG( "attrBuffs index %i, addState:%i" % ( index, state ) )
		buffData = self.attrBuffs[ index ]
		buffData[ "skill" ].onAddState( self, buffData, state )
		buffData[ "skill" ] = buffData[ "skill" ]	# 重新赋值，使其它重新广播给其它的ghost，否则可能会有问题
		buffData[ "state" ] |= state

	def removeBuffState( self, index, state ):
		"""
		改变某个索引位置的BUFF状态
		@param index: 该BUFF索引位置
		@param state:状态
		"""
		assert self.isReal(), "attrBuffs index %i, removeState:%i" % ( index, state )
		DEBUG_MSG( "attrBuffs index %i, removeState:%i" % ( index, state ) )
		buffData = self.attrBuffs[ index ]
		buffData[ "skill" ].onRemoveState( self, buffData, state )
		buffData[ "skill" ] = buffData[ "skill" ]	# 重新赋值，使其它重新广播给其它的ghost，否则可能会有问题
		buffData[ "state" ] &= ~state

	def hasState( self, buff, state ):
		"""
		是否存在标记。
			@return	:	标记字
			@rtype	:	bool
		"""
		return buff[ "state" ] & state != 0

	def clearBuff( self, reasons ):
		"""
		define method
		去除所有Buff。 BUFF_INTERRUPT_NONE 无条件执行
		"""
		assert self.isReal(), "%s" % str( reasons )
		for idx in xrange( len( self.attrBuffs ) - 1, -1, -1 ):
			try:
				self.removeBuff( idx, reasons )
			except IndexError:
				continue

	def onBuffTick( self, timerID, cbID ):
		"""
		效果每次作用。
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

			# 在此处做一个容错处理，我们不能保证在buff的doLoop()里不会出现一些必要的（或人为失误的）传送，
			# 因此，在这里必须对这种情况进行处理，如果确实存在了这样的情况，我们直接返回，以期待下次的处理。
			# 用assert而不用if，是为了能通过简单的日志过滤方式发现问题。
			try:
				assert self.isReal(), "%s" % str( dict( buff ) )
			except:
				EXCEHOOK_MSG( "onBuffTick warning" )
				return

			self.currBuffTickIndex -= 1

	def removeBuff( self, index, reasons ):
		"""
		从列表中去除一个Buff并通知客户端。
		@param index: BUFF所在的索引
		@param reasons:请求取消该BUFF的理由 [中断码]
		"""
		assert self.isReal(), "remove a buff, index:%i, reasons:%s" % ( index, str( reasons ) )
		if self.isDestroyed:
			return False

		# 如果某个buff A在doLoop中移除了buff B,然后buff A的doLoop返回假时，就会造成这种情况。
		# 这里仅仅做日志，而不做任何修正是因为在下一轮buffTick中buff A会被正常移除 by mushuang
		if index >= len( self.attrBuffs ):
			ERROR_MSG( "Buff already removed( idx: %s, len( attrBuffs ) = %s )"%( index, len( self.attrBuffs ) ) )
			ERROR_MSG( "Entity type: %s, id: %s"%( self, self.id ) )
			return False

		buff = self.getBuff( index )
		spell = buff["skill"]

		if csdefine.BUFF_INTERRUPT_NONE not in reasons: # BUFF_INTERRUPT_NONE 无条件执行
			if not spell.cancelBuff( reasons ):			# 取消BUFF失败 返回信息
				return False

		# 由于onBuffTick->doLoop中可能会导致另一个buff被删除，那么循环中使用原始的idx索引进行删除就肯定是错误的了
		# 在这里发现要删除的index小于循环的当前index时就变动偏移量
		if index < self.currBuffTickIndex:
			self.currBuffTickIndex -= 1

		self.attrBuffs.pop( index )
		spell.doEnd( self, buff )
		self.onRemoveBuff( buff )

		DEBUG_MSG( "remove a buff[%i], index:%i" % ( spell.getBuffID(), buff["index"] ) )

		# 检查timer是否还有存在的必要, 如果没有则会被去除
		if self.buffTimer != 0:
			if self.state == csdefine.ENTITY_STATE_DEAD or len( self.attrBuffs ) == 0:
				self.cancel( self.buffTimer )
				self.buffTimer = 0

		return True

	def removeBuffByID( self, skillID, reasons ):
		"""
		删除第一个与skillID相同的buff
		@param reasons:请求取消该BUFF的理由
		"""
		for index, buff in enumerate( self.attrBuffs ):
			if buff["skill"].getID() == skillID:
				self.removeBuff( index, reasons )
				return

		ERROR_MSG( "%i: skillID %i not found in buffs." % (self.id, skillID) )

	def removeBuffByBuffID( self, buffID, reasons ):
		"""
		删除第一个与此buffID相同的buff
		@buffID：buff的ID
		@reasons: 移除的原因，参考csdefine.BUFF_INTERRUPT_XXX，注意，此参数必须是一个可遍历的结构比如list或者tuple
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
		删除第一个与skillID相同的uid
		@param reasons:请求取消该BUFF的理由
		"""
		for index, buff in enumerate( self.attrBuffs ):
			if buff["skill"].getUID() == uid:
				self.removeBuff( index, reasons )
				return

		ERROR_MSG( "%i: skillUID %i not found buff." % (self.id, uid) )

	def removeBuffByIndex( self, index, reasons ):
		"""
		按照buff索引删除一个buff
		@param reasons:请求取消该BUFF的理由
		"""
		for idx, buff in enumerate( self.attrBuffs ):
			if buff["index"] == index:
				self.removeBuff( idx, reasons )
				return
		ERROR_MSG( "%i: skillUID index: %i not found buff." % (self.id, index) )

	def removeAllBuffByID( self, skillID, reasons ):
		"""
		删除所有与skillID相同的buff
		@param reasons:请求取消该BUFF的理由
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
		删除所以由ID是skillID的技能触发的buff
		"""
		# 注：self.attrBuffs是<type 'PyArrayDataInstance'>，对齐使用完整切片复制，
		# 即：self.attrBuffs[:]得到的是其本身，即同一个实例，与普通列表不一样。
		for idx in xrange( len(self.attrBuffs)-1, -1, -1 ):
			buff = self.attrBuffs[ idx ]
			if buff["skill"].getSourceSkillID() == skillID:
				self.removeBuff( idx, reasons )

	def removeBuffBySkillIDAndSourceIndex( self, skillID, index, reasons ):
		"""
		删除第一个由id是skillID添加的且在技能中的索引是index的buff
		"""
		for idx in xrange( len(self.attrBuffs)-1, -1, -1 ):
			buff = self.attrBuffs[ idx ]
			if buff["skill"].getSourceSkillID() == skillID\
			and buff["skill"].getSourceSkillIndex() == index:
				self.removeBuff( idx, reasons )
				break

	def removeSkillLinkBuffs( self, skillID, reasons ):
		"""
		删除由ID是skillID的技能添加的buff
		注：使用此方法时要注意，部分buff是有触发概率限制的
		"""
		for buffData in g_skills[skillID].getBuffsLink():
			sourceIndex = buffData.getBuff().getSourceSkillIndex()
			self.removeBuffBySkillIDAndSourceIndex( skillID, sourceIndex, reasons )

	def addBuff( self, buff ):
		"""
		添加一个Buff。

		@param buff			:	instance of BUFF
		@type  buff			:	BUFF
		"""
		assert self.isReal(), "add a buff, %s" % str( dict( buff ) )
		# phw 2009-10-15: 为了查找buff偶尔会出时间超长的原因，在此处加入判断调试信息，
		# 将来修正后下面的代码需要删除
		# 如果将来有玩家报告buff有问题，而这里没有检查出来，
		# 那说明bigworld.time()很可能有bug，在某一时间段内会突然变成一个很大的值。
		"""
		try:
			# 如果结束时间大于24小时则输出错误日志 3600 * 24 * csconst.SERVER_TIME_AMEND
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
		产生一个新的buffindex
		"""
		index = self.lastBuffIndex
		self.lastBuffIndex += 1
		return index

	def getBuffIndexsByType( self, buffType, effectType ):
		"""
		查找指定类型的所有buff索引。

		@return: 找到则返回相应的索引列表，找不到则返回[]
		"""
		buffs = []
		for index, buff in enumerate( self.attrBuffs ):
			if buff["skill"].getBuffType() == buffType and buff["skill"].getEffectState() == effectType:
				buffs.append( index )

		return buffs

	def getBuffIndexByType( self, buffType ):
		"""
		查找指定类型的第一个buff索引。

		@return: 找到则返回相应的索引列表，找不到则返回-1
		"""
		for index, buff in enumerate( self.attrBuffs ):
			if buff["skill"].getBuffType() == buffType:
				return index

		return -1

	def getBuffIndexsBySourceType( self, buffSourceType ):
		"""
		查找指定类型的所有buff索引。 BUFF小类

		@return: 找到则返回相应的索引列表，找不到则返回[]
		"""
		buffs = []
		for index, buff in enumerate( self.attrBuffs ):
			if buff["skill"].getSourceType() == buffSourceType:
				buffs.append( index )

		return buffs

	def getBuffIndexsByEffectType( self, effectType ):
		"""
		查找指定类型的所有buff索引。 BUFF性质类型  恶性或良性

		@return: 找到则返回相应的索引列表，找不到则返回[]
		"""
		buffs = []
		for index, buff in enumerate( self.attrBuffs ):
			if buff["skill"].getEffectState() == effectType:
				buffs.append( index )

		return buffs

	def findBuffsByBuffID( self, buffID ):
		"""
		查找指定类型的所有buff索引。 通过BUFFID寻找

		@return: 找到则返回相应的索引列表，找不到则返回[]
		"""
		buffs = []
		for index, buff in enumerate( self.attrBuffs ):
			if buff["skill"].getBuffID() == buffID:
				buffs.append( index )

		#buffs.reverse() 底层不进行此操作
		return buffs

	def removeAllBuffByBuffID( self, buffID, reasons ):
		"""
		删除所有与skillID相同的buff
		@param reasons:请求取消该BUFF的理由
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
		从一组索引中查找剩余时间最短的BUFF索引

		@return: 找到则返回相应的索引
		"""
		timeVal = int( time.time() )
		rm = 0
		index = indexs[0]

		for idx in indexs:
			t = self.getBuff( idx )["persistent"]

			if t == 0:
				continue #忽略无限时间的

			rm1 = t - timeVal
			if rm > rm1:
				rm = rm1
				index = idx

		return index

	def getBuff( self, index ):
		"""
		取得某个位置的buff

		@return: instance of BUFF
		"""
		return self.attrBuffs[index]

	def getBuffByIndex( self, index ):
		"""
		根据 index 属性取得buff

		@return: instance of BUFF
		"""
		for idx, buff in enumerate( self.attrBuffs ):
			if buff["index"] == index:
				return self.attrBuffs[idx]

	def getBuffs( self ):
		"""
		取得所有buffs

		@return: instance of BUFF
		"""
		return self.attrBuffs

	def getBuffByType( self, buffType ):
		"""
		根据buff type获取第一个buff数据

		@return: instance of buff or None if buff not found.
		@rtype:  BUFF
		"""
		for buff in self.attrBuffs:
			if buff["skill"].getBuffType() == buffType:
				return buff

		return None

	def getVehicleBuffs( self ):
		"""
		获得玩家身上的全部骑宠buff实例
		"""
		buffs = []
		for index in self.currentVehicleBuffIndexs:
			buff = self.getBuffByIndex( index )
			buffs.append(buff)
		return buffs

	def getVehicleBuffByIndex( self, idx ):
		"""
		根据索引获得玩家身上的单个骑宠buff实例
		"""
		for index in self.currentVehicleBuffIndexs:
			if index != idx:
				continue
			return self.getBuffByIndex( index )

	def spellNone( self, skillID ):
		"""
		不需要目标和位置的施法方式（以自己为中心施法）
		@param  skillID: 法术标识符
		@type   skillID: INT16
		"""
		return self.castSpell( skillID, SkillTargetObjImpl.createTargetObjPosition( self.position ) )

	def spellTarget( self, skillID, targetID ):
		"""
		向一个entity施法
		@param  skillID: 法术标识符
		@type   skillID: INT16
		@param targetID: 目标entityID
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
		向一个位置施法
		@param  skillID: 法术标识符
		@type   skillID: INT16
		@param position: 目标位置
		@type  position: VECTOR3
		"""
		return self.castSpell( skillID, SkillTargetObjImpl.createTargetObjPosition( position ) )

	def systemCastSpell( self, skillID ) :
		"""
		defined method
		系统要对目标施放某个技能，此类技能是系统对玩家施放的技能，无施法者
		@param	skillID		: 技能ID
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
		远程装载一个技能
		"""
		skill.attach( self )

	def detachSkillOnReal( self, skill ):
		"""
		Define method.
		远程卸载一个技能
		"""
		skill.detach( self )

	def findBuffByBuffID( self, buffID ):
		"""
		通过buffid找到某个buff
		"""
		for buffData in self.attrBuffs:
			if buffData["skill"].getBuffID() == buffID:
				return buffData
		return None


	def findBuffByID( self, id ):
		"""
		查找指定技能对应的BUFF的ID。

		@return: buff实例
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
		连击技能被目标抵抗
		"""
		self.client.onHomingSpellResist( id )

	def onBuffMiss( self, receiver, skill ):
		"""
		buff未命中
		"""
		pass

	def onBuffResist( self, receiver, buff ):
		"""
		buff被抵抗
		"""
		pass

	def onBuffResistHit( self, buff ):
		"""
		抵抗了buff效果
		"""
		pass
		
	def rotateToSpellTarget( self, target ):
		"""
		旋转方向
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_CANT_ROTATE_IN_FIGHT_STATE ):
			return

		# 转向处理, 需要精确的方向
		position = target.getObjectPosition()
		disPos = position - self.position

		if math.fabs( disPos.yaw ) > 0.0:
			self.rotateToPos( position )

	# --------------------------------------------------------
	# 一些特殊的buff处理
	# --------------------------------------------------------
	def getFlameWay( self, loopTime ):
		"""
		生成火焰路径（Buff_299004）
		"""
		if self.flameWayTimer == 0:
			self.flameWayTimer = self.addTimer( 0, loopTime, ECBExtend.FLAME_WAY_TIMER_CBID )

	def onFlameWayTimer( self, timerID, cbID ):
		"""
		每个火焰Tick
		"""
		if self.isDestroyed: return
		if not self.queryTemp( "FLAME_MOVE_EFFECTIVE", False ):	 # 只有移动才生效
			if not self.isMoving(): return
		dict = self.queryTemp( "FLAME_TRAP_DICT", {} )
		if not dict: return			#如果getFlameWay回调时已经doEnd，火焰路径已经被删除，就会报错。改为被删除的话就不继续执行了。GRL
		trap = BigWorld.createEntity( "SkillTrap", self.spaceID, self.position, self.direction, dict )
		skillID = self.queryTemp( "FLAME_SKILLID", 0 )
		if not skillID: return
		trap.trapSpellTarget( skillID, trap, trap )	# 对自身使用技能

	def delFlameWay( self ):
		"""
		销毁火焰路径（Buff_299004）
		"""
		if self.flameWayTimer != 0:
			self.cancel( self.flameWayTimer )
			self.flameWayTimer = 0
		self.removeTemp( "FLAME_TRAP_DICT" )
		self.removeTemp( "FLAME_SKILLID" )
		self.removeTemp( "FLAME_MOVE_EFFECTIVE" )

	def detachNotNeedManaEffect( self ):
		"""
		移除不需要消耗魔法标记
		"""
		if not self.queryTemp( "NOT_NEED_MANA", False ): return
		self.removeTemp( "NOT_NEED_MANA" )

# SpellUnit.py
