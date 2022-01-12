# -*- coding: gb18030 -*-
#
# $Id: Spell_PhysSkill.py,v 1.18 2008-09-04 07:46:27 kebiao Exp $

"""
持续性效果
"""

import random
import csdefine
import csstatus
from SpellBase import *
import BigWorld
import csconst
from bwdebug import *
import SkillTargetObjImpl

class Spell_ElemDamage( CombatSpell ):
	"""
	元素伤害技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		CombatSpell.__init__( self )
		self._damageType = csdefine.DAMAGE_TYPE_ELEM				# 伤害类别

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		CombatSpell.init( self, dict )

	def getType( self ):
		"""
		取得基础分类类型
		这些值是BASE_SKILL_TYPE_*之一
		"""
		return csdefine.BASE_SKILL_TYPE_ELEM

	def calcSkillHitStrength( self, source,receiver, dynPercent, dynValue ):
		"""
		virtual method.
		计算技能攻击力
		方式1：技能攻击力（总公式中的基础值）=技能本身的攻击力+角色的物理攻击力
		带入总公式中就是：（技能本身的攻击力+角色物理攻击力）*（1+物理攻击力加成）+物理攻击力加值
		@param source:	攻击方
		@type  source:	entity
		@param dynPercent:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加成
		@param  dynValue:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加值
		"""
		return 0

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
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
		# 防止其他原因导致的不可施法
		if caster.actionSign( csdefine.ACTION_FORBID_SPELL_PHY ):
			return csstatus.SKILL_CANT_CAST
		return CombatSpell.useableCheck( self, caster, target )

