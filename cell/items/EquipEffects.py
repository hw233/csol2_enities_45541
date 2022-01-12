# -*- coding: gb18030 -*-

# $Id: EquipEffects.py,v 1.18 2008-09-04 07:44:43 kebiao Exp $

import csconst
from bwdebug import *
from Resource.SkillLoader import g_skills
import math
import CombatUnitConfig


# 随机效果实现
# -----------------------------------------------
# 体质加值
# -----------------------------------------------
class AddValueCorporeity:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		装备属性
		"""
		if owner is None: return
		owner.corporeity_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		卸下属性
		"""
		if owner is None: return
		owner.corporeity_extra -= int( math.ceil( value ) )

class AddPercentCorporeity:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		装备属性
		"""
		if owner is None: return
		owner.corporeity_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		卸下属性
		"""
		if owner is None: return
		owner.corporeity_percent -= int( math.ceil( value ) )
# -----------------------------------------------
# 智力加值
# -----------------------------------------------
class AddValueIntellect:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.intellect_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.intellect_extra -= int( math.ceil( value ) )

class AddPercentIntellect:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.intellect_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.intellect_percent -= int( math.ceil( value ) )

# -----------------------------------------------
# 力量加值
# -----------------------------------------------
class AddValueStrength:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		@
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.strength_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.strength_extra -= int( math.ceil( value ) )

class AddPercentStrength:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		@
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.strength_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.strength_percent -= int( math.ceil( value ) )

# -----------------------------------------------
# 敏捷加值
# -----------------------------------------------
class AddValueDexterity:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.dexterity_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.dexterity_extra -= int( math.ceil( value ) )

class AddPercentDexterity:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.dexterity_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.dexterity_percent -= int( math.ceil( value ) )

# -----------------------------------------------
# 生命加值
# -----------------------------------------------
class AddValueHP:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_Max_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_Max_extra -= int( math.ceil( value ) )

class AddPercentHP:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_Max_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_Max_percent -= int( math.ceil( value ) )

# -----------------------------------------------
# 精力加值
# -----------------------------------------------
class AddValueMP:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_Max_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_Max_extra -= int( math.ceil( value ) )

class AddPercentMP:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_Max_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_Max_percent -= int( math.ceil( value ) )

# -----------------------------------------------
# 物理防御加值
# -----------------------------------------------
class AddValueArmor:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.armor_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.armor_extra -= int( math.ceil( value ) )

class AddPercentArmor:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.armor_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.armor_percent -= int( math.ceil( value ) )

# -----------------------------------------------
# 法术防御加值
# -----------------------------------------------
class AddValueMagicArmor:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_armor_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_armor_extra -= int( math.ceil( value ) )

class AddPercentMagicArmor:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_armor_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_armor_percent -= int( math.ceil( value ) )

# -----------------------------------------------
# 角色物理攻击力
# -----------------------------------------------
class AddValueDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_extra += int( math.ceil( value ) )
		owner.damage_max_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_extra -= int( math.ceil( value ) )
		owner.damage_max_extra -= int( math.ceil( value ) )

class AddPercentDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_percent += int( math.ceil( value ) )
		owner.damage_max_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_percent -= int( math.ceil( value ) )
		owner.damage_max_percent -= int( math.ceil( value ) )

# -----------------------------------------------
# 角色法术攻击力
# -----------------------------------------------
class AddValueMagicDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_extra -= int( math.ceil( value ) )

class AddPercentMagicDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_percent -= int( math.ceil( value ) )

# -----------------------------------------------
# 生命恢复速度
# -----------------------------------------------
class AddValueHPRegen:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_regen_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_regen_extra -= int( math.ceil( value ) )

# -----------------------------------------------
# 精力恢复速度
# -----------------------------------------------
class AddValueMPRegen:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_regen_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_regen_extra -= int( math.ceil( value ) )

# -----------------------------------------------
# 最小攻击力
# -----------------------------------------------
class AddValueDamageMin:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_extra -= int( math.ceil( value ) )

# -----------------------------------------------
# 最大攻击力
# -----------------------------------------------
class AddValueDamageMax:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_max_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_max_extra -= int( math.ceil( value ) )

