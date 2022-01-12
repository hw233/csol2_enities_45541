# -*- coding: gb18030 -*-
#
# edit by wuxo

"""
触发连续技能类。
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import skills as Skill

class Spell_TriggerSkill( Spell ):
	def __init__( self ):
		"""
		从python dict构造SkillBase
		"""
		Spell.__init__( self )
		self.parentID = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		if dict[ "param2" ] != "":
			self.parentID = int ( dict[ "param2" ] )

	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )
		
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
		return Spell.useableCheck( self, caster, target )
		
		
	def isTriggerSkill( self ):
		"""
		判断是否触发连续技能 	
		@return: BOOL
		"""
		return True
	