# -*- coding: gb18030 -*-

import csdefine
import ItemTypeEnum

# 战士
class FighterFunc:
	def __init__( self ):
		"""
		"""
		pass

	def calcRoleHPMaxBase( self, selfEntity ):
		"""
		real entity method.
		virtual method
		生命上限值基础值
		"""
		return selfEntity.corporeity * 12

	def calcRoleMPMaxBase( self, selfEntity ):
		"""
		real entity method.
		virtual method
		法力上限值基础值
		"""
		return selfEntity.intellect * 5	# 数值修改2.1.03，原值5

	def calcRolePhysicsDPS( self, selfEntity ):
		"""
		virtual method.
		计算职业基础物理DPS
		"""
		return selfEntity.strength * 0.62	# 数值修改2.1.03，原值0.5

	def calcPhysicsDPS( self, selfEntity ):
		"""
		virtual method.
		计算职业（怪物）基础物理DPS
		"""
		return selfEntity.strength * 0.1

	def calcBaseDodgeProbability( self, selfEntity ):
		"""
		virtual method.
		计算职业基础闪躲率
		战士基础闪避（总公式中的基础值）=3%+角色当前敏捷/15000-1*（lv-1）/15000
		"""
		return 0.03 + selfEntity.dexterity / 15000 - 1.0 * ( selfEntity.level - 1 ) / 15000

	def calcBaseDoubleHitProbability( self, selfEntity ):
		"""
		virtual method.
		计算职业基础物理暴击率
		战士基础物理暴击率（总公式中的基础值）=5%+角色当前敏捷/10000-1*（lv-1）/10000
		"""
		return 0.05 + selfEntity.dexterity / 10000 - 1.0 * ( selfEntity.level - 1 ) / 10000

	def calcMagicBaseDoubleHitProbability( self, selfEntity ):
		"""
		virtual method.
		计算职业基础法术暴击率
		战士基础法术暴击率（总公式中的基础值）=5%+角色当前智力/10000-0.5*（lv-1）/10000
		"""
		return 0.05 + selfEntity.intellect / 10000 - 1.0 * ( selfEntity.level - 1 ) / 10000

	def calcBaseResistHitProbability( self, selfEntity ):
		"""
		virtual method.
		计算职业基础招架几率
		战士基础招架（总公式中的基础值）=3%+角色当前力量/12000-2*（lv-1）/12000
		"""
		return 0.03 + selfEntity.strength / 12000 - 2.0 * ( selfEntity.level - 1 ) / 12000

	def calcRoleMagicDamage( self, selfEntity ):
		"""
		virtual method.
		计算职业基础法术攻击力
		"""
		return selfEntity.intellect * 1.0	# 数值修改2.1.03，原值0.5

	def initElemProperty( self, selfEntity ):
		"""
		初始化各种元素
		"""
		selfEntity.elem_huo_damage_percent = 0
		selfEntity.elem_xuan_damage_percent = 0
		selfEntity.elem_lei_damage_percent = 0
		selfEntity.elem_bing_damage_percent = 0

# 剑客
class SwordmanFunc(  FighterFunc ):
	def calcRoleHPMaxBase( self, selfEntity ):
		"""
		real entity method.
		virtual method
		生命上限值基础值
		"""
		return selfEntity.corporeity * 10

	def calcRoleMPMaxBase( self, selfEntity ):
		"""
		real entity method.
		virtual method
		法力上限值基础值
		"""
		return selfEntity.intellect * 5	# 数值修改2.1.03，原值6

	def calcRolePhysicsDPS( self, selfEntity ):
		"""
		virtual method.
		计算职业基础物理DPS
		"""
		return selfEntity.strength * 0.77 + selfEntity.dexterity * 0.77
		# 数值修改2.1.03，原值0.5，0.5

	def calcPhysicsDPS( self, selfEntity ):
		"""
		virtual method.
		计算职业（怪物）基础物理DPS
		"""
		return selfEntity.strength * 0.07 + selfEntity.dexterity * 0.07

	def calcBaseDodgeProbability( self, selfEntity ):
		"""
		virtual method.
		计算职业基础闪躲率
		剑客基础闪避（总公式中的基础值）=3%+角色当前敏捷/15000-1.5*（lv-1）/15000
		"""
		return 0.03 + selfEntity.dexterity / 15000 - 1.5 * ( selfEntity.level - 1 ) / 15000

	def calcBaseDoubleHitProbability( self, selfEntity ):
		"""
		virtual method.
		计算职业基础物理暴击率
		剑客基础物理暴击率（总公式中的基础值）=20%+角色当前敏捷/10000-1.5*（lv-1）/10000
		"""
		return 0.2 + selfEntity.dexterity / 10000 - 1.5 * ( selfEntity.level - 1 ) / 10000

	def calcMagicBaseDoubleHitProbability( self, selfEntity ):
		"""
		virtual method.
		计算职业基础法术暴击率
		剑客基础法术暴击率（总公式中的基础值）=20%+角色当前智力/10000-1.5*（lv-1）/10000
		"""
		return 0.2 + selfEntity.intellect / 10000 - 1.5 * ( selfEntity.level - 1 ) / 10000

	def calcBaseResistHitProbability( self, selfEntity ):
		"""
		virtual method.
		计算职业基础招架几率
		剑客基础招架（总公式中的基础值）=2.5%+角色当前力量/12000-1.5*（lv-1）/12000
		"""
		return 0.025 + selfEntity.strength / 12000 - 1.5 * ( selfEntity.level - 1 ) / 12000

	def calcRoleMagicDamage( self, selfEntity ):
		"""
		virtual method.
		计算职业基础法术攻击力
		"""
		return selfEntity.intellect * 1.5		# 数值修改2.1.03，原值0.5

	def initElemProperty( self, selfEntity ):
		"""
		初始化各种元素
		"""
		selfEntity.elem_huo_damage_percent = 0
		selfEntity.elem_xuan_damage_percent = 0
		selfEntity.elem_lei_damage_percent = 0
		selfEntity.elem_bing_damage_percent = 0