# -----------------------------------------------
# 物理命中点数
# -----------------------------------------------
class AddValueHit:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.hitProbability_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.hitProbability_extra -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 法术命中点数
# -----------------------------------------------
class AddValueMagicHit:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.magic_hitProbability_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.magic_hitProbability_extra -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 闪避点数
# -----------------------------------------------
class AddValueDodge:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.dodge_probability_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.dodge_probability_extra -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
#  御敌
# -----------------------------------------------
class AddValueReduceRoleD:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.reduce_role_damage_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.reduce_role_damage_extra -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
#  破敌
# -----------------------------------------------
class AddValueAddRoleD:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.add_role_damage_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.add_role_damage_extra -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 物理暴击点数
# -----------------------------------------------
class AddValueDoubleHit:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.double_hit_probability_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.double_hit_probability_extra -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 法术暴击点数
# -----------------------------------------------
class AddValueMagicDoubleHit:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.magic_double_hit_probability_extra+= int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.magic_double_hit_probability_extra -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 招架点数
# -----------------------------------------------
class AddValueResistHit:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.resist_hit_probability_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.resist_hit_probability_extra -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 招架减伤点数
# -----------------------------------------------
class AddValueResistHitDerate:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_hit_derate_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_hit_derate_extra -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 物理伤害减免
# -----------------------------------------------
class AddValueDamageDerate:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_derate_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_derate_extra -= int( math.ceil( value ) )

# -----------------------------------------------
# 法术伤害减免
# -----------------------------------------------
class AddValueMagicDamageDerate:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_derate_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_derate_extra -= int( math.ceil( value ) )
# -----------------------------------------------
# 伤害减免
# -----------------------------------------------
class AddValueAllDerate:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_derate_extra += int( math.ceil( value ) )
		owner.magic_damage_derate_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_derate_extra -= int( math.ceil( value ) )
		owner.magic_damage_derate_extra -= int( math.ceil( value ) )
# -----------------------------------------------
# 特效触发点数
# -----------------------------------------------
class AddValueSpeciallySpring:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		# 15:08 2008-2-22
		pass

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		# 15:08 2008-2-22
		pass
# -----------------------------------------------
# 物理暴击伤害倍数
# -----------------------------------------------
class AddValueDoubleHitMultiple:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.double_hit_multiple_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.double_hit_multiple_value -= int( value * csconst.FLOAT_ZIP_PERCENT )
# -----------------------------------------------
# 法术暴击伤害倍数
# -----------------------------------------------
class AddValueMagicDoubleHitMultiple:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.magic_double_hit_multiple_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.magic_double_hit_multiple_value -= int( value * csconst.FLOAT_ZIP_PERCENT )
# -----------------------------------------------
# 降低对方物理命中点数
# -----------------------------------------------
class AddValueReduceTargetHit:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		# 属性receive_be_hit_value 为负数则降低对方物理命中
		# 为正数就增加对方物理命中
		owner.receive_be_hit_value -= int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.receive_be_hit_value += int( math.ceil( value ) )

# -----------------------------------------------
#降低对方法术命中点数
# -----------------------------------------------
class AddValueReduceTargetMagicHit:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		# 见降低对方物理命中点数
		owner.receive_magic_be_hit_value -= int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.receive_magic_be_hit_value += int( math.ceil( value ) )

# ------------------由于一些策划规则上的冲突 对抗性的加成做8级及以下的等级阻隔 by姜毅-----------------------------
# -----------------------------------------------
# 抵抗沉默点数
# -----------------------------------------------
class AddValueResistChenmo:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		level = owner.level
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.resist_chenmo_probability_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		level = owner.level
		value = CombatUnitConfig.valueToPer( value, owner.level )
		resValue = owner.resist_chenmo_probability_value
		resValue -= int( value * csconst.FLOAT_ZIP_PERCENT )
		if resValue < 0.0:
			owner.resist_chenmo_probability_extra = 0.0
		else:
			owner.resist_chenmo_probability_extra = resValue

# -----------------------------------------------
# 抵抗眩晕
# -----------------------------------------------
class AddValueResistGiddy:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		level = owner.level
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.resist_giddy_probability_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		level = owner.level
		value = CombatUnitConfig.valueToPer( value, owner.level )
		resValue = owner.resist_giddy_probability_value
		resValue -= int( value * csconst.FLOAT_ZIP_PERCENT )
		if resValue < 0.0:
			owner.resist_giddy_probability_extra = 0.0
		else:
			owner.resist_giddy_probability_extra = resValue

