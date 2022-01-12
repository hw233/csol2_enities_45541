# -*- coding: gb18030 -*-

#目标位置技能
#该类技能起手时即以目标所在位置为技能效果最终作用位置
#edit by wuxo 2012-3-20

import math
import Math
import copy
import random
import csdefine
import csstatus
from SpellBase import *
import csarithmetic
import SkillTargetObjImpl
from Spell_CastTotem import Spell_CastTotem



class Spell_TargetPosition( Spell_CastTotem ):
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_CastTotem.__init__( self )
		self._target = None
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_CastTotem.init( self, dict )
		
		
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
		#处理沉默等一类技能的施法判断
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO  > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		
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
		
		if not target:
			dstPos = caster.position
		else:
			dstPos = target.getObjectPosition()
		dstPos = csarithmetic.getCollidePoint( caster.spaceID, dstPos+(0,5,0), dstPos-( 0,5,0 ) )
		self._target = copy.deepcopy(SkillTargetObjImpl.createTargetObjPosition(dstPos))
		
		caster.setTemp( "TARGETPOSITION", self._target )
		return csstatus.SKILL_GO_ON
		
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
		Spell_CastTotem.use( self, caster, caster.queryTemp( "TARGETPOSITION", None ) )	
		
	def cast( self, caster, target ):
		Spell_CastTotem.cast( self, caster, caster.queryTemp( "TARGETPOSITION", None ) )
		caster.removeTemp( "TARGETPOSITION" )
		

class Spell_TargetPosRandom( Spell_TargetPosition ):
	"""
	目标所在位置为圆心半径为R随机的一个点作为目标点
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_TargetPosition.__init__( self )
		self._target = None
		self.randomRange = 0.0
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_TargetPosition.init( self, dict )
		param =  dict[ "param3" ].split(";")[-1]
		if param != "":
			self.randomRange = float( param )
		
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
		#处理沉默等一类技能的施法判断
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO  > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		
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
		
		if not target:
			dstPos = caster.position
		else:
			dstPos = target.getObjectPosition()
		radius = random.uniform( 0.0, self.randomRange )
		yaw    = random.uniform( 0.0, 2*math.pi )
		direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
		pos = dstPos + radius*direction
		pos = csarithmetic.getCollidePoint( caster.spaceID, pos+(0,5,0), pos-( 0,5,0 ) )
		self._target = copy.deepcopy(SkillTargetObjImpl.createTargetObjPosition( pos ))
		
		caster.setTemp( "TARGETPOSITION", self._target )
		return csstatus.SKILL_GO_ON
		
	