# 射手
class ArcherFunc(  FighterFunc ):
	def calcRoleHPMaxBase( self, selfEntity ):
		"""
		real entity method.
		virtual method
		生命上限值基础值
		"""
		return selfEntity.corporeity * 8.5		# 数值修改2.1.03，原值10

	def calcRoleMPMaxBase( self, selfEntity ):
		"""
		real entity method.
		virtual method
		法力上限值基础值
		"""
		return selfEntity.intellect * 5	# 数值修改2.1.03，原值6

	def calcRolePhysicsDPS( self, selfEntity ):
		"""
		virtual method.
		计算职业基础物理DPS
		"""
		return selfEntity.strength * 0.57 + selfEntity.dexterity * 0.57
		# 数值修改2.1.03，原值0.3;0.6
	def calcPhysicsDPS( self, selfEntity ):
		"""
		virtual method.
		计算职业(怪物)基础物理DPS
		"""
		return selfEntity.strength * 0.04 + selfEntity.dexterity * 0.06

	def calcBaseDodgeProbability( self, selfEntity ):
		"""
		virtual method.
		计算职业基础闪躲率
		射手基础闪避（总公式中的基础值）=3%+角色当前敏捷/20000-2.5*（lv-1）/20000
		"""
		return 0.03 + selfEntity.dexterity / 20000 - 2.5 * ( selfEntity.level - 1 ) / 20000

	def calcBaseDoubleHitProbability( self, selfEntity ):
		"""
		virtual method.
		计算职业基础物理暴击率
		射手基础物理暴击率（总公式中的基础值）=5%+角色当前敏捷/15000-2.5*（lv-1）/15000
		"""
		return 0.05 + selfEntity.dexterity / 15000 - 2.5 * ( selfEntity.level - 1 ) / 15000

	def calcMagicBaseDoubleHitProbability( self, selfEntity ):
		"""
		virtual method.
		计算职业基础法术暴击率
		射手基础法术暴击率（总公式中的基础值）=5%+角色当前智力/10000-0.5*（lv-1）/10000
		"""
		return 0.05 + selfEntity.intellect / 10000 - 1.0 * ( selfEntity.level - 1 ) / 10000

	def calcBaseResistHitProbability( self, selfEntity ):
		"""
		virtual method.
		计算职业基础招架几率
		射手基础招架（总公式中的基础值）=2%+角色当前力量/12000-1.5*（lv-1）/12000
		"""
		return 0.02 + selfEntity.strength / 12000 - 1.5 * ( selfEntity.level - 1 ) / 12000

	def calcRoleMagicDamage( self, selfEntity ):
		"""
		virtual method.
		计算职业基础法术攻击力
		"""
		return selfEntity.intellect * 1.5		# 数值修改2.1.03，原值0.5

	def initElemProperty( self, selfEntity ):
		"""
		初始化各种元素
		"""
		selfEntity.elem_huo_damage_percent = 0
		selfEntity.elem_xuan_damage_percent = 0
		selfEntity.elem_lei_damage_percent = 0
		selfEntity.elem_bing_damage_percent = 0

