# -*- coding: gb18030 -*-

# $Id: EquipEffects.py,v 1.18 2008-09-04 07:44:43 kebiao Exp $

import csconst
from bwdebug import *
from Resource.SkillLoader import g_skills
import math
import CombatUnitConfig


# ���Ч��ʵ��
# -----------------------------------------------
# ���ʼ�ֵ
# -----------------------------------------------
class AddValueCorporeity:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		װ������
		"""
		if owner is None: return
		owner.corporeity_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		ж������
		"""
		if owner is None: return
		owner.corporeity_extra -= int( math.ceil( value ) )

class AddPercentCorporeity:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		װ������
		"""
		if owner is None: return
		owner.corporeity_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		ж������
		"""
		if owner is None: return
		owner.corporeity_percent -= int( math.ceil( value ) )
# -----------------------------------------------
# ������ֵ
# -----------------------------------------------
class AddValueIntellect:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.intellect_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.intellect_extra -= int( math.ceil( value ) )

class AddPercentIntellect:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.intellect_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.intellect_percent -= int( math.ceil( value ) )

# -----------------------------------------------
# ������ֵ
# -----------------------------------------------
class AddValueStrength:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		@
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.strength_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.strength_extra -= int( math.ceil( value ) )

class AddPercentStrength:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		@
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.strength_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.strength_percent -= int( math.ceil( value ) )

# -----------------------------------------------
# ���ݼ�ֵ
# -----------------------------------------------
class AddValueDexterity:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.dexterity_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.dexterity_extra -= int( math.ceil( value ) )

class AddPercentDexterity:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.dexterity_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.dexterity_percent -= int( math.ceil( value ) )

# -----------------------------------------------
# ������ֵ
# -----------------------------------------------
class AddValueHP:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_Max_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_Max_extra -= int( math.ceil( value ) )

class AddPercentHP:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_Max_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_Max_percent -= int( math.ceil( value ) )

# -----------------------------------------------
# ������ֵ
# -----------------------------------------------
class AddValueMP:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_Max_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_Max_extra -= int( math.ceil( value ) )

class AddPercentMP:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_Max_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_Max_percent -= int( math.ceil( value ) )

# -----------------------------------------------
# ���������ֵ
# -----------------------------------------------
class AddValueArmor:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.armor_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.armor_extra -= int( math.ceil( value ) )

class AddPercentArmor:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.armor_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.armor_percent -= int( math.ceil( value ) )

# -----------------------------------------------
# ����������ֵ
# -----------------------------------------------
class AddValueMagicArmor:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_armor_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_armor_extra -= int( math.ceil( value ) )

class AddPercentMagicArmor:

	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_armor_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_armor_percent -= int( math.ceil( value ) )

# -----------------------------------------------
# ��ɫ��������
# -----------------------------------------------
class AddValueDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_extra += int( math.ceil( value ) )
		owner.damage_max_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_extra -= int( math.ceil( value ) )
		owner.damage_max_extra -= int( math.ceil( value ) )

class AddPercentDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_percent += int( math.ceil( value ) )
		owner.damage_max_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_percent -= int( math.ceil( value ) )
		owner.damage_max_percent -= int( math.ceil( value ) )

# -----------------------------------------------
# ��ɫ����������
# -----------------------------------------------
class AddValueMagicDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_extra -= int( math.ceil( value ) )

class AddPercentMagicDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_percent += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_percent -= int( math.ceil( value ) )

# -----------------------------------------------
# �����ָ��ٶ�
# -----------------------------------------------
class AddValueHPRegen:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_regen_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_regen_extra -= int( math.ceil( value ) )

# -----------------------------------------------
# �����ָ��ٶ�
# -----------------------------------------------
class AddValueMPRegen:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_regen_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_regen_extra -= int( math.ceil( value ) )

# -----------------------------------------------
# ��С������
# -----------------------------------------------
class AddValueDamageMin:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_extra -= int( math.ceil( value ) )

# -----------------------------------------------
# ��󹥻���
# -----------------------------------------------
class AddValueDamageMax:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_max_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_max_extra -= int( math.ceil( value ) )