# -----------------------------------------------
# 抵抗定身
# -----------------------------------------------
class AddValueResistFix:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		level = owner.level
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.resist_fix_probability_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		level = owner.level
		value = CombatUnitConfig.valueToPer( value, owner.level )
		resValue = owner.resist_fix_probability_value
		resValue -= int( value * csconst.FLOAT_ZIP_PERCENT )
		if resValue < 0.0:
			owner.resist_fix_probability_extra = 0.0
		else:
			owner.resist_fix_probability_extra = resValue

# -----------------------------------------------
# 抵抗睡眠
# -----------------------------------------------
class AddValueResistSleep:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		level = owner.level
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.resist_sleep_probability_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		level = owner.level
		value = CombatUnitConfig.valueToPer( value, owner.level )
		resValue = owner.resist_sleep_probability_value
		resValue -= int( value * csconst.FLOAT_ZIP_PERCENT )
		if resValue < 0.0:
			owner.resist_sleep_probability_extra = 0.0
		else:
			owner.resist_sleep_probability_extra = resValue

# -----------------------------------------------
# 抵抗沉默几率
# -----------------------------------------------
class AddValueResistChenmoOdds:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_chenmo_probability_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_chenmo_probability_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 抵抗眩晕几率
# -----------------------------------------------
class AddValueResistGiddyOdds:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_giddy_probability_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_giddy_probability_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 抵抗定身几率
# -----------------------------------------------
class AddValueResistFixOdds:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_fix_probability_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_fix_probability_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 抵抗睡眠几率
# -----------------------------------------------
class AddValueResistSleepOdds:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_sleep_probability_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_sleep_probability_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 攻击速度
# -----------------------------------------------
class AddValueHitSpeed:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.hit_speed_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.hit_speed_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 移动速度
# -----------------------------------------------
class AddValueMoveSpeed:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.move_speed_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.move_speed_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 攻击距离
# -----------------------------------------------
class AddValueRange:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.range_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.range_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 特效触发率
# -----------------------------------------------
class AddValueSpeciallySpringPro:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		pass

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		pass

# -----------------------------------------------
# 物理暴击率
# -----------------------------------------------
class AddValueDoubleHitPro:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.double_hit_probability_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.double_hit_probability_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 法术暴击率
# -----------------------------------------------
class AddValueMagicDoubleHitPro:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_double_hit_probability_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_double_hit_probability_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 物理被暴击率减免
# -----------------------------------------------
class AddValueBeDoubleHitProReduce:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.be_double_hit_probability_reduce += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.be_double_hit_probability_reduce -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 法术被暴击率减免
# -----------------------------------------------
class AddValueMagicBeDoubleHitProReduce:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.be_magic_double_hit_probability_reduce += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.be_magic_double_hit_probability_reduce -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 物理命中率
# -----------------------------------------------
class AddValueHitPro:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.hitProbability_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.hitProbability_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 法术命中率
# -----------------------------------------------
class AddValueMagicHitPro:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_hitProbability_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_hitProbability_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 武器攻击力
# -----------------------------------------------
class AddValueWeaponDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_value += int( math.ceil( value ) )
		owner.damage_max_value += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_value -= int( math.ceil( value ) )
		owner.damage_max_value -= int( math.ceil( value ) )

# -----------------------------------------------
# 体质加成
# -----------------------------------------------
class AddPercentCorporeity:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.corporeity_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.corporeity_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 智力加成
# -----------------------------------------------
class AddPercentIntellect:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.intellect_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.intellect_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 力量加成
# -----------------------------------------------
class AddPercentStrength:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.strength_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.strength_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 敏捷加成
# -----------------------------------------------
class AddPercentDexterity:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.dexterity_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.dexterity_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 生命加成
# -----------------------------------------------
class AddPercentHP:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_Max_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_Max_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 精力加成
# -----------------------------------------------
class AddPercentMP:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_Max_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_Max_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 物理防御加成
# -----------------------------------------------
class AddPercentArmor:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.armor_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.armor_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 法术防御加成
# -----------------------------------------------
class AddPercentMagicArmor:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_armor_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_armor_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 武器攻击力加成
# -----------------------------------------------
class AddPercentWeaponDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_percent += int( value * csconst.FLOAT_ZIP_PERCENT )
		owner.damage_max_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )
		owner.damage_max_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 角色物理攻击力加成
