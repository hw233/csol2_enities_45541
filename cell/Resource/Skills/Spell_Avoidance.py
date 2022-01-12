# -*- coding:gb18030 -*-

#edit by wuxo 2013-2-1

import Math
import math
import csdefine
import csarithmetic
import ECBExtend
import csstatus
from SpellBase import *
from Spell_BuffNormal import Spell_BuffNormal
import time

class Spell_Avoidance( Spell_BuffNormal ):
	"""
	主动闪避技能
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		#施法者位移数据
		self.casterMoveDistance = 0.0	#冲刺距离
		self.casterMoveSpeed    = 0.0	#冲刺速度
		self._triggerBuffInterruptCode = []
		self.forbidUseBuffs = []  #身上带有哪些buff，将禁止使用此技能
		self.buffTimeBefore = -1
		self.buffTimeAfter  = -1
		
	def init( self, data ):
		"""
		"""
		Spell_BuffNormal.init( self, data )
		param1 = data["param1"].split(";")
		self.forbidUseBuffs = [ int( i ) for i in param1 ]	
		param2 = data["param2"].split(";")
		if len( param2 ) >= 2:
			self.casterMoveSpeed = float( param2[0] )
			self.casterMoveDistance = float( param2[1] )
		for val in data[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )
		if data["param3"] != "" :
			self.buffTimeBefore = int(data["param3"])
		if data["param4"] != "" :
			self.buffTimeAfter  = int(data["param4"])
		
	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		#以下为特殊判断 当拥有以下buff时 无法释放
		for index, buff in enumerate( caster.attrBuffs ):
			if int(buff["skill"].getBuffID()) in self.forbidUseBuffs:
				return csstatus.SKILL_CANT_CAST
			#if int(buff["skill"].getBuffID()) == 108007:
				#leaveTime = buff["persistent"] - time.time()
				#disTime = buff["skill"]._persistent - leaveTime
				#if self.buffTimeBefore > 0 and self.buffTimeBefore >= disTime:
					#return csstatus.SKILL_CANT_CAST
				#if self.buffTimeAfter > 0 and self.buffTimeAfter <= disTime:
					#return csstatus.SKILL_CANT_CAST
		# 检查技能cooldown
		if not self.isCooldown( caster ):
			return csstatus.SKILL_NOT_READY

		# 施法需求检查
		state = self.checkRequire_( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		# 施法者检查
		state = self.castValidityCheck( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# 检查目标是否符合法术施展
		state = self.getCastObject().valid( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state
		caster.interruptSpell( csstatus.SKILL_INTERRUPTED_BY_AVOIDANCE )	
		return csstatus.SKILL_GO_ON	
		
	def cast( self, caster, target ) :
		"""
		virtual method
		"""
		caster.setTemp( "AVOIDANCE_FLAG", True ) #增加主动闪避标识
		Spell_BuffNormal.cast( self, caster, target )
		
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		if receiver.isDestroyed:
			return
		caster.clearBuff( self._triggerBuffInterruptCode ) #中断buff
		self.receiveLinkBuff( caster, receiver )	
		