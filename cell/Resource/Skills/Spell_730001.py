# -*- coding: gb18030 -*-

# 系统技能，生成一个AreaRestrictTransducer的entity(陷阱功能entity)，在施放者位置

import BigWorld
import csdefine
import csstatus
from SpellBase import *
from Spell_BuffNormal import Spell_BuffNormal
import csarithmetic

class Spell_730001( Spell_BuffNormal ):
	"""
	运镖强化
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_BuffNormal.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_BuffNormal.init( self, dict )
		
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
		state = Spell_BuffNormal.useableCheck( self, caster, target )
		if state != csstatus.SKILL_GO_ON:	# 先检查cooldown等条件
			return state
				
		if not target.getObject().isDarting():
			return csstatus.SKILL_CANT_CAST
		
		dartVehicle = BigWorld.entities.get( caster.queryTemp( "dart_id", 0 ), None )
		if not dartVehicle or dartVehicle.spaceID != caster.spaceID or csarithmetic.distancePP3( caster.position, dartVehicle.position ) > 10.0:
			return csstatus.SKILL_CANT_CAST
			
		return state