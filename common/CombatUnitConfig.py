# -*- coding: gb18030 -*-

import csdefine
import ItemTypeEnum

# սʿ
class FighterFunc:
	def __init__( self ):
		"""
		"""
		pass

	def calcRoleHPMaxBase( self, selfEntity ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
		"""
		return selfEntity.corporeity * 12

	def calcRoleMPMaxBase( self, selfEntity ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
		"""
		return selfEntity.intellect * 5	# ��ֵ�޸�2.1.03��ԭֵ5

	def calcRolePhysicsDPS( self, selfEntity ):
		"""
		virtual method.
		����ְҵ��������DPS
		"""
		return selfEntity.strength * 0.62	# ��ֵ�޸�2.1.03��ԭֵ0.5

	def calcPhysicsDPS( self, selfEntity ):
		"""
		virtual method.
		����ְҵ�������������DPS
		"""
		return selfEntity.strength * 0.1

	def calcBaseDodgeProbability( self, selfEntity ):
		"""
		virtual method.
		����ְҵ����������
		սʿ�������ܣ��ܹ�ʽ�еĻ���ֵ��=3%+��ɫ��ǰ����/15000-1*��lv-1��/15000
		"""
		return 0.03 + selfEntity.dexterity / 15000 - 1.0 * ( selfEntity.level - 1 ) / 15000

	def calcBaseDoubleHitProbability( self, selfEntity ):
		"""
		virtual method.
		����ְҵ������������
		սʿ�����������ʣ��ܹ�ʽ�еĻ���ֵ��=5%+��ɫ��ǰ����/10000-1*��lv-1��/10000
		"""
		return 0.05 + selfEntity.dexterity / 10000 - 1.0 * ( selfEntity.level - 1 ) / 10000

	def calcMagicBaseDoubleHitProbability( self, selfEntity ):
		"""
		virtual method.
		����ְҵ��������������
		սʿ�������������ʣ��ܹ�ʽ�еĻ���ֵ��=5%+��ɫ��ǰ����/10000-0.5*��lv-1��/10000
		"""
		return 0.05 + selfEntity.intellect / 10000 - 1.0 * ( selfEntity.level - 1 ) / 10000

	def calcBaseResistHitProbability( self, selfEntity ):
		"""
		virtual method.
		����ְҵ�����мܼ���
		սʿ�����мܣ��ܹ�ʽ�еĻ���ֵ��=3%+��ɫ��ǰ����/12000-2*��lv-1��/12000
		"""
		return 0.03 + selfEntity.strength / 12000 - 2.0 * ( selfEntity.level - 1 ) / 12000

	def calcRoleMagicDamage( self, selfEntity ):
		"""
		virtual method.
		����ְҵ��������������
		"""
		return selfEntity.intellect * 1.0	# ��ֵ�޸�2.1.03��ԭֵ0.5

	def initElemProperty( self, selfEntity ):
		"""
		��ʼ������Ԫ��
		"""
		selfEntity.elem_huo_damage_percent = 0
		selfEntity.elem_xuan_damage_percent = 0
		selfEntity.elem_lei_damage_percent = 0
		selfEntity.elem_bing_damage_percent = 0

# ����
class SwordmanFunc(  FighterFunc ):
	def calcRoleHPMaxBase( self, selfEntity ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
		"""
		return selfEntity.corporeity * 10

	def calcRoleMPMaxBase( self, selfEntity ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
		"""
		return selfEntity.intellect * 5	# ��ֵ�޸�2.1.03��ԭֵ6

	def calcRolePhysicsDPS( self, selfEntity ):
		"""
		virtual method.
		����ְҵ��������DPS
		"""
		return selfEntity.strength * 0.77 + selfEntity.dexterity * 0.77
		# ��ֵ�޸�2.1.03��ԭֵ0.5��0.5

	def calcPhysicsDPS( self, selfEntity ):
		"""
		virtual method.
		����ְҵ�������������DPS
		"""
		return selfEntity.strength * 0.07 + selfEntity.dexterity * 0.07

	def calcBaseDodgeProbability( self, selfEntity ):
		"""
		virtual method.
		����ְҵ����������
		���ͻ������ܣ��ܹ�ʽ�еĻ���ֵ��=3%+��ɫ��ǰ����/15000-1.5*��lv-1��/15000
		"""
		return 0.03 + selfEntity.dexterity / 15000 - 1.5 * ( selfEntity.level - 1 ) / 15000

	def calcBaseDoubleHitProbability( self, selfEntity ):
		"""
		virtual method.
		����ְҵ������������
		���ͻ����������ʣ��ܹ�ʽ�еĻ���ֵ��=20%+��ɫ��ǰ����/10000-1.5*��lv-1��/10000
		"""
		return 0.2 + selfEntity.dexterity / 10000 - 1.5 * ( selfEntity.level - 1 ) / 10000

	def calcMagicBaseDoubleHitProbability( self, selfEntity ):
		"""
		virtual method.
		����ְҵ��������������
		���ͻ������������ʣ��ܹ�ʽ�еĻ���ֵ��=20%+��ɫ��ǰ����/10000-1.5*��lv-1��/10000
		"""
		return 0.2 + selfEntity.intellect / 10000 - 1.5 * ( selfEntity.level - 1 ) / 10000

	def calcBaseResistHitProbability( self, selfEntity ):
		"""
		virtual method.
		����ְҵ�����мܼ���
		���ͻ����мܣ��ܹ�ʽ�еĻ���ֵ��=2.5%+��ɫ��ǰ����/12000-1.5*��lv-1��/12000
		"""
		return 0.025 + selfEntity.strength / 12000 - 1.5 * ( selfEntity.level - 1 ) / 12000

	def calcRoleMagicDamage( self, selfEntity ):
		"""
		virtual method.
		����ְҵ��������������
		"""
		return selfEntity.intellect * 1.5		# ��ֵ�޸�2.1.03��ԭֵ0.5

	def initElemProperty( self, selfEntity ):
		"""
		��ʼ������Ԫ��
		"""
		selfEntity.elem_huo_damage_percent = 0
		selfEntity.elem_xuan_damage_percent = 0
		selfEntity.elem_lei_damage_percent = 0
		selfEntity.elem_bing_damage_percent = 0

# ����
class ArcherFunc(  FighterFunc ):
	def calcRoleHPMaxBase( self, selfEntity ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
		"""
		return selfEntity.corporeity * 8.5		# ��ֵ�޸�2.1.03��ԭֵ10

	def calcRoleMPMaxBase( self, selfEntity ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
		"""
		return selfEntity.intellect * 5	# ��ֵ�޸�2.1.03��ԭֵ6

	def calcRolePhysicsDPS( self, selfEntity ):
		"""
		virtual method.
		����ְҵ��������DPS
		"""
		return selfEntity.strength * 0.57 + selfEntity.dexterity * 0.57
		# ��ֵ�޸�2.1.03��ԭֵ0.3;0.6
	def calcPhysicsDPS( self, selfEntity ):
		"""
		virtual method.
		����ְҵ(����)��������DPS
		"""
		return selfEntity.strength * 0.04 + selfEntity.dexterity * 0.06

	def calcBaseDodgeProbability( self, selfEntity ):
		"""
		virtual method.
		����ְҵ����������
		���ֻ������ܣ��ܹ�ʽ�еĻ���ֵ��=3%+��ɫ��ǰ����/20000-2.5*��lv-1��/20000
		"""
		return 0.03 + selfEntity.dexterity / 20000 - 2.5 * ( selfEntity.level - 1 ) / 20000

	def calcBaseDoubleHitProbability( self, selfEntity ):
		"""
		virtual method.
		����ְҵ������������
		���ֻ����������ʣ��ܹ�ʽ�еĻ���ֵ��=5%+��ɫ��ǰ����/15000-2.5*��lv-1��/15000
		"""
		return 0.05 + selfEntity.dexterity / 15000 - 2.5 * ( selfEntity.level - 1 ) / 15000

	def calcMagicBaseDoubleHitProbability( self, selfEntity ):
		"""
		virtual method.
		����ְҵ��������������
		���ֻ������������ʣ��ܹ�ʽ�еĻ���ֵ��=5%+��ɫ��ǰ����/10000-0.5*��lv-1��/10000
		"""
		return 0.05 + selfEntity.intellect / 10000 - 1.0 * ( selfEntity.level - 1 ) / 10000

	def calcBaseResistHitProbability( self, selfEntity ):
		"""
		virtual method.
		����ְҵ�����мܼ���
		���ֻ����мܣ��ܹ�ʽ�еĻ���ֵ��=2%+��ɫ��ǰ����/12000-1.5*��lv-1��/12000
		"""
		return 0.02 + selfEntity.strength / 12000 - 1.5 * ( selfEntity.level - 1 ) / 12000

	def calcRoleMagicDamage( self, selfEntity ):
		"""
		virtual method.
		����ְҵ��������������
		"""
		return selfEntity.intellect * 1.5		# ��ֵ�޸�2.1.03��ԭֵ0.5

	def initElemProperty( self, selfEntity ):
		"""
		��ʼ������Ԫ��
		"""
		selfEntity.elem_huo_damage_percent = 0
		selfEntity.elem_xuan_damage_percent = 0
		selfEntity.elem_lei_damage_percent = 0
		selfEntity.elem_bing_damage_percent = 0

# ��ʦ
class MageFunc(  FighterFunc ):
	def calcRoleHPMaxBase( self, selfEntity ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
		"""
		return selfEntity.corporeity * 8

	def calcRoleMPMaxBase( self, selfEntity ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
		"""
		return selfEntity.intellect * 5

	def calcRolePhysicsDPS( self, selfEntity ):
		"""
		virtual method.
		����ְҵ��������DPS
		"""
		return selfEntity.strength * 1.0	# ��ֵ�޸�2.1.03��ԭֵ0.5

	def calcPhysicsDPS( self, selfEntity ):
		"""
		virtual method.
		����ְҵ�������������DPS
		"""
		return selfEntity.strength * 0.07

	def calcBaseDodgeProbability( self, selfEntity ):
		"""
		virtual method.
		����ְҵ����������
		��ʦ�������ܣ��ܹ�ʽ�еĻ���ֵ��=3%+��ɫ��ǰ����/15000
		"""
		return 0.03 + selfEntity.dexterity / 15000

	def calcBaseDoubleHitProbability( self, selfEntity ):
		"""
		virtual method.
		����ְҵ������������
		��ʦ�����������ʣ��ܹ�ʽ�еĻ���ֵ��=5%+��ɫ��ǰ����/10000-1*��lv-1��/10000
		"""
		return 0.05 + selfEntity.dexterity / 10000 - 1.0 * ( selfEntity.level - 1 ) / 10000

	def calcMagicBaseDoubleHitProbability( self, selfEntity ):
		"""
		virtual method.
		����ְҵ��������������
		��ʦ�������������ʣ��ܹ�ʽ�еĻ���ֵ��=5%+��ɫ��ǰ����/15000-3.5*��lv-1��/15000
		"""
		return 0.05 + selfEntity.intellect / 15000 - 3.5 * ( selfEntity.level - 1 ) / 15000

	def calcBaseResistHitProbability( self, selfEntity ):
		"""
		virtual method.
		����ְҵ�����мܼ���
		��ʦ�����мܣ��ܹ�ʽ�еĻ���ֵ��=1%+��ɫ��ǰ����/8000
		"""
		return 0.01 + selfEntity.strength / 8000

	def calcRoleMagicDamage( self, selfEntity ):
		"""
		virtual method.
		����ְҵ��������������
		"""
		return selfEntity.intellect * 1.5	# ��ֵ�޸�2.1.03��ԭֵ2.0

	def initElemProperty( self, selfEntity ):
		"""
		��ʼ������Ԫ��
		"""
		selfEntity.elem_huo_damage_percent = 0
		selfEntity.elem_xuan_damage_percent = 0
		selfEntity.elem_lei_damage_percent = 0
		selfEntity.elem_bing_damage_percent = 0

# ս����ʽ����
class CombatRadix:
	"""
	��ɫս����ز���
	"""
	def __init__( self, **argw ):
		"""
		"""
		self.strength = 0 #����(int)
		self.dexterity = 0 #����(int)
		self.intellect = 0 #����(int)
		self.corporeity = 0 #����(int)
		self.physics_dps = 0 #��������(int)
		self.magic_dps = 0 #����������(int)
		self.strength_value = 0 #����ÿ����ֵ(float)
		self.dexterity_value = 0 #����ÿ����ֵ(float)
		self.intellect_value = 0.0 #����ÿ����ֵ(float)
		self.corporeity_value = 0.0 #����ÿ����ֵ(float)
		self.physics_dps_value = 0.0 #��������ÿ����ֵ(float)
		self.magic_dps_value = 0.0 #����������ÿ����ֵ(float)
		self.HP_regen_base = 0.0 #HP�ָ�ֵ(float)
		self.MP_regen_base = 0.0 #MP�ָ�ֵ(float)
		self.MP_Max_value = 0.0 #MP����ÿ����ֵ(float)
		# init
		self.__dict__.update( argw )

# ��ְҵս����ʽ����
ROLE_COMBAT_RADIX = {
		# սʿ
		csdefine.CLASS_FIGHTER	:	CombatRadix(
											strength = 13, #����(int)
											dexterity = 7, #����(int)
											intellect = 4, #����(int)
											corporeity = 16, #����(int)
											physics_dps = 6, #��������(int)
											magic_dps = 0, #����������(int)
											strength_value = 2.0, #����ÿ����ֵ(float)
											dexterity_value = 1.0, #����ÿ����ֵ(float)
											intellect_value = 1.0, #����ÿ����ֵ(float)
											corporeity_value = 2.5, #����ÿ����ֵ(float)
											physics_dps_value = 4.0, #��������ÿ����ֵ(float)
											magic_dps_value = 0.0, #����������ÿ����ֵ(float)
											HP_regen_base = 10.0, #HP�ָ�ֵ(float)
											MP_regen_base = 10.0, #MP�ָ�ֵ(float)
											MP_Max_value = 15.0, #MP����ÿ����ֵ(float)
											),
		# ����
		csdefine.CLASS_SWORDMAN	:	CombatRadix(
											strength = 10, #����(int)
											dexterity = 10, #����(int)
											intellect = 9, #����(int)
											corporeity = 11, #����(int)
											physics_dps = 0, #��������(int)
											magic_dps = 6, #����������(int)
											strength_value = 1.5, #����ÿ����ֵ(int)
											dexterity_value = 1.5, #����ÿ����ֵ(int)
											intellect_value = 1.5, #����ÿ����ֵ(float)
											corporeity_value = 2.0, #����ÿ����ֵ(float)
											physics_dps_value = 4.0, #��������ÿ����ֵ(float)
											magic_dps_value = 4.0, #����������ÿ����ֵ(float)
											HP_regen_base = 10.0, #HP�ָ�ֵ(float)
											MP_regen_base = 10.0, #MP�ָ�ֵ(float)
											MP_Max_value = 15.0, #MP����ÿ����ֵ(float)
											),
		# ����
		csdefine.CLASS_ARCHER		:	CombatRadix(
											strength = 10, #����(int)
											dexterity = 13, #����(int)
											intellect = 6, #����(int)
											corporeity = 11, #����(int)
											physics_dps = 6, #��������(int)
											magic_dps = 4, #����������(int)
											strength_value = 1.5, #����ÿ����ֵ(int)
											dexterity_value = 2.5, #����ÿ����ֵ(int)
											intellect_value = 1.0, #����ÿ����ֵ(float)
											corporeity_value = 1.5, #����ÿ����ֵ(float)
											physics_dps_value = 3.0, #��������ÿ����ֵ(float)
											magic_dps_value = 5.5, #����������ÿ����ֵ(float)
											HP_regen_base = 10.0, #HP�ָ�ֵ(float)
											MP_regen_base = 10.0, #MP�ָ�ֵ(float)
											MP_Max_value = 15.0, #MP����ÿ����ֵ(float)
											),
		# ��ʦ
		csdefine.CLASS_MAGE		:	CombatRadix(
											strength = 6, #����(int)
											dexterity = 6, #����(int)
											intellect = 18, #����(int)
											corporeity = 10, #����(int)
											physics_dps = 0, #��������(int)
											magic_dps = 0, #����������(int)
											strength_value = 1.0, #����ÿ����ֵ(int)
											dexterity_value = 1.0, #����ÿ����ֵ(int)
											intellect_value = 3.0, #����ÿ����ֵ(float)
											corporeity_value = 1.5, #����ÿ����ֵ(float)
											physics_dps_value = 0.0, #��������ÿ����ֵ(float)
											magic_dps_value = 3.0, #����������ÿ����ֵ(float)
											HP_regen_base = 10.0, #HP�ָ�ֵ(float)
											MP_regen_base = 10.0, #MP�ָ�ֵ(float)
											MP_Max_value = 15.0, #MP����ÿ����ֵ(float)
											),
		# ��ʦ
		csdefine.CLASS_WARLOCK	:	CombatRadix(
											strength = 0, #����(int)
											dexterity = 0, #����(int)
											intellect = 0, #����(int)
											corporeity = 0, #����(int)
											physics_dps = 0, #��������(int)
											magic_dps = 0, #����������(int)
											strength_value = 0.0, #����ÿ����ֵ(float)
											dexterity_value = 0.0, #����ÿ����ֵ(float)
											intellect_value = 0.0, #����ÿ����ֵ(float)
											corporeity_value = 0.0, #����ÿ����ֵ(float)
											physics_dps_value = 0.0, #��������ÿ����ֵ(float)
											magic_dps_value = 0.0, #����������ÿ����ֵ(float)
											HP_regen_base = 10.0, #HP�ָ�ֵ(float)
											MP_regen_base = 10.0, #MP�ָ�ֵ(float)
											MP_Max_value = 0.0, #MP����ÿ����ֵ(float)
											),
		# ��ʦ
		csdefine.CLASS_PRIEST		:	CombatRadix(
											strength = 0, #����(int)
											dexterity = 0, #����(int)
											intellect = 0, #����(int)
											corporeity = 0, #����(int)
											physics_dps = 0, #��������(int)
											magic_dps = 0, #����������(int)
											strength_value = 0.0, #����ÿ����ֵ(float)
											dexterity_value = 0.0, #����ÿ����ֵ(float)
											intellect_value = 0.0, #����ÿ����ֵ(float)
											corporeity_value = 0.0, #����ÿ����ֵ(float)
											physics_dps_value = 0.0, #��������ÿ����ֵ(float)
											magic_dps_value = 0.0, #����������ÿ����ֵ(float)
											HP_regen_base = 10.0, #HP�ָ�ֵ(float)
											MP_regen_base = 10.0, #MP�ָ�ֵ(float)
											MP_Max_value = 0.0, #MP����ÿ����ֵ(float)
											),
	}	# end of ROLE_COMBAT_RADIX

# ��ְҵս����ʽ����
ENTITY_COMBAT_BASE_EXPRESSION = {
		# սʿ
		csdefine.CLASS_FIGHTER	:	FighterFunc(),
		# ����
		csdefine.CLASS_SWORDMAN	:	SwordmanFunc(),
		# ����
		csdefine.CLASS_ARCHER		:	ArcherFunc(),
		# ��ʦ
		csdefine.CLASS_MAGE		:	MageFunc(),
		# ��ʦ
		csdefine.CLASS_WARLOCK	:	FighterFunc(),
		# ��ʦ
		csdefine.CLASS_PRIEST		:	FighterFunc(),
		# ǿ��սʿ
		csdefine.CLASS_PALADIN	:	FighterFunc(),
	}	# end of ROLE_COMBAT_RADIX


# ����ת���ʼ��㹫ʽ
def valueToPer( value, level ):
	"""
	װ�������е���ת�����ʵĹ�ʽ
	"""
	return ( 0.01012 * value)/( 1.5 **( 0.091 * level - 1 ) )


# ����������/�����������м��㹫ʽ
def calcHitProbability( caster, target ):
	"""
	������������
	
	���������� = max��0,min��1, ��������������ֵ - �ط�������ֵ����+�ȼ�������
	�ȼ����� = 1%*(int((�����ȼ�-�ط��ȼ�)/5)+(int(�����ȼ�<�ط��ȼ�)*1))
	"""
	levelAdjust = ( int( (caster.level - target.level)/5 ) + ( int(caster.level < target.level)*1 ) ) * 0.01
	return max( 0,min( 1,caster.hitProbability - target.dodge_probability ) ) + levelAdjust

def calcMagicHitProbability( caster, target ):
	"""
	���㷨������
	
	���������� = max��0,min��1, ��������������ֵ - �ط�������ֵ����+�ȼ�������
	�ȼ����� = 1%*(int((�����ȼ�-�ط��ȼ�)/5)+(int(�����ȼ�<�ط��ȼ�)*1))
	"""
	levelAdjust = ( int( (caster.level - target.level)/5 ) + ( int(caster.level < target.level)*1 ) ) * 0.01
	return max( 0,min( 1,caster.magic_hitProbability - target.dodge_probability ) ) + levelAdjust


# �����;�ֵ���㹫ʽ
def calcArmorHardiness( baseValue, level, baseRate ):
	"""
	�;ö�ʵ��ֵ=��λ����ֵ*1.5^��0.1*���ߵȼ�-1��*��������Ʒ�ʱ���
	"""
	return baseValue * 1.5 ** ( 0.1 * level - 1 ) * baseRate

def calcHeadHardiness( level, baseRate ):
	"""
	ͷ���;ö�ʵ��ֵ=56000*1.5^��0.1*���ߵȼ�-1��*��������Ʒ�ʱ���
	"""
	return calcArmorHardiness( 56000, level, baseRate )

def calcBodyHardiness( level, baseRate ):
	"""
	�ؼ��;ö�ʵ��ֵ=65000*1.5^��0.1*���ߵȼ�-1��*��������Ʒ�ʱ���
	"""
	return calcArmorHardiness( 65000, level, baseRate )

def calcHaunchHardiness( level, baseRate ):
	"""
	�����;ö�ʵ��ֵ=40000*1.5^��0.1*���ߵȼ�-1��*��������Ʒ�ʱ���
	"""
	return calcArmorHardiness( 40000, level, baseRate )

def calcCuffHardiness( level, baseRate ):
	"""
	�����;ö�ʵ��ֵ=34000*1.5^��0.1*���ߵȼ�-1��*��������Ʒ�ʱ���
	"""
	return calcArmorHardiness( 34000, level, baseRate )

def calcVolaHardiness( level, baseRate ):
	"""
	�����;ö�ʵ��ֵ=46000*1.5^��0.1*���ߵȼ�-1��*��������Ʒ�ʱ���
	"""
	return calcArmorHardiness( 46000, level, baseRate )

def calcBreechHardiness( level, baseRate ):
	"""
	�����;ö�ʵ��ֵ=61000*1.5^��0.1*���ߵȼ�-1��*��������Ʒ�ʱ���
	"""
	return calcArmorHardiness( 61000, level, baseRate )

def calcFeetHardiness( level, baseRate ):
	"""
	Ь���;ö�ʵ��ֵ=51000*1.5^��0.1*���ߵȼ�-1��*��������Ʒ�ʱ���
	"""
	return calcArmorHardiness( 51000, level, baseRate )

def calcShieldHardiness( level, baseRate ):
	"""
	�����;ö�ʵ��ֵ=118000*1.5^��0.1*���ߵȼ�-1��*��������Ʒ�ʱ���
	"""
	return calcArmorHardiness( 118000, level, baseRate )

FUNC_CALCHARDINESS_MAPS = { ItemTypeEnum.ITEM_ARMOR_HEAD 	: calcHeadHardiness,
							ItemTypeEnum.ITEM_ARMOR_BODY 	: calcBodyHardiness,
							ItemTypeEnum.ITEM_ARMOR_HAUNCH 	: calcHaunchHardiness,
							ItemTypeEnum.ITEM_ARMOR_CUFF 	: calcCuffHardiness,
							ItemTypeEnum.ITEM_ARMOR_VOLA 	: calcVolaHardiness,
							ItemTypeEnum.ITEM_ARMOR_BREECH 	: calcBreechHardiness,
							ItemTypeEnum.ITEM_ARMOR_FEET 	: calcFeetHardiness,
							ItemTypeEnum.ITEM_WEAPON_SHIELD : calcShieldHardiness,
							}