# -----------------------------------------------
class AddPercentDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_percent += int( value * csconst.FLOAT_ZIP_PERCENT )
		owner.damage_max_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )
		owner.damage_max_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 角色法术攻击力加成
# -----------------------------------------------
class AddPercentMagicDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 生命恢复速度加成
# -----------------------------------------------
class AddPercentHPRegen:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_regen_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_regen_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 精力恢复速度加成
# -----------------------------------------------
class AddPercentMPRegen:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_regen_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_regen_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 物理伤害减免加成
# -----------------------------------------------
class AddPercentDamageDerate:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_derate_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_derate_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 法术伤害减免
# -----------------------------------------------
class AddPercentMagicDamageDerate:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_derate_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_derate_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 伤害减免加成
# -----------------------------------------------
class AddPercentAllDerate:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_derate_percent += int( value * csconst.FLOAT_ZIP_PERCENT )
		owner.magic_damage_derate_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_derate_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )
		owner.magic_damage_derate_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 经验加成
# -----------------------------------------------
class AddPercentMultExp:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.multExp += value

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.multExp -= value

# -----------------------------------------------
# 潜能点加成
# -----------------------------------------------
class AddPercentMultPotential:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.potential_percent += value

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.potential_percent -= value

# -----------------------------------------------
# 移动速度加成
# -----------------------------------------------
class AddPercentMoveSpeed:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.move_speed_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.move_speed_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 攻击速度
# -----------------------------------------------
class AddPercentHitSpeed:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.hit_speed_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.hit_speed_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# 元素相关
# -----------------------------------------------
#-------------火------------------------
class AddHuoDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage -= int(  math.ceil( value ) )

class AddHuoDamageBase:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage_base += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage_base -= int(  math.ceil( value ) )

class AddHuoDamagePercent:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage_percent += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage_percent -= int(  math.ceil( value ) )

class AddHuoDamageExtra:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage_extra += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage_extra -= int(  math.ceil( value ) )

class AddHuoDamageValue:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage_value += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage_value -= int(  math.ceil( value ) )

class AddHuoDR:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio += int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio -= int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()

class AddHuoDRBase:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio_base += int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio_base -= int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()

class AddHuoDRPercent:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio_percent += int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio_percent -= int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()

class AddHuoDRExtra:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio_extra += int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio_extra -= int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()

class AddHuoDRValue:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio_value += int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio_value -= int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()
#-------------玄------------------------
class AddXuanDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage -= int(  math.ceil( value ) )

class AddXuanDamageBase:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage_base += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage_base -= int(  math.ceil( value ) )

class AddXuanDamagePercent:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage_percent += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage_percent -= int(  math.ceil( value ) )

class AddXuanDamageExtra:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage_extra += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage_extra -= int(  math.ceil( value ) )

class AddXuanDamageValue:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage_value += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage_value -= int(  math.ceil( value ) )

class AddXuanDR:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio += int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio -= int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()

class AddXuanDRBase:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio_base += int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio_base -= int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()

class AddXuanDRPercent:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio_percent += int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio_percent -= int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()

class AddXuanDRExtra:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio_extra += int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio_extra -= int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()

class AddXuanDRValue:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio_value += int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio_value -= int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()
#-------------雷------------------------
class AddLeiDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage -= int(  math.ceil( value ) )

class AddLeiDamageBase:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage_base += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage_base -= int(  math.ceil( value ) )

class AddLeiDamagePercent:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage_percent += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage_percent -= int(  math.ceil( value ) )

class AddLeiDamageExtra:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage_extra += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage_extra -= int(  math.ceil( value ) )

class AddLeiDamageValue:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage_value += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage_value -= int(  math.ceil( value ) )

class AddLeiDR:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio += int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio -= int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()

class AddLeiDRBase:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio_base += int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio_base -= int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()

class AddLeiDRPercent:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio_percent += int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio_percent -= int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()

class AddLeiDRExtra:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio_extra += int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio_extra -= int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()

class AddLeiDRValue:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio_value += int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio_value -= int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()
#-------------冰------------------------
class AddBingDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage -= int(  math.ceil( value ) )

class AddBingDamageBase:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage_base += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage_base -= int(  math.ceil( value ) )