# -----------------------------------------------
# �������е���
# -----------------------------------------------
class AddValueHit:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.hitProbability_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.hitProbability_extra -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �������е���
# -----------------------------------------------
class AddValueMagicHit:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.magic_hitProbability_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.magic_hitProbability_extra -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# ���ܵ���
# -----------------------------------------------
class AddValueDodge:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.dodge_probability_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.dodge_probability_extra -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
#  ����
# -----------------------------------------------
class AddValueReduceRoleD:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.reduce_role_damage_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.reduce_role_damage_extra -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
#  �Ƶ�
# -----------------------------------------------
class AddValueAddRoleD:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.add_role_damage_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.add_role_damage_extra -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# ����������
# -----------------------------------------------
class AddValueDoubleHit:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.double_hit_probability_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.double_hit_probability_extra -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# ������������
# -----------------------------------------------
class AddValueMagicDoubleHit:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.magic_double_hit_probability_extra+= int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.magic_double_hit_probability_extra -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �мܵ���
# -----------------------------------------------
class AddValueResistHit:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.resist_hit_probability_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.resist_hit_probability_extra -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �мܼ��˵���
# -----------------------------------------------
class AddValueResistHitDerate:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_hit_derate_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_hit_derate_extra -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �����˺�����
# -----------------------------------------------
class AddValueDamageDerate:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_derate_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_derate_extra -= int( math.ceil( value ) )

# -----------------------------------------------
# �����˺�����
# -----------------------------------------------
class AddValueMagicDamageDerate:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_derate_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_derate_extra -= int( math.ceil( value ) )
# -----------------------------------------------
# �˺�����
# -----------------------------------------------
class AddValueAllDerate:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_derate_extra += int( math.ceil( value ) )
		owner.magic_damage_derate_extra += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_derate_extra -= int( math.ceil( value ) )
		owner.magic_damage_derate_extra -= int( math.ceil( value ) )
# -----------------------------------------------
# ��Ч��������
# -----------------------------------------------
class AddValueSpeciallySpring:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		# 15:08 2008-2-22
		pass

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		# 15:08 2008-2-22
		pass
# -----------------------------------------------
# �������˺�����
# -----------------------------------------------
class AddValueDoubleHitMultiple:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.double_hit_multiple_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.double_hit_multiple_value -= int( value * csconst.FLOAT_ZIP_PERCENT )
# -----------------------------------------------
# ���������˺�����
# -----------------------------------------------
class AddValueMagicDoubleHitMultiple:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.magic_double_hit_multiple_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.magic_double_hit_multiple_value -= int( value * csconst.FLOAT_ZIP_PERCENT )
# -----------------------------------------------
# ���ͶԷ��������е���
# -----------------------------------------------
class AddValueReduceTargetHit:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		# ����receive_be_hit_value Ϊ�����򽵵ͶԷ���������
		# Ϊ���������ӶԷ���������
		owner.receive_be_hit_value -= int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.receive_be_hit_value += int( math.ceil( value ) )

# -----------------------------------------------
#���ͶԷ��������е���
# -----------------------------------------------
class AddValueReduceTargetMagicHit:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		# �����ͶԷ��������е���
		owner.receive_magic_be_hit_value -= int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.receive_magic_be_hit_value += int( math.ceil( value ) )

# ------------------����һЩ�߻������ϵĳ�ͻ �Կ��Եļӳ���8�������µĵȼ���� by����-----------------------------
# -----------------------------------------------
# �ֿ���Ĭ����
# -----------------------------------------------
class AddValueResistChenmo:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		level = owner.level
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.resist_chenmo_probability_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
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
# �ֿ�ѣ��
# -----------------------------------------------
class AddValueResistGiddy:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		level = owner.level
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.resist_giddy_probability_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
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
# �ֿ�����
# -----------------------------------------------
class AddValueResistFix:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		level = owner.level
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.resist_fix_probability_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
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
# �ֿ�˯��
# -----------------------------------------------
class AddValueResistSleep:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		level = owner.level
		value = CombatUnitConfig.valueToPer( value, owner.level )
		owner.resist_sleep_probability_extra += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
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
# �ֿ���Ĭ����
# -----------------------------------------------
class AddValueResistChenmoOdds:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_chenmo_probability_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_chenmo_probability_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �ֿ�ѣ�μ���
# -----------------------------------------------
class AddValueResistGiddyOdds:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_giddy_probability_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_giddy_probability_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �ֿ�������
# -----------------------------------------------
class AddValueResistFixOdds:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_fix_probability_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_fix_probability_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �ֿ�˯�߼���
# -----------------------------------------------
class AddValueResistSleepOdds:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_sleep_probability_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.resist_sleep_probability_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �����ٶ�
# -----------------------------------------------
class AddValueHitSpeed:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.hit_speed_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.hit_speed_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �ƶ��ٶ�
# -----------------------------------------------
class AddValueMoveSpeed:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.move_speed_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.move_speed_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# ��������
# -----------------------------------------------
class AddValueRange:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.range_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.range_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# ��Ч������
# -----------------------------------------------
class AddValueSpeciallySpringPro:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		pass

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		pass

