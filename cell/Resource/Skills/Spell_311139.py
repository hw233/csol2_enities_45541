# -*- coding: gb18030 -*-

# 系统技能，生成一个AreaRestrictTransducer的entity(陷阱功能entity)，在施放者位置

import BigWorld
import csdefine
import csstatus
from SpellBase import *
from Spell_CastTotem import Spell_CastTotem

class Spell_311139( Spell_CastTotem ):
	"""
	系统技能
	响应范围2米，作用范围3米5人，距离施放者超过50米失效。	持续30秒后消失，最多放置4个
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_CastTotem.__init__( self )

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
		state = Spell_CastTotem.useableCheck( self, caster, target )
		if state != csstatus.SKILL_GO_ON:	# 先检查cooldown等条件
			return state
			
		count = 0
		for entity in caster.entitiesInRangeExt( 50.0, "SkillTrap", caster.position ):
			if entity.casterID == caster.id and entity.originSkill == self.getID():
				count += 1
				
		if count >= 4:
			return csstatus.SKILL_UNKNOW
		
		return state