# 法师
class MageFunc(  FighterFunc ):
	def calcRoleHPMaxBase( self, selfEntity ):
		"""
		real entity method.
		virtual method
		生命上限值基础值
		"""
		return selfEntity.corporeity * 8

	def calcRoleMPMaxBase( self, selfEntity ):
		"""
		real entity method.
		virtual method
		法力上限值基础值
		"""
		return selfEntity.intellect * 5

	def calcRolePhysicsDPS( self, selfEntity ):
		"""
		virtual method.
		计算职业基础物理DPS
		"""
		return selfEntity.strength * 1.0	# 数值修改2.1.03，原值0.5

	def calcPhysicsDPS( self, selfEntity ):
		"""
		virtual method.
		计算职业（怪物）基础物理DPS
		"""
		return selfEntity.strength * 0.07

	def calcBaseDodgeProbability( self, selfEntity ):
		"""
		virtual method.
		计算职业基础闪躲率
		法师基础闪避（总公式中的基础值）=3%+角色当前敏捷/15000
		"""
		return 0.03 + selfEntity.dexterity / 15000

	def calcBaseDoubleHitProbability( self, selfEntity ):
		"""
		virtual method.
		计算职业基础物理暴击率
		法师基础物理暴击率（总公式中的基础值）=5%+角色当前敏捷/10000-1*（lv-1）/10000
		"""
		return 0.05 + selfEntity.dexterity / 10000 - 1.0 * ( selfEntity.level - 1 ) / 10000

	def calcMagicBaseDoubleHitProbability( self, selfEntity ):
		"""
		virtual method.
		计算职业基础法术暴击率
		法师基础法术暴击率（总公式中的基础值）=5%+角色当前智力/15000-3.5*（lv-1）/15000
		"""
		return 0.05 + selfEntity.intellect / 15000 - 3.5 * ( selfEntity.level - 1 ) / 15000

	def calcBaseResistHitProbability( self, selfEntity ):
		"""
		virtual method.
		计算职业基础招架几率
		法师基础招架（总公式中的基础值）=1%+角色当前力量/8000
		"""
		return 0.01 + selfEntity.strength / 8000

	def calcRoleMagicDamage( self, selfEntity ):
		"""
		virtual method.
		计算职业基础法术攻击力
		"""
		return selfEntity.intellect * 1.5	# 数值修改2.1.03，原值2.0

	def initElemProperty( self, selfEntity ):
		"""
		初始化各种元素
		"""
		selfEntity.elem_huo_damage_percent = 0
		selfEntity.elem_xuan_damage_percent = 0
		selfEntity.elem_lei_damage_percent = 0
		selfEntity.elem_bing_damage_percent = 0

# 战斗公式基数
class CombatRadix:
	"""
	角色战斗相关参数
	"""
	def __init__( self, **argw ):
		"""
		"""
		self.strength = 0 #力量(int)
		self.dexterity = 0 #敏捷(int)
		self.intellect = 0 #智力(int)
		self.corporeity = 0 #体质(int)
		self.physics_dps = 0 #物理攻击力(int)
		self.magic_dps = 0 #法术攻击力(int)
		self.strength_value = 0 #力量每级加值(float)
		self.dexterity_value = 0 #敏捷每级加值(float)
		self.intellect_value = 0.0 #智力每级加值(float)
		self.corporeity_value = 0.0 #体质每级加值(float)
		self.physics_dps_value = 0.0 #物理攻击力每级加值(float)
		self.magic_dps_value = 0.0 #法术攻击力每级加值(float)
		self.HP_regen_base = 0.0 #HP恢复值(float)
		self.MP_regen_base = 0.0 #MP恢复值(float)
		self.MP_Max_value = 0.0 #MP上限每级加值(float)
		# init
		self.__dict__.update( argw )