# -----------------------------------------------
# ��������
# -----------------------------------------------
class AddValueDoubleHitPro:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.double_hit_probability_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.double_hit_probability_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# ����������
# -----------------------------------------------
class AddValueMagicDoubleHitPro:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_double_hit_probability_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_double_hit_probability_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# ���������ʼ���
# -----------------------------------------------
class AddValueBeDoubleHitProReduce:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.be_double_hit_probability_reduce += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.be_double_hit_probability_reduce -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �����������ʼ���
# -----------------------------------------------
class AddValueMagicBeDoubleHitProReduce:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.be_magic_double_hit_probability_reduce += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.be_magic_double_hit_probability_reduce -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# ����������
# -----------------------------------------------
class AddValueHitPro:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.hitProbability_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.hitProbability_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# ����������
# -----------------------------------------------
class AddValueMagicHitPro:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_hitProbability_value += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_hitProbability_value -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# ����������
# -----------------------------------------------
class AddValueWeaponDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_value += int( math.ceil( value ) )
		owner.damage_max_value += int( math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_value -= int( math.ceil( value ) )
		owner.damage_max_value -= int( math.ceil( value ) )

# -----------------------------------------------
# ���ʼӳ�
# -----------------------------------------------
class AddPercentCorporeity:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.corporeity_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.corporeity_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �����ӳ�
# -----------------------------------------------
class AddPercentIntellect:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.intellect_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.intellect_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �����ӳ�
# -----------------------------------------------
class AddPercentStrength:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.strength_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.strength_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# ���ݼӳ�
# -----------------------------------------------
class AddPercentDexterity:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.dexterity_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.dexterity_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �����ӳ�
# -----------------------------------------------
class AddPercentHP:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_Max_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_Max_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �����ӳ�
# -----------------------------------------------
class AddPercentMP:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_Max_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_Max_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# ��������ӳ�
# -----------------------------------------------
class AddPercentArmor:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.armor_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.armor_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# ���������ӳ�
# -----------------------------------------------
class AddPercentMagicArmor:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_armor_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_armor_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �����������ӳ�
# -----------------------------------------------
class AddPercentWeaponDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_percent += int( value * csconst.FLOAT_ZIP_PERCENT )
		owner.damage_max_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )
		owner.damage_max_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# ��ɫ���������ӳ�
# -----------------------------------------------
class AddPercentDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_percent += int( value * csconst.FLOAT_ZIP_PERCENT )
		owner.damage_max_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_min_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )
		owner.damage_max_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# ��ɫ�����������ӳ�
# -----------------------------------------------
class AddPercentMagicDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �����ָ��ٶȼӳ�
# -----------------------------------------------
class AddPercentHPRegen:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_regen_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.HP_regen_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �����ָ��ٶȼӳ�
# -----------------------------------------------
class AddPercentMPRegen:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_regen_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.MP_regen_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �����˺�����ӳ�
# -----------------------------------------------
class AddPercentDamageDerate:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_derate_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_derate_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �����˺�����
# -----------------------------------------------
class AddPercentMagicDamageDerate:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_derate_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.magic_damage_derate_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �˺�����ӳ�
# -----------------------------------------------
class AddPercentAllDerate:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_derate_percent += int( value * csconst.FLOAT_ZIP_PERCENT )
		owner.magic_damage_derate_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.damage_derate_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )
		owner.magic_damage_derate_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# ����ӳ�
# -----------------------------------------------
class AddPercentMultExp:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.multExp += value

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.multExp -= value

