# -*- coding: gb18030 -*-

"""
Spell技能类。
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import csstatus
import csdefine
from gbref import rds
from Time import Time

class Spell_Avoidance( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.casterMoveDistance = 0.0	#冲刺距离
		self.casterMoveSpeed    = 0.0	#冲刺速度
		self.forbidUseBuffs = []
		self.buffTimeBefore = -1
		self.buffTimeAfter  = -1
		
	def init( self, data ):
		"""
		"""
		Spell.init( self, data )
		param2 = data["param2"].split(";")
		if len( param2 ) >= 2:
			self.casterMoveSpeed = float( param2[0] )
			self.casterMoveDistance = float( param2[1] )
		param1 = data["param1"].split(";")
		self.forbidUseBuffs = [ int( i ) for i in param1 ]
		if data["param3"] != "" :
			self.buffTimeBefore = int(data["param3"])
		if data["param4"] != "" :
			self.buffTimeAfter  = int(data["param4"])
		
	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		if hasattr( caster, "state" ):
			if caster.state == csdefine.ENTITY_STATE_DEAD:	# 对施法者是否死亡的判断
				return csstatus.SKILL_IN_DEAD
		
		#以下为特殊判断 当拥有以下buff时 无法释放
		for index, buff in enumerate( caster.attrBuffs ):
			if int(buff["skill"].getBuffID()) in self.forbidUseBuffs:
				return csstatus.SKILL_CANT_CAST
			#if int(buff["skill"].getBuffID()) == 108007:
				#leaveTime = buff["persistent"] - Time.time()
				#disTime = buff["skill"].getPersistent() - leaveTime
				#if self.buffTimeBefore > 0 and self.buffTimeBefore >= disTime:
					#return csstatus.SKILL_CANT_CAST
				#if self.buffTimeAfter > 0 and self.buffTimeAfter <= disTime:
					#return csstatus.SKILL_CANT_CAST
			
		# 检查目标是否符合
		state = self.validTarget( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# 检查施法者的消耗是否足够
		state = self._checkRequire( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		if caster.intonating():
			return csstatus.SKILL_INTONATING

		# 检查玩家是否处于竞技场死亡隐身或GM观察者状态
		player = BigWorld.player()
		if caster == player:
			if caster.isDeadWatcher() or caster.isGMWatcher():
				return csstatus.SKILL_NOT_IN_POSTURE

		# 检查技能cooldown 根据快捷栏变色的需求调整技能条件的判断顺序 这个只能放最后
		if not self.isCooldown( caster ):
			return csstatus.SKILL_NOT_READY
		#if caster.isInHomingSpell:
		#	return csstatus.SKILL_CANT_CAST
		
		
		return csstatus.SKILL_GO_ON
	
	def cast( self, caster, targetObject ) :
		"""
		virtual method
		系统施放，没有吟唱体，所以都是瞬发
		"""
		if caster.id == BigWorld.player().id:
			caster.stopMove()
		Spell.cast( self, caster, targetObject )
		