# 各职业战斗公式基数
ROLE_COMBAT_RADIX = {
		# 战士
		csdefine.CLASS_FIGHTER	:	CombatRadix(
											strength = 13, #力量(int)
											dexterity = 7, #敏捷(int)
											intellect = 4, #智力(int)
											corporeity = 16, #体质(int)
											physics_dps = 6, #物理攻击力(int)
											magic_dps = 0, #法术攻击力(int)
											strength_value = 2.0, #力量每级加值(float)
											dexterity_value = 1.0, #敏捷每级加值(float)
											intellect_value = 1.0, #智力每级加值(float)
											corporeity_value = 2.5, #体质每级加值(float)
											physics_dps_value = 4.0, #物理攻击力每级加值(float)
											magic_dps_value = 0.0, #法术攻击力每级加值(float)
											HP_regen_base = 10.0, #HP恢复值(float)
											MP_regen_base = 10.0, #MP恢复值(float)
											MP_Max_value = 15.0, #MP上限每级加值(float)
											),
		# 剑客
		csdefine.CLASS_SWORDMAN	:	CombatRadix(
											strength = 10, #力量(int)
											dexterity = 10, #敏捷(int)
											intellect = 9, #智力(int)
											corporeity = 11, #体质(int)
											physics_dps = 0, #物理攻击力(int)
											magic_dps = 6, #法术攻击力(int)
											strength_value = 1.5, #力量每级加值(int)
											dexterity_value = 1.5, #敏捷每级加值(int)
											intellect_value = 1.5, #智力每级加值(float)
											corporeity_value = 2.0, #体质每级加值(float)
											physics_dps_value = 4.0, #物理攻击力每级加值(float)
											magic_dps_value = 4.0, #法术攻击力每级加值(float)
											HP_regen_base = 10.0, #HP恢复值(float)
											MP_regen_base = 10.0, #MP恢复值(float)
											MP_Max_value = 15.0, #MP上限每级加值(float)
											),
		# 射手
		csdefine.CLASS_ARCHER		:	CombatRadix(
											strength = 10, #力量(int)
											dexterity = 13, #敏捷(int)
											intellect = 6, #智力(int)
											corporeity = 11, #体质(int)
											physics_dps = 6, #物理攻击力(int)
											magic_dps = 4, #法术攻击力(int)
											strength_value = 1.5, #力量每级加值(int)
											dexterity_value = 2.5, #敏捷每级加值(int)
											intellect_value = 1.0, #智力每级加值(float)
											corporeity_value = 1.5, #体质每级加值(float)
											physics_dps_value = 3.0, #物理攻击力每级加值(float)
											magic_dps_value = 5.5, #法术攻击力每级加值(float)
											HP_regen_base = 10.0, #HP恢复值(float)
											MP_regen_base = 10.0, #MP恢复值(float)
											MP_Max_value = 15.0, #MP上限每级加值(float)
											),
		# 法师
		csdefine.CLASS_MAGE		:	CombatRadix(
											strength = 6, #力量(int)
											dexterity = 6, #敏捷(int)
											intellect = 18, #智力(int)
											corporeity = 10, #体质(int)
											physics_dps = 0, #物理攻击力(int)
											magic_dps = 0, #法术攻击力(int)
											strength_value = 1.0, #力量每级加值(int)
											dexterity_value = 1.0, #敏捷每级加值(int)
											intellect_value = 3.0, #智力每级加值(float)
											corporeity_value = 1.5, #体质每级加值(float)
											physics_dps_value = 0.0, #物理攻击力每级加值(float)
											magic_dps_value = 3.0, #法术攻击力每级加值(float)
											HP_regen_base = 10.0, #HP恢复值(float)
											MP_regen_base = 10.0, #MP恢复值(float)
											MP_Max_value = 15.0, #MP上限每级加值(float)
											),
		# 巫师
		csdefine.CLASS_WARLOCK	:	CombatRadix(
											strength = 0, #力量(int)
											dexterity = 0, #敏捷(int)
											intellect = 0, #智力(int)
											corporeity = 0, #体质(int)
											physics_dps = 0, #物理攻击力(int)
											magic_dps = 0, #法术攻击力(int)
											strength_value = 0.0, #力量每级加值(float)
											dexterity_value = 0.0, #敏捷每级加值(float)
											intellect_value = 0.0, #智力每级加值(float)
											corporeity_value = 0.0, #体质每级加值(float)
											physics_dps_value = 0.0, #物理攻击力每级加值(float)
											magic_dps_value = 0.0, #法术攻击力每级加值(float)
											HP_regen_base = 10.0, #HP恢复值(float)
											MP_regen_base = 10.0, #MP恢复值(float)
											MP_Max_value = 0.0, #MP上限每级加值(float)
											),
		# 祭师
		csdefine.CLASS_PRIEST		:	CombatRadix(
											strength = 0, #力量(int)
											dexterity = 0, #敏捷(int)
											intellect = 0, #智力(int)
											corporeity = 0, #体质(int)
											physics_dps = 0, #物理攻击力(int)
											magic_dps = 0, #法术攻击力(int)
											strength_value = 0.0, #力量每级加值(float)
											dexterity_value = 0.0, #敏捷每级加值(float)
											intellect_value = 0.0, #智力每级加值(float)
											corporeity_value = 0.0, #体质每级加值(float)
											physics_dps_value = 0.0, #物理攻击力每级加值(float)
											magic_dps_value = 0.0, #法术攻击力每级加值(float)
											HP_regen_base = 10.0, #HP恢复值(float)
											MP_regen_base = 10.0, #MP恢复值(float)
											MP_Max_value = 0.0, #MP上限每级加值(float)
											),
	}	# end of ROLE_COMBAT_RADIX