# -----------------------------------------------
# Ǳ�ܵ�ӳ�
# -----------------------------------------------
class AddPercentMultPotential:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.potential_percent += value

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.potential_percent -= value

# -----------------------------------------------
# �ƶ��ٶȼӳ�
# -----------------------------------------------
class AddPercentMoveSpeed:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.move_speed_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.move_speed_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# �����ٶ�
# -----------------------------------------------
class AddPercentHitSpeed:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.hit_speed_percent += int( value * csconst.FLOAT_ZIP_PERCENT )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.hit_speed_percent -= int( value * csconst.FLOAT_ZIP_PERCENT )

# -----------------------------------------------
# Ԫ�����
# -----------------------------------------------
#-------------��------------------------
class AddHuoDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage -= int(  math.ceil( value ) )

class AddHuoDamageBase:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage_base += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage_base -= int(  math.ceil( value ) )

class AddHuoDamagePercent:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage_percent += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage_percent -= int(  math.ceil( value ) )

class AddHuoDamageExtra:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage_extra += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage_extra -= int(  math.ceil( value ) )

class AddHuoDamageValue:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage_value += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_damage_value -= int(  math.ceil( value ) )

class AddHuoDR:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio += int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio -= int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()

class AddHuoDRBase:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio_base += int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio_base -= int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()

class AddHuoDRPercent:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio_percent += int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio_percent -= int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()

class AddHuoDRExtra:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio_extra += int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio_extra -= int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()

class AddHuoDRValue:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio_value += int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_huo_derate_ratio_value -= int(  math.ceil( value ) )
		owner.calcElemHuoDerateRatio()
#-------------��------------------------
class AddXuanDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage -= int(  math.ceil( value ) )

class AddXuanDamageBase:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage_base += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage_base -= int(  math.ceil( value ) )

class AddXuanDamagePercent:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage_percent += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage_percent -= int(  math.ceil( value ) )

class AddXuanDamageExtra:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage_extra += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage_extra -= int(  math.ceil( value ) )

class AddXuanDamageValue:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage_value += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_damage_value -= int(  math.ceil( value ) )

class AddXuanDR:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio += int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio -= int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()

class AddXuanDRBase:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio_base += int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio_base -= int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()

class AddXuanDRPercent:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio_percent += int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio_percent -= int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()

class AddXuanDRExtra:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio_extra += int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio_extra -= int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()

class AddXuanDRValue:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio_value += int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_xuan_derate_ratio_value -= int(  math.ceil( value ) )
		owner.calcElemXuanDerateRatio()
#-------------��------------------------
class AddLeiDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage -= int(  math.ceil( value ) )

class AddLeiDamageBase:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage_base += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage_base -= int(  math.ceil( value ) )

class AddLeiDamagePercent:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage_percent += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage_percent -= int(  math.ceil( value ) )

class AddLeiDamageExtra:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage_extra += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage_extra -= int(  math.ceil( value ) )

class AddLeiDamageValue:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage_value += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_damage_value -= int(  math.ceil( value ) )

class AddLeiDR:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio += int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio -= int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()

class AddLeiDRBase:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio_base += int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio_base -= int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()

class AddLeiDRPercent:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio_percent += int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio_percent -= int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()

class AddLeiDRExtra:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio_extra += int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio_extra -= int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()

class AddLeiDRValue:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio_value += int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_lei_derate_ratio_value -= int(  math.ceil( value ) )
		owner.calcElemLeiDerateRatio()
#-------------��------------------------
class AddBingDamage:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage -= int(  math.ceil( value ) )

class AddBingDamageBase:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage_base += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage_base -= int(  math.ceil( value ) )

class AddBingDamagePercent:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage_percent += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage_percent -= int(  math.ceil( value ) )

class AddBingDamageExtra:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage_extra += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage_extra -= int(  math.ceil( value ) )

class AddBingDamageValue:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage_value += int(  math.ceil( value ) )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_damage_value -= int(  math.ceil( value ) )

class AddBingDR:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio += int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio -= int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()

class AddBingDRBase:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio_base += int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio_base -= int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()

class AddBingDRPercent:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio_percent += int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio_percent -= int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()

