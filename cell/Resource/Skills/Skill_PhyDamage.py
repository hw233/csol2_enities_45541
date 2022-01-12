# -*- coding: gb18030 -*-


import BigWorld
from bwdebug import *

from SpellBase import *
from Skill_Damage import Skill_Damage

import csconst
import csdefine
import csstatus
import random
import CombatUnitConfig
from CombatSystemExp import CombatExp


class Skill_PhyDamage( Skill_Damage ):
	"""
	被动技能伤害类:物理伤害

	目前还不完善,仅加入了目前为止确定的一些行为以适应装备附加属性技能的需求,
	以后需要对被动技能结构进行总体规划.11:14 2008-10-24,wsf
	"""
	def __init__( self ):
		"""
		"""
		Skill_Damage.__init__( self )


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Skill_Damage.init( self, dict )


	def isDoubleHit( self, caster, receiver ):
		"""
		virtual method.
		判断攻击者是否爆击
		return type:bool
		"""
		return random.random() < ( caster.double_hit_probability + ( receiver.be_double_hit_probability - receiver.be_double_hit_probability_reduce ) / csconst.FLOAT_ZIP_PERCENT )


	def calcDoubleMultiple( self, caster ):
		"""
		virtual method.
		计算暴击伤害加倍
		@param caster: 被攻击方
		@type  caster: entity
		@return type:计算后得到的暴击倍数
		"""
		return caster.double_hit_multiple

	def calcHitProbability( self, source, target ):
		"""
		virtual method.
		计算命中率
		物理命中
		物理命中率=1-（0.13-（攻方命中/10000-0.9）+（守方闪避/10000-0.03）-取整（（攻方等级-守方等级）/5）*0.01）
		以上攻方命中为攻击者命中终值，守方闪避为防守方闪避终值。以上计算结果大于1时，取1；小于0.7时，取0.7

		@param source:	攻击方
		@type  source:	entity
		@param target:	被攻击方
		@type  target:	entity
		return type:	Float
		"""
		hitRate = CombatUnitConfig.calcHitProbability( source, target )
		return hitRate > 1 and 1 or max( 0.7, hitRate )

	def calcVictimResist( self, source, target ):
		"""
		virtual method.
		计算被攻击方物理防御减伤
		角色基础物理防御值（总公式中的基础值）=0
		物理防御减伤（总公式中的基础值）=物理防御值/（物理防御值+40*攻击方等级+350）-0.23
		在攻防的计算中，防御值会先换算成防御减伤，然后再和攻击力进行换算。
		@param source:	攻击方
		@type  source:	entity
		@param target:	被攻击方
		@type  target:	entity
		@return: FLOAT
		"""
		exp = CombatExp( source, target )
		val = max( 0.0, exp.getPhysicsDamageReductionRate() )
		if val > 0.95:
			val = 0.95
		return self.calcProperty( val, target.armor_reduce_damage_extra / csconst.FLOAT_ZIP_PERCENT, target.armor_reduce_damage_percent / csconst.FLOAT_ZIP_PERCENT, target.armor_reduce_damage_value / csconst.FLOAT_ZIP_PERCENT )