class AddBingDamagePercent:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage_percent += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage_percent -= int(  math.ceil( value ) )

class AddBingDamageExtra:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage_extra += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage_extra -= int(  math.ceil( value ) )

class AddBingDamageValue:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage_value += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage_value -= int(  math.ceil( value ) )

class AddBingDR:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio += int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio -= int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()

class AddBingDRBase:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio_base += int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio_base -= int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()

class AddBingDRPercent:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio_percent += int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio_percent -= int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()

class AddBingDRExtra:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio_extra += int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio_extra -= int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()

class AddBingDRValue:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio_value += int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio_value -= int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()
# -----------------------------------------------
# 添加buff
# -----------------------------------------------
class SPEAddBuff:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		#buff 不单独存在，以被动技能的方式添加
		owner.addSkill( value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.removeSKill( value )

# -----------------------------------------------
# 物理击中时触发
# -----------------------------------------------
class SPEHitSpring:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		# 以参数 value 创建一个技能实例
		# 其中技能ID value 就是一个物理击中时触发物理伤害的技能
		# 这个技能附加到玩家身上之后在物理命中的时候会自动调用
		# 当有多个 物理命中时触发物理伤害这种技能存在时，玩家的
		# 物理命中表中只会保存一个ID为value的技能实例，而值则以
		# 累加的方式添加进去。具体做法在对应的技能value做处理
		try:
			skill = g_skills[ value ]
		except KeyError:
			ERROR_MSG( "技能不存在: %i." % value )
			return
		skill = skill.newSelf()
		equip.setTemp( "skillUID", skill.getUID() )
		skill.attach( owner )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		# 通过装备保存的技能UID在玩家的击中列表里面寻找对应的技能并卸载该技能
		# 临时属性 equipEffect_hit_damage 用于保存玩家需要卸载的属性值(下面类似)
		# 在对应的技能实例里面有做相关处理
		#owner.setTemp( "equipEffect_hit_damage", value )
		for skill in owner.springAttackerHitList:
			if skill.getUID() == equip.queryTemp( "skillUID" ):
			 	skill.detach( owner )
			 	return


# -----------------------------------------------
# 法术击中触发
# -----------------------------------------------
class SPEMagicHitSpring:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		try:
			skill = g_skills[ value ]
		except KeyError:
			ERROR_MSG( "技能不存在: %i." % value )
			return
		skill = skill.newSelf()
		equip.setTemp( "skillUID", skill.getUID() )
		skill.attach( owner )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		for skill in owner.springAttackerHitList:
			if skill.getUID() == equip.queryTemp( "skillUID" ):
			 	skill.detach( owner )
			 	return

# -----------------------------------------------
# 被击中时触发
# -----------------------------------------------
class SPEBeHitSpring:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		try:
			skill = g_skills[value]
		except KeyError:
			ERROR_MSG( "技能不存在: %i." % value )
			return
		skill = skill.newSelf()
		equip.setTemp( "skillUID", skill.getUID() )
		skill.attach( owner )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		for skill in owner.springVictimHitList:
			if skill.getUID() == equip.queryTemp( "skillUID" ):
			 	skill.detach( owner )
			 	return

# -----------------------------------------------
# 被暴击时触发
# -----------------------------------------------
class SPEBeDoubleHitSpring:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		try:
			skill = g_skills[ value ]
		except KeyError:
			ERROR_MSG( "不存在技能: %i." % value )
			return
		skill = skill.newSelf()
		equip.setTemp( "skillUID", skill.getUID() )
		skill.attach( owner )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		for skill in owner.springVictimDoubleHitList:
			if skill.getUID() == equip.queryTemp( "skillUID" ):
			 	skill.detach( owner )
			 	return

# -----------------------------------------------
# 物理暴击时触发
# -----------------------------------------------
class SPEDoubleHitSpring:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		try:
			skill = g_skills[ value ]
		except KeyError:
			ERROR_MSG( "不存在技能: %i." % value )
			return
		skill = skill.newSelf()
		equip.setTemp( "skillUID", skill.getUID() )
		skill.attach( owner )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		for skill in owner.springAttackerDoubleHitList:
			if skill.getUID() == equip.queryTemp( "skillUID" ):
			 	skill.detach( owner )
			 	return

# -----------------------------------------------
# 法术暴击时触发
# -----------------------------------------------
class SPEMagicDoubleHitSpring:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		try:
			skill = g_skills[ value ]
		except KeyError:
			ERROR_MSG( "不存在技能: %i." % value )
			return
		skill = skill.newSelf()
		equip.setTemp( "skillUID", skill.getUID() )
		skill.attach( owner )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		for skill in owner.springAttackerDoubleHitList:
			if skill.getUID() == equip.queryTemp( "skillUID" ):
			 	skill.detach( owner )
			 	return

# -----------------------------------------------
# 添加技能
# -----------------------------------------------
class SPEAddSkill:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.addSkill( value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		if owner is None: return
		owner.removeSkill( value )

# -----------------------------------------------
#
# -----------------------------------------------
class SPENone:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		pass

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		pass

# -----------------------------------------------
# 增加冲锋破绽
# -----------------------------------------------
class AddBuffOdds1:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL1
		owner.skillBuffOdds.addOdds( skillID, value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL1
		owner.skillBuffOdds.decOdds( skillID, value )

# -----------------------------------------------
# 增加猛击破绽
# -----------------------------------------------
class AddBuffOdds2:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL2
		owner.skillBuffOdds.addOdds( skillID, value )
		
	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL2
		owner.skillBuffOdds.decOdds( skillID, value )

# -----------------------------------------------
# 增加横扫破绽
# -----------------------------------------------
class AddBuffOdds3:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL3
		owner.skillBuffOdds.addOdds( skillID, value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL3
		owner.skillBuffOdds.decOdds( skillID, value )


# -----------------------------------------------
# 增加泰山压顶破绽
# -----------------------------------------------
class AddBuffOdds4:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL4
		owner.skillBuffOdds.addOdds( skillID, value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL4
		owner.skillBuffOdds.decOdds( skillID, value )

# -----------------------------------------------
# 增加劲射破绽
# -----------------------------------------------
class AddBuffOdds5:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL5
		owner.skillBuffOdds.addOdds( skillID, value )


	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL5
		owner.skillBuffOdds.decOdds( skillID, value )


# -----------------------------------------------
# 增加乱射破绽
# -----------------------------------------------
class AddBuffOdds6:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL6
		owner.skillBuffOdds.addOdds( skillID, value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL6
		owner.skillBuffOdds.decOdds( skillID, value )

# -----------------------------------------------
# 增加落日破绽
# -----------------------------------------------
class AddBuffOdds7:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL7
		owner.skillBuffOdds.addOdds( skillID, value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL7
		owner.skillBuffOdds.decOdds( skillID, value )

# -----------------------------------------------
# 增加快剑破绽
# -----------------------------------------------
class AddBuffOdds8:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL8
		owner.skillBuffOdds.addOdds( skillID, value )
		
	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL8
		owner.skillBuffOdds.decOdds( skillID, value )

# -----------------------------------------------
# 增加连绵剑破绽
# -----------------------------------------------
class AddBuffOdds9:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL9
		owner.skillBuffOdds.addOdds( skillID, value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL9
		owner.skillBuffOdds.decOdds( skillID, value )

# -----------------------------------------------
# 增加追魂夺命破绽
# -----------------------------------------------
class AddBuffOdds10:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL10
		owner.skillBuffOdds.addOdds( skillID, value )
		
	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL10
		owner.skillBuffOdds.decOdds( skillID, value )
		
# -----------------------------------------------
# 增加火球术破绽
# -----------------------------------------------
class AddBuffOdds11:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL11
		owner.skillBuffOdds.addOdds( skillID, value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL11
		owner.skillBuffOdds.decOdds( skillID, value )

# -----------------------------------------------
# 增加电击术破绽
# -----------------------------------------------
class AddBuffOdds12:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL12
		owner.skillBuffOdds.addOdds( skillID, value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL12
		owner.skillBuffOdds.decOdds( skillID, value )

# -----------------------------------------------
# 增加风卷残云破绽
# -----------------------------------------------
class AddBuffOdds13:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		装备属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL13
		owner.skillBuffOdds.addOdds( skillID, value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		卸下属性
		@param owner: 属性拥有者
		@type  owner: String
		@param value: 该条属性所用到的参数
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL13
		owner.skillBuffOdds.decOdds( skillID, value )