class AddBingDRExtra:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio_extra += int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio_extra -= int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()

class AddBingDRValue:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio_value += int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.elem_bing_derate_ratio_value -= int(  math.ceil( value ) )
		owner.calcElemBingDerateRatio()
# -----------------------------------------------
# ���buff
# -----------------------------------------------
class SPEAddBuff:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		#buff ���������ڣ��Ա������ܵķ�ʽ���
		owner.addSkill( value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.removeSKill( value )

# -----------------------------------------------
# �������ʱ����
# -----------------------------------------------
class SPEHitSpring:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		# �Բ��� value ����һ������ʵ��
		# ���м���ID value ����һ���������ʱ���������˺��ļ���
		# ������ܸ��ӵ��������֮�����������е�ʱ����Զ�����
		# ���ж�� ��������ʱ���������˺����ּ��ܴ���ʱ����ҵ�
		# �������б���ֻ�ᱣ��һ��IDΪvalue�ļ���ʵ������ֵ����
		# �ۼӵķ�ʽ��ӽ�ȥ�����������ڶ�Ӧ�ļ���value������
		try:
			skill = g_skills[ value ]
		except KeyError:
			ERROR_MSG( "���ܲ�����: %i." % value )
			return
		skill = skill.newSelf()
		equip.setTemp( "skillUID", skill.getUID() )
		skill.attach( owner )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		# ͨ��װ������ļ���UID����ҵĻ����б�����Ѱ�Ҷ�Ӧ�ļ��ܲ�ж�ظü���
		# ��ʱ���� equipEffect_hit_damage ���ڱ��������Ҫж�ص�����ֵ(��������)
		# �ڶ�Ӧ�ļ���ʵ������������ش���
		#owner.setTemp( "equipEffect_hit_damage", value )
		for skill in owner.springAttackerHitList:
			if skill.getUID() == equip.queryTemp( "skillUID" ):
			 	skill.detach( owner )
			 	return


# -----------------------------------------------
# �������д���
# -----------------------------------------------
class SPEMagicHitSpring:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		try:
			skill = g_skills[ value ]
		except KeyError:
			ERROR_MSG( "���ܲ�����: %i." % value )
			return
		skill = skill.newSelf()
		equip.setTemp( "skillUID", skill.getUID() )
		skill.attach( owner )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		for skill in owner.springAttackerHitList:
			if skill.getUID() == equip.queryTemp( "skillUID" ):
			 	skill.detach( owner )
			 	return

# -----------------------------------------------
# ������ʱ����
# -----------------------------------------------
class SPEBeHitSpring:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		try:
			skill = g_skills[value]
		except KeyError:
			ERROR_MSG( "���ܲ�����: %i." % value )
			return
		skill = skill.newSelf()
		equip.setTemp( "skillUID", skill.getUID() )
		skill.attach( owner )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		for skill in owner.springVictimHitList:
			if skill.getUID() == equip.queryTemp( "skillUID" ):
			 	skill.detach( owner )
			 	return

# -----------------------------------------------
# ������ʱ����
# -----------------------------------------------
class SPEBeDoubleHitSpring:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		try:
			skill = g_skills[ value ]
		except KeyError:
			ERROR_MSG( "�����ڼ���: %i." % value )
			return
		skill = skill.newSelf()
		equip.setTemp( "skillUID", skill.getUID() )
		skill.attach( owner )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		for skill in owner.springVictimDoubleHitList:
			if skill.getUID() == equip.queryTemp( "skillUID" ):
			 	skill.detach( owner )
			 	return

# -----------------------------------------------
# ������ʱ����
# -----------------------------------------------
class SPEDoubleHitSpring:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		try:
			skill = g_skills[ value ]
		except KeyError:
			ERROR_MSG( "�����ڼ���: %i." % value )
			return
		skill = skill.newSelf()
		equip.setTemp( "skillUID", skill.getUID() )
		skill.attach( owner )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		for skill in owner.springAttackerDoubleHitList:
			if skill.getUID() == equip.queryTemp( "skillUID" ):
			 	skill.detach( owner )
			 	return

# -----------------------------------------------
# ��������ʱ����
# -----------------------------------------------
class SPEMagicDoubleHitSpring:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		try:
			skill = g_skills[ value ]
		except KeyError:
			ERROR_MSG( "�����ڼ���: %i." % value )
			return
		skill = skill.newSelf()
		equip.setTemp( "skillUID", skill.getUID() )
		skill.attach( owner )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		for skill in owner.springAttackerDoubleHitList:
			if skill.getUID() == equip.queryTemp( "skillUID" ):
			 	skill.detach( owner )
			 	return

# -----------------------------------------------
# ��Ӽ���
# -----------------------------------------------
class SPEAddSkill:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		if owner is None: return
		owner.addSkill( value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
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
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		pass

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		pass

# -----------------------------------------------
# ���ӳ������
# -----------------------------------------------
class AddBuffOdds1:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL1
		owner.skillBuffOdds.addOdds( skillID, value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL1
		owner.skillBuffOdds.decOdds( skillID, value )

# -----------------------------------------------
# �����ͻ�����
# -----------------------------------------------
class AddBuffOdds2:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL2
		owner.skillBuffOdds.addOdds( skillID, value )
		
	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL2
		owner.skillBuffOdds.decOdds( skillID, value )

# -----------------------------------------------
# ���Ӻ�ɨ����
# -----------------------------------------------
class AddBuffOdds3:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL3
		owner.skillBuffOdds.addOdds( skillID, value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL3
		owner.skillBuffOdds.decOdds( skillID, value )


# -----------------------------------------------
# ����̩ɽѹ������
# -----------------------------------------------
class AddBuffOdds4:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL4
		owner.skillBuffOdds.addOdds( skillID, value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL4
		owner.skillBuffOdds.decOdds( skillID, value )

# -----------------------------------------------
# ���Ӿ�������
# -----------------------------------------------
class AddBuffOdds5:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL5
		owner.skillBuffOdds.addOdds( skillID, value )


	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL5
		owner.skillBuffOdds.decOdds( skillID, value )


# -----------------------------------------------
# ������������
# -----------------------------------------------
class AddBuffOdds6:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL6
		owner.skillBuffOdds.addOdds( skillID, value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL6
		owner.skillBuffOdds.decOdds( skillID, value )

# -----------------------------------------------
# ������������
# -----------------------------------------------
class AddBuffOdds7:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL7
		owner.skillBuffOdds.addOdds( skillID, value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL7
		owner.skillBuffOdds.decOdds( skillID, value )

# -----------------------------------------------
# ���ӿ콣����
# -----------------------------------------------
class AddBuffOdds8:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL8
		owner.skillBuffOdds.addOdds( skillID, value )
		
	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL8
		owner.skillBuffOdds.decOdds( skillID, value )

# -----------------------------------------------
# �������ལ����
# -----------------------------------------------
class AddBuffOdds9:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL9
		owner.skillBuffOdds.addOdds( skillID, value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL9
		owner.skillBuffOdds.decOdds( skillID, value )

# -----------------------------------------------
# ����׷���������
# -----------------------------------------------
class AddBuffOdds10:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL10
		owner.skillBuffOdds.addOdds( skillID, value )
		
	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL10
		owner.skillBuffOdds.decOdds( skillID, value )
		
# -----------------------------------------------
# ���ӻ���������
# -----------------------------------------------
class AddBuffOdds11:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL11
		owner.skillBuffOdds.addOdds( skillID, value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL11
		owner.skillBuffOdds.decOdds( skillID, value )

# -----------------------------------------------
# ���ӵ��������
# -----------------------------------------------
class AddBuffOdds12:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL12
		owner.skillBuffOdds.addOdds( skillID, value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL12
		owner.skillBuffOdds.decOdds( skillID, value )

# -----------------------------------------------
# ���ӷ���������
# -----------------------------------------------
class AddBuffOdds13:
	@staticmethod
	def attach( owner, value, equip ):
		"""
		װ������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL13
		owner.skillBuffOdds.addOdds( skillID, value )

	@staticmethod
	def detach( owner, value, equip ):
		"""
		ж������
		@param owner: ����ӵ����
		@type  owner: String
		@param value: �����������õ��Ĳ���
		@type  value: Int
		"""
		skillID = csconst.EQUIP_EFFECT_ADD_ODDS_SKILL13
		owner.skillBuffOdds.decOdds( skillID, value )
