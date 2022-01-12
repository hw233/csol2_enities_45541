# -*- coding: gb18030 -*-

from Spell_PhysSkillImprove import Spell_PhysSkillImprove
import csdefine
import csstatus
from bwdebug import *
import csarithmetic
import SkillTargetObjImpl
import copy

class Spell_323079( Spell_PhysSkillImprove ):
	# 跳砍
	def __init__( self ):
		Spell_PhysSkillImprove.__init__( self )
		self.param2 = 6.0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell_PhysSkillImprove.init( self, dict )
		param2 = dict["param2"]
		if param2 != "":
			self.param2 = float( param2 )

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
		if csarithmetic.checkSkillCollide( caster.spaceID, caster.position, target.getObjectPosition() ) != None:
			return csstatus.SKILL_CANT_ARRIVAL
		if caster.effect_state & csdefine.EFFECT_STATE_FIX > 0:
			return csstatus.SKILL_UNKNOW
		return Spell_PhysSkillImprove.useableCheck( self, caster, target )

	def cast( self, caster, target ):
		"""
		virtual method.
		正式向一个目标或位置施放（或叫发射）法术，此接口通常直接（或间接）由intonate()方法调用。

		注：此接口即原来旧版中的castSpell()接口

		@param     caster: 使用技能的实体
		@type      caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		caster.move_speed = self.param2
		caster.updateTopSpeed()
		Spell_PhysSkillImprove.cast( self, caster, target )

	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		法术抵达目标通告。在默认情况下，此处执行可受术人员的获取，然后调用receive()方法进行对每个可受术者进行处理。
		注：此接口为旧版中的receiveSpell()

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell_PhysSkillImprove.onArrive( self, caster, target )
		caster.calcMoveSpeed()

class Spell_jumpAttck( Spell_PhysSkillImprove ):
	# 跳砍对目标
	def __init__( self ):
		Spell_PhysSkillImprove.__init__( self )
		self.param2 = 6.0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell_PhysSkillImprove.init( self, dict )
		param2 = dict["param2"]
		if param2 != "":
			self.param2 = float( param2 )

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
		if csarithmetic.checkSkillCollide( caster.spaceID, caster.position, target.getObjectPosition() ) != None:
			return csstatus.SKILL_CANT_ARRIVAL
		flag = Spell_PhysSkillImprove.useableCheck( self, caster, target )
		if not target:
			dstPos = caster.position
		else:
			dstPos = target.getObjectPosition()
		self._target = copy.deepcopy(SkillTargetObjImpl.createTargetObjPosition(dstPos))
		return flag

	def use( self, caster, target ):
		"""
		virtual method.
		请求对 target/position 施展一个法术，任何法术的施法入口由此进。
		dstEntity和position是可选的，不用的参数用None代替，具体看法术本身是对目标还是位置，一般此方法都是由client调用统一接口后再转过来。
		默认啥都不做，直接返回。
		注：此接口即原来旧版中的cast()接口
		@param   caster: 施法者
		@type    caster: Entity

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell_PhysSkillImprove.use( self, caster, self._target )
		
	def cast( self, caster, target ):
		"""
		virtual method.
		正式向一个目标或位置施放（或叫发射）法术，此接口通常直接（或间接）由intonate()方法调用。

		注：此接口即原来旧版中的castSpell()接口

		@param     caster: 使用技能的实体
		@type      caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		caster.move_speed = self.param2
		caster.updateTopSpeed()
		Spell_PhysSkillImprove.cast( self, caster, self._target )

	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		法术抵达目标通告。在默认情况下，此处执行可受术人员的获取，然后调用receive()方法进行对每个可受术者进行处理。
		注：此接口为旧版中的receiveSpell()

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell_PhysSkillImprove.onArrive( self, caster, target )
		caster.calcMoveSpeed()