# 各职业战斗公式基数
ENTITY_COMBAT_BASE_EXPRESSION = {
		# 战士
		csdefine.CLASS_FIGHTER	:	FighterFunc(),
		# 剑客
		csdefine.CLASS_SWORDMAN	:	SwordmanFunc(),
		# 射手
		csdefine.CLASS_ARCHER		:	ArcherFunc(),
		# 法师
		csdefine.CLASS_MAGE		:	MageFunc(),
		# 巫师
		csdefine.CLASS_WARLOCK	:	FighterFunc(),
		# 祭师
		csdefine.CLASS_PRIEST		:	FighterFunc(),
		# 强防战士
		csdefine.CLASS_PALADIN	:	FighterFunc(),
	}	# end of ROLE_COMBAT_RADIX


# 点数转换率计算公式
def valueToPer( value, level ):
	"""
	装备属性中点数转换成率的公式
	"""
	return ( 0.01012 * value)/( 1.5 **( 0.091 * level - 1 ) )


# 物理攻击命中/法术攻击命中计算公式
def calcHitProbability( caster, target ):
	"""
	计算物理命中
	
	物理命中率 = max（0,min（1, 攻方物理命中终值 - 守方闪避终值））+等级修正）
	等级修正 = 1%*(int((攻方等级-守方等级)/5)+(int(攻方等级<守方等级)*1))
	"""
	levelAdjust = ( int( (caster.level - target.level)/5 ) + ( int(caster.level < target.level)*1 ) ) * 0.01
	return max( 0,min( 1,caster.hitProbability - target.dodge_probability ) ) + levelAdjust

def calcMagicHitProbability( caster, target ):
	"""
	计算法术命中
	
	法术命中率 = max（0,min（1, 攻方法术命中终值 - 守方闪避终值））+等级修正）
	等级修正 = 1%*(int((攻方等级-守方等级)/5)+(int(攻方等级<守方等级)*1))
	"""
	levelAdjust = ( int( (caster.level - target.level)/5 ) + ( int(caster.level < target.level)*1 ) ) * 0.01
	return max( 0,min( 1,caster.magic_hitProbability - target.dodge_probability ) ) + levelAdjust


# 防具耐久值计算公式
def calcArmorHardiness( baseValue, level, baseRate ):
	"""
	耐久度实际值=部位基础值*1.5^（0.1*道具等级-1）*基础属性品质比率
	"""
	return baseValue * 1.5 ** ( 0.1 * level - 1 ) * baseRate

def calcHeadHardiness( level, baseRate ):
	"""
	头部耐久度实际值=56000*1.5^（0.1*道具等级-1）*基础属性品质比率
	"""
	return calcArmorHardiness( 56000, level, baseRate )

def calcBodyHardiness( level, baseRate ):
	"""
	胸甲耐久度实际值=65000*1.5^（0.1*道具等级-1）*基础属性品质比率
	"""
	return calcArmorHardiness( 65000, level, baseRate )

def calcHaunchHardiness( level, baseRate ):
	"""
	腰带耐久度实际值=40000*1.5^（0.1*道具等级-1）*基础属性品质比率
	"""
	return calcArmorHardiness( 40000, level, baseRate )

def calcCuffHardiness( level, baseRate ):
	"""
	护腕耐久度实际值=34000*1.5^（0.1*道具等级-1）*基础属性品质比率
	"""
	return calcArmorHardiness( 34000, level, baseRate )

def calcVolaHardiness( level, baseRate ):
	"""
	手套耐久度实际值=46000*1.5^（0.1*道具等级-1）*基础属性品质比率
	"""
	return calcArmorHardiness( 46000, level, baseRate )

def calcBreechHardiness( level, baseRate ):
	"""
	裤子耐久度实际值=61000*1.5^（0.1*道具等级-1）*基础属性品质比率
	"""
	return calcArmorHardiness( 61000, level, baseRate )

def calcFeetHardiness( level, baseRate ):
	"""
	鞋子耐久度实际值=51000*1.5^（0.1*道具等级-1）*基础属性品质比率
	"""
	return calcArmorHardiness( 51000, level, baseRate )

def calcShieldHardiness( level, baseRate ):
	"""
	盾牌耐久度实际值=118000*1.5^（0.1*道具等级-1）*基础属性品质比率
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