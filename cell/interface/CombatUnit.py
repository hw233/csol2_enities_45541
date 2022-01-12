# -*- coding: gb18030 -*-

"""
可战斗单位

$Id: CombatUnit.py,v 1.76 2008-09-04 07:44:14 kebiao Exp $
"""

import sys
import BigWorld
from bwdebug import *
import csdefine
import csstatus
import Const
import ECBExtend
from State import State
from SpellUnit import SpellUnit
from EntityRelationTable import EntityRelationTable
import csconst
import math
import random
import Language
import CombatUnitConfig
import ShareTexts as ST
from RelationStaticModeMgr import RelationStaticModeMgr
import RelationDynamicObjImpl

g_relationStaticMgr = RelationStaticModeMgr.instance()


# 注：由于策划案中未指定各怪物的类型（战士、剑客等），导致有些算法不能使用，
#     因此此处的算法为默认算法，而主角则继承其接口重写算法

def calcProperty( baseVal, extraVal, percentVal, value ):
	"""
	创世基础计算总公式
	计算值=（基础值+附加值）*（1+加成）+加值
	result = ( corporeity_base + corporeity_extra ) * ( 1 + corporeity_percent ) + corporeity_value
	( 100 + 0 ) * (1 + 0.0 ) + 0 = 100
	( 100 + 0 ) * (1 + 0.1 ) + 0 = 110

	@param baseVal: 基础值
	@param extraVal: 附加值
	@param percentVal: 加成
	@param value: 加值
	"""
	return ( baseVal + extraVal ) * ( 1 + percentVal ) + value

class CombatUnit( State, SpellUnit, EntityRelationTable ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		State.__init__( self )
		SpellUnit.__init__( self )
		EntityRelationTable.__init__( self )

		self.friendlyCamps = [ self.getCamp() ]	#默认为自己的阵营
		if Language.LANG == Language.LANG_GBK:
			self.double_hit_multiple_base = 20000
			self.magic_double_hit_multiple_base = 20000

	def initAvatar( self ):
		"""
		virtual method = 0.
		初始化avatar，主角和怪物(或NPC)可能会有不同的初始化方式
		"""
		pass

	def calcDynamicProperties( self ):
		"""
		重新计算所有的属性
		"""
		#必须先初始化的部分
		self.calcStrength()							# 力量
		self.calcDexterity()						# 敏捷
		self.calcIntellect()						# 智力
		self.calcCorporeity()						# 体质
		self.calcPhysicsDPS()						# 物理 DPS
		self.calcWaveDPS()							# dps 波动

		self.calcHPMax()							# HP 最大值
		self.calcMPMax()							# MP 最大值
		self.calcHPCureSpeed()						# HP 治愈速度
		self.calcMPCureSpeed()						# MP 治愈速度
		self.calcDoubleHitProbability()				# 物理暴击率
		self.calcMagicDoubleHitProbability()		# 法术暴击率
		self.calcResistHitProbability()				# 物理招架率
		self.calcDodgeProbability()					# 物理闪避率
		self.calcReduceRoleDamage()                           #御敌伤害减免
		self.calcAddRoleDamage()                           #破敌
		self.calcArmor()							# 物理防御
		self.calcMagicArmor()						# 法术防御
		self.calcMoveSpeed()						# 移动速度
		self.calcHitSpeed()							# 攻击速度
		self.calcRange()							# 攻击距离
		self.calcDamageDerate()						# 物理伤害减免
		self.calcMagicDamageDerate()				# 法术伤害减免
		self.calcDamageDerateRatio()				# 物理伤害减免率
		self.calcMagicDamageDerateRatio()			# 法术伤害减免率
		self.calcHitProbability()					# 物理命中率
		self.calcMagicHitProbability()				# 法术命中率
		self.calcResistYuanli()						# 计算元力
		self.calcResistLingli()						# 计算灵力
		self.calcResistTipo()						# 计算体魄
		self.calcResistGiddyProbability()			# 抵抗眩晕几率
		self.calcResistFixProbability()				# 抵抗定身几率
		self.calcResistChenmoProbability()			# 抵抗沉默几率
		self.calcResistSleepProbability()			# 抵抗睡眠几率
		self.calcDoubleHitMultiple()				# 物理暴击倍数
		self.calcMagicDoubleHitMultiple()			# 法术暴击倍数
		self.calcResistHitDerate()					# 招架减伤

		#需要后初始化
		self.calcDamageMin()						# 最小物理攻击力
		self.calcDamageMax()						# 最大物理攻击力
		self.calcMagicDamage()						# 法术攻击力

		# 计算元素属性
		# self.initElemProperty()						# 首先初始化元素
		self.calcElemHuoDamage()					# 计算火元素伤害
		self.calcElemXuanDamage()					# 计算玄元素伤害
		self.calcElemLeiDamage()					# 计算雷元素伤害
		self.calcElemBingDamage()					# 计算冰元素伤害

		self.calcElemHuoDeepRatio()					# 计算火元素伤害加深率
		self.calcElemXuanDeepRatio()				# 计算玄元素伤害加深率
		self.calcElemLeiDeepRatio()					# 计算雷元素伤害加深率
		self.calcElemBingDeepRatio()				# 计算冰元素伤害加深率

		self.calcElemHuoDerateRatio()				# 计算火元素抗性
		self.calcElemXuanDerateRatio()				# 计算玄元素抗性
		self.calcElemLeiDerateRatio()				# 计算雷元素抗性
		self.calcElemBingDerateRatio()				# 计算冰元素抗性

	def getClass( self ):
		"""
		取得自身职业
		@return: INT
		"""
		return self.raceclass & csdefine.RCMASK_CLASS

	def calcStrengthBase( self ):
		"""
		计算力量基础值
		"""
		pass

	def calcStrength( self ):
		"""
		计算力量
		"""
		self.calcStrengthBase()
		strength = calcProperty( self.strength_base, \
								self.strength_extra, \
								self.strength_percent / csconst.FLOAT_ZIP_PERCENT, \
								self.strength_value )
		if strength < 0:strength = 0
		if self.strength != strength: self.strength = strength

	def calcDexterityBase( self ):
		"""
		计算敏捷基础值
		"""
		pass

	def calcDexterity( self ):
		"""
		计算敏捷
		"""
		self.calcDexterityBase()
		dexterity = calcProperty( self.dexterity_base, \
								self.dexterity_extra, \
								self.dexterity_percent / csconst.FLOAT_ZIP_PERCENT, \
								self.dexterity_value )
		if dexterity < 0:dexterity = 0
		if self.dexterity != dexterity: self.dexterity = dexterity

	def calcIntellectBase( self ):
		"""
		计算智力基础值
		"""
		pass

	def calcIntellect( self ):
		"""
		计算智力
		"""
		self.calcIntellectBase()
		intellect = calcProperty( self.intellect_base,
									self.intellect_extra, \
									self.intellect_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.intellect_value )
		if intellect < 0:intellect = 0
		if self.intellect != intellect: self.intellect = intellect

	def calcCorporeityBase( self ):
		"""
		计算体质基础值
		"""
		pass

	def calcCorporeity( self ):
		"""
		计算体质
		"""
		self.calcCorporeityBase()
		corporeity = calcProperty( self.corporeity_base, \
									self.corporeity_extra, \
									self.corporeity_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.corporeity_value )
		if corporeity < 0:corporeity = 0
		if self.corporeity != corporeity: self.corporeity = corporeity

	def calcPhysicsDPSBase( self ):
		"""
		计算物理DPS_base值
		"""
		self.physics_dps_base = int( CombatUnitConfig.ENTITY_COMBAT_BASE_EXPRESSION[self.getClass()].calcPhysicsDPS( self ) * csconst.FLOAT_ZIP_PERCENT )

	def calcPhysicsDPS( self ):
		"""
		计算物理DPS
		"""
		self.calcPhysicsDPSBase()
		physics_dps = calcProperty( self.physics_dps_base / csconst.FLOAT_ZIP_PERCENT, \
									self.physics_dps_extra / csconst.FLOAT_ZIP_PERCENT, \
									self.physics_dps_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.physics_dps_value / csconst.FLOAT_ZIP_PERCENT )
		if physics_dps < 0:physics_dps = 0.0
		if self.physics_dps != physics_dps: self.physics_dps = physics_dps

	def calcWaveDPS( self ):
		"""
		计算DPS波动
		"""
		self.wave_dps = calcProperty( self.wave_dps_base / csconst.FLOAT_ZIP_PERCENT, \
									self.wave_dps_extra / csconst.FLOAT_ZIP_PERCENT, \
									self.wave_dps_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.wave_dps_value / csconst.FLOAT_ZIP_PERCENT )

	def calcHPMaxBase( self ):
		"""
		real entity method.
		virtual method
		生命上限值基础值
		"""
		self.HP_Max_base = self.corporeity * 10

	def calcHPMax( self ):
		"""
		real entity method.
		virtual method
		生命上限值
		"""
		if self.queryTemp( "SAME_TYPE_BUFF_REPLACE", False ): return
		if self.queryTemp( "SAME_TYPE_SKILL_REPLACE", False ): return
		self.calcHPMaxBase()
		HP_Max = int( calcProperty( self.HP_Max_base, \
									self.HP_Max_extra, \
									self.HP_Max_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.HP_Max_value ) )

		if self.HP_Max != HP_Max:
			self.HP_Max = HP_Max
			if self.HP > HP_Max:
				self.HP = HP_Max

	def calcMPMaxBase( self ):
		"""
		real entity method.
		virtual method
		法力上限值基础值
		"""
		self.MP_Max_base = self.intellect * 10

	def calcMPMax( self ):
		"""
		real entity method.
		virtual method
		法力上限值
		"""
		if self.queryTemp( "SAME_TYPE_BUFF_REPLACE", False ): return
		if self.queryTemp( "SAME_TYPE_SKILL_REPLACE", False ): return
		self.calcMPMaxBase()
		MP_Max = int( calcProperty( self.MP_Max_base, \
									self.MP_Max_extra, \
									self.MP_Max_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.MP_Max_value ) )

		if self.MP_Max != MP_Max:
			self.MP_Max = MP_Max
			if self.MP > MP_Max:
				self.MP = MP_Max

	def calcHPCureSpeed( self ):
		"""
		计算生命恢复速度
		角色的隐藏属性，决定角色每3秒可以恢复的生命数值。战斗时无效。数值读表。
		"""
		self.HP_regen = int( calcProperty( self.HP_regen_base, \
										self.HP_regen_extra, \
										self.HP_regen_percent / csconst.FLOAT_ZIP_PERCENT, \
										self.HP_regen_value ) )

	def calcMPCureSpeed( self ):
		"""
		角色的隐藏属性，决定角色每3秒可以恢复的法力数值。战斗时无效。数值读表。
		"""
		self.MP_regen = int( calcProperty( self.MP_regen_base, \
										self.MP_regen_extra, \
										self.MP_regen_percent / csconst.FLOAT_ZIP_PERCENT, \
										self.MP_regen_value ) )

	def calcMagicDamageBase( self ):
		"""
		virtual method
		法术攻击力
		"""
		self.magic_damage_base = int( self.intellect * 0.14 ) #基础法术攻击力（总公式中的基础值）=智力*0.14

	def calcMagicDamage( self ):
		"""
		virtual method
		法术攻击力
		"""
		self.calcMagicDamageBase()
		magic_damage = math.ceil( calcProperty( self.magic_damage_base, \
											self.magic_damage_extra, \
											self.magic_damage_percent / csconst.FLOAT_ZIP_PERCENT, \
											self.magic_damage_value ) )
		if magic_damage < 0:magic_damage = 0.0
		if self.magic_damage != magic_damage: self.magic_damage = magic_damage

	def calcDamageMinBase( self ):
		"""
		计算最小物理攻击力 基础值
		"""
		self.damage_min_base = int( self.physics_dps * self.hit_speed * ( 1.0 - self.wave_dps ) )

	def calcDamageMin( self ):
		"""
		计算最小物理攻击力
		"""
		self.calcDamageMinBase()
		damage_min = calcProperty( self.damage_min_base, \
									self.damage_min_extra, \
									self.damage_min_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.damage_min_value )
		if damage_min < 0:damage_min = 0
		if self.damage_min != damage_min: self.damage_min = damage_min

	def calcDamageMaxBase( self ):
		"""
		计算最大物理攻击力 基础值
		"""
		self.damage_max_base = int( self.physics_dps * self.hit_speed * ( 1.0 + self.wave_dps ) )

	def calcDamageMax( self ):
		"""
		计算最大物理攻击力
		"""
		self.calcDamageMaxBase()
		damage_max = calcProperty( self.damage_max_base, \
									self.damage_max_extra, \
									self.damage_max_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.damage_max_value )
		if damage_max < 0:damage_max = 0
		if self.damage_max != damage_max: self.damage_max = damage_max

	def calcDoubleHitProbabilityBase( self ):
		"""
		物理爆击率
		"""
		self.double_hit_probability_base = int( CombatUnitConfig.ENTITY_COMBAT_BASE_EXPRESSION[self.getClass()].calcBaseDoubleHitProbability( self ) * csconst.FLOAT_ZIP_PERCENT )

	def calcDoubleHitProbability( self ):
		"""
		物理爆击率
		"""
		self.calcDoubleHitProbabilityBase()
		double_hit_probability = max( calcProperty( self.double_hit_probability_base / csconst.FLOAT_ZIP_PERCENT, \
													self.double_hit_probability_extra / csconst.FLOAT_ZIP_PERCENT, \
													self.double_hit_probability_percent / csconst.FLOAT_ZIP_PERCENT, \
													self.double_hit_probability_value / csconst.FLOAT_ZIP_PERCENT ), 0.0 )
		if self.double_hit_probability != double_hit_probability: self.double_hit_probability = double_hit_probability

	def calcMagicDoubleHitProbabilityBase( self ):
		"""
		法术爆击率
		"""
		self.magic_double_hit_probability_base = int( CombatUnitConfig.ENTITY_COMBAT_BASE_EXPRESSION[self.getClass()].calcMagicBaseDoubleHitProbability( self ) * csconst.FLOAT_ZIP_PERCENT )

	def calcMagicDoubleHitProbability( self ):
		"""
		法术爆击率
		"""
		self.calcMagicDoubleHitProbabilityBase()
		magic_double_hit_probability = max( calcProperty( self.magic_double_hit_probability_base / csconst.FLOAT_ZIP_PERCENT, \
														self.magic_double_hit_probability_extra / csconst.FLOAT_ZIP_PERCENT, \
														self.magic_double_hit_probability_percent / csconst.FLOAT_ZIP_PERCENT, \
														self.magic_double_hit_probability_value / csconst.FLOAT_ZIP_PERCENT ), 0.0 )
		if self.magic_double_hit_probability != magic_double_hit_probability: self.magic_double_hit_probability = magic_double_hit_probability

	def calcResistHitProbabilityBase( self ):
		"""
		招架率
		招架率是指招架发生的几率，普通物理攻击，物理技能攻击，都能够被招架。但是法术攻击，不能被招架。招架成功后，角色受到的伤害降低50%
		"""
		self.resist_hit_probability_base = int( CombatUnitConfig.ENTITY_COMBAT_BASE_EXPRESSION[self.getClass()].calcBaseResistHitProbability( self ) * csconst.FLOAT_ZIP_PERCENT )

	def calcResistHitProbability( self ):
		"""
		招架率
		招架率是指招架发生的几率，普通物理攻击，物理技能攻击，都能够被招架。但是法术攻击，不能被招架。招架成功后，角色受到的伤害降低50%
		"""
		self.calcResistHitProbabilityBase()
		resist_hit_probability = calcProperty( self.resist_hit_probability_base / csconst.FLOAT_ZIP_PERCENT, \
											self.resist_hit_probability_extra / csconst.FLOAT_ZIP_PERCENT, \
											self.resist_hit_probability_percent / csconst.FLOAT_ZIP_PERCENT, \
											self.resist_hit_probability_value / csconst.FLOAT_ZIP_PERCENT )
		if self.resist_hit_probability != resist_hit_probability: self.resist_hit_probability = resist_hit_probability

	def calcDodgeProbabilityBase( self ):
		"""
		闪避率 基础值
		角色闪躲对方攻击的几率。普通物理攻击可以被闪避。物理技能攻击和法术技能攻击不能被闪避。闪避成功后，被攻击方本次攻击不受任何伤害。
		"""
		self.dodge_probability_base = int( CombatUnitConfig.ENTITY_COMBAT_BASE_EXPRESSION[self.getClass()].calcBaseDodgeProbability( self ) * csconst.FLOAT_ZIP_PERCENT )

	def calcDodgeProbability( self ):
		"""
		闪避率
		角色闪躲对方攻击的几率。普通物理攻击可以被闪避。物理技能攻击和法术技能攻击不能被闪避。闪避成功后，被攻击方本次攻击不受任何伤害。
		"""
		self.calcDodgeProbabilityBase()
		dodge_probability = calcProperty( self.dodge_probability_base / csconst.FLOAT_ZIP_PERCENT, \
										self.dodge_probability_extra / csconst.FLOAT_ZIP_PERCENT, \
										self.dodge_probability_percent / csconst.FLOAT_ZIP_PERCENT, \
										self.dodge_probability_value / csconst.FLOAT_ZIP_PERCENT )
		if self.dodge_probability != dodge_probability: self.dodge_probability = dodge_probability

	def calcReduceRoleDamageBase( self ):
		"""
		御敌 基础值
		受到其他玩家的伤害减少，基础值出生时存在
		"""
		self.reduce_role_damage_base = 0

	def calcReduceRoleDamage( self ):
		"""
		御敌伤害减免率
		"""
		self.calcReduceRoleDamageBase()
		reduce_role_damage = calcProperty( self.reduce_role_damage_base / csconst.FLOAT_ZIP_PERCENT, \
										self.reduce_role_damage_extra / csconst.FLOAT_ZIP_PERCENT, \
										self.reduce_role_damage_percent / csconst.FLOAT_ZIP_PERCENT, \
										self.reduce_role_damage_value / csconst.FLOAT_ZIP_PERCENT )
		if self.reduce_role_damage != reduce_role_damage: self.reduce_role_damage = reduce_role_damage
		
	def calcAddRoleDamageBase( self ):
		"""
		破敌 基础值
		增加对玩家的伤害，基础值出生时存在
		"""
		self.add_role_damage_base = 0

	def calcAddRoleDamage( self ):
		"""
		破敌--对玩家伤害增加率
		"""
		self.calcAddRoleDamageBase()
		add_role_damage = calcProperty( self.add_role_damage_base / csconst.FLOAT_ZIP_PERCENT, \
										self.add_role_damage_extra / csconst.FLOAT_ZIP_PERCENT, \
										self.add_role_damage_percent / csconst.FLOAT_ZIP_PERCENT, \
										self.add_role_damage_value / csconst.FLOAT_ZIP_PERCENT )
		if self.add_role_damage != add_role_damage: self.add_role_damage = add_role_damage	

	def calcArmorBase( self ):
		"""
		virtual method
		物理防御值	表示当角色受到物理攻击时，能对此物理攻击力进行削减的能力。
		"""
		pass

	def calcArmor( self ):
		"""
		virtual method
		物理防御值	表示当角色受到物理攻击时，能对此物理攻击力进行削减的能力。
		"""
		self.calcArmorBase()
		armor = max( int( math.ceil( calcProperty( self.armor_base, \
													self.armor_extra, \
													self.armor_percent / csconst.FLOAT_ZIP_PERCENT, \
													self.armor_value ) ) ), 0 )
		if self.armor != armor: self.armor = armor

	def calcMagicArmorBase( self ):
		"""
		virtual method
		法术防御值	表示当角色受到法术攻击时，能对此法术攻击力进行削减的能力。
		"""
		pass

	def calcMagicArmor( self ):
		"""
		virtual method
		法术防御值	表示当角色受到法术攻击时，能对此法术攻击力进行削减的能力。
		"""
		self.calcMagicArmorBase()
		magic_armor = max( int( math.ceil( calcProperty( self.magic_armor_base, \
															self.magic_armor_extra, \
															self.magic_armor_percent / csconst.FLOAT_ZIP_PERCENT, \
															self.magic_armor_value ) ) ), 0)
		if self.magic_armor != magic_armor: self.magic_armor = magic_armor

	def calcMoveSpeed( self ):
		"""
		virtual method.
		移动速度 = 移动速度基础值 + 移动速度加值
		npc移动速度（总公式中的基础值）=4.5m/s
		"""
		if self.hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT ) and self.isEntityType( csdefine.ENTITY_TYPE_ROLE ):return #处于飞行传送状态不响应速度值修改
		move_speed = calcProperty( self.move_speed_base / csconst.FLOAT_ZIP_PERCENT, \
									self.move_speed_extra / csconst.FLOAT_ZIP_PERCENT, \
									self.move_speed_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.move_speed_value / csconst.FLOAT_ZIP_PERCENT )
		if self.move_speed != move_speed:
			if move_speed < 0:
				move_speed = 0.01
			self.setMoveSpeed( move_speed )

	def calcHitSpeedBase( self ):
		"""
		攻击速度
		"""
		pass

	def calcHitSpeed( self ):
		"""
		攻击速度
		"""
		# hit_speed结果为攻击延迟, 单位: 秒
		self.calcHitSpeedBase()
		hit_speed = calcProperty( self.hit_speed_base / csconst.FLOAT_ZIP_PERCENT, \
									self.hit_speed_extra / csconst.FLOAT_ZIP_PERCENT, \
									self.hit_speed_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.hit_speed_value / csconst.FLOAT_ZIP_PERCENT )
		if self.hit_speed != hit_speed: self.hit_speed = hit_speed

	def calcRange( self ):
		"""
		virtual method.
		计算攻击距离
		"""
		range = calcProperty( self.range_base / csconst.FLOAT_ZIP_PERCENT, \
								self.range_extra / csconst.FLOAT_ZIP_PERCENT, \
								self.range_percent / csconst.FLOAT_ZIP_PERCENT, \
								self.range_value / csconst.FLOAT_ZIP_PERCENT )
		if self.range != range: self.range = range

	def calcDamageDerate( self ):
		"""
		计算物理伤害减免值
		"""
		self.damage_derate = calcProperty( self.damage_derate_base, \
								self.damage_derate_extra, \
								self.damage_derate_percent / csconst.FLOAT_ZIP_PERCENT, \
								self.damage_derate_value )

	def calcMagicDamageDerate( self ):
		"""
		计算法术伤害减免值
		"""
		self.magic_damage_derate = calcProperty( self.magic_damage_derate_base, \
													self.magic_damage_derate_extra, \
													self.magic_damage_derate_percent / csconst.FLOAT_ZIP_PERCENT, \
													self.magic_damage_derate_value )

	def calcDamageDerateRatio( self ):
		"""
		计算物理伤害减免率
		"""
		self.damage_derate_ratio = calcProperty( self.damage_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.damage_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.damage_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.damage_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT

	def calcMagicDamageDerateRatio( self ):
		"""
		计算法术伤害减免率
		"""
		self.magic_damage_derate_ratio = calcProperty( self.magic_damage_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
													self.magic_damage_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
													self.magic_damage_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
													self.magic_damage_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT

	def calcHitProbability( self ):
		"""
		计算物理命中率
		按照策划要求 显示到客户端默认是显示与自己同一级别的目标算出的概率
		参考公式文档中物理命中率计算，如下：
		基础物理命中率（总公式中的基础值）=95% -（被攻击方等级-攻击方等级）^1.61*3%
		如果（被攻击方等级-攻击方等级）<0，则（被攻击方等级-攻击方等级）=0项计为0。
		如果95% -（被攻击方等级-攻击方等级）^1.61*3%<1%。则此项取1%。
		物理普通攻击和物理技能攻击，都采用物理命中率
		法术攻击采用法术命中率
		"""
		hitProbability = calcProperty( self.hitProbability_base / csconst.FLOAT_ZIP_PERCENT, \
										self.hitProbability_extra / csconst.FLOAT_ZIP_PERCENT, \
										self.hitProbability_percent / csconst.FLOAT_ZIP_PERCENT, \
										self.hitProbability_value / csconst.FLOAT_ZIP_PERCENT )
		if self.hitProbability != hitProbability: self.hitProbability = hitProbability

	def calcMagicHitProbability( self ):
		"""
		计算法术命中率
		按照策划要求 显示到客户端默认是显示与自己同一级别的目标算出的概率
		参考公式文档中法术命中率计算，公式如下：
		基础法术命中率（总公式中的基础值）=95% -（被攻击方等级-攻击方等级）^1.61*3%
		如果（被攻击方等级-攻击方等级）<0，则（被攻击方等级-攻击方等级）=0项计为0。
		如果95% -（被攻击方等级-攻击方等级）^1.61*3%<1%。则此项取1%。
		"""
		magic_hitProbability = calcProperty( self.magic_hitProbability_base / csconst.FLOAT_ZIP_PERCENT, \
											self.magic_hitProbability_extra / csconst.FLOAT_ZIP_PERCENT, \
											self.magic_hitProbability_percent / csconst.FLOAT_ZIP_PERCENT, \
											self.magic_hitProbability_value / csconst.FLOAT_ZIP_PERCENT )
		if self.magic_hitProbability != magic_hitProbability: self.magic_hitProbability = magic_hitProbability
	
	def calcResistYuanli( self ):
		"""
		计算元力
		"""
		resist_yuanli = calcProperty( self.resist_yuanli_base / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_yuanli_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_yuanli_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_yuanli_value / csconst.FLOAT_ZIP_PERCENT )
		if resist_yuanli > 100.0:
			resist_yuanli = 100.0
			
		if self.resist_yuanli != resist_yuanli: self.resist_yuanli = resist_yuanli
		
	def calcResistLingli( self ):
		"""
		计算灵力
		"""
		resist_lingli = calcProperty( self.resist_lingli_base / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_lingli_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_lingli_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_lingli_value / csconst.FLOAT_ZIP_PERCENT )
		if resist_lingli > 100.0:
			resist_lingli = 100.0
			
		if self.resist_lingli != resist_lingli: self.resist_lingli = resist_lingli
		
	def calcResistTipo( self ):
		"""
		计算体魄
		"""
		resist_tipo = calcProperty( self.resist_tipo_base / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_tipo_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_tipo_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_tipo_value / csconst.FLOAT_ZIP_PERCENT )
		if resist_tipo > 100.0:
			resist_tipo = 100.0
			
		if self.resist_tipo != resist_tipo: self.resist_tipo = resist_tipo

	def calcResistGiddyProbability( self ):
		"""
		计算抵抗眩晕几率
		"""
		resist_giddy_probability = calcProperty( self.resist_giddy_probability_base / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_giddy_probability_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_giddy_probability_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_giddy_probability_value / csconst.FLOAT_ZIP_PERCENT )
		if self.resist_giddy_probability != resist_giddy_probability: self.resist_giddy_probability = resist_giddy_probability

	def calcResistFixProbability( self ):
		"""
		计算抵抗定身几率
		"""
		resist_fix_probability = calcProperty( self.resist_fix_probability_base / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_fix_probability_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_fix_probability_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_fix_probability_value / csconst.FLOAT_ZIP_PERCENT )
		if self.resist_fix_probability != resist_fix_probability: self.resist_fix_probability = resist_fix_probability

	def calcResistChenmoProbability( self ):
		"""
		计算抵抗沉默几率
		"""
		resist_chenmo_probability = calcProperty( self.resist_chenmo_probability_base / csconst.FLOAT_ZIP_PERCENT, \
													self.resist_chenmo_probability_extra / csconst.FLOAT_ZIP_PERCENT, \
													self.resist_chenmo_probability_percent / csconst.FLOAT_ZIP_PERCENT, \
													self.resist_chenmo_probability_value / csconst.FLOAT_ZIP_PERCENT )
		if self.resist_chenmo_probability != resist_chenmo_probability: self.resist_chenmo_probability = resist_chenmo_probability

	def calcResistSleepProbability( self ):
		"""
		计算抵抗睡眠几率
		"""
		resist_sleep_probability = calcProperty( self.resist_sleep_probability_base / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_sleep_probability_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_sleep_probability_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_sleep_probability_value / csconst.FLOAT_ZIP_PERCENT )
		if self.resist_sleep_probability != resist_sleep_probability: self.resist_sleep_probability = resist_sleep_probability

	def calcDoubleHitMultiple( self ):
		"""
		计算物理暴击倍数
		"""
		self.double_hit_multiple = calcProperty( self.double_hit_multiple_base / csconst.FLOAT_ZIP_PERCENT, \
												self.double_hit_multiple_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.double_hit_multiple_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.double_hit_multiple_value / csconst.FLOAT_ZIP_PERCENT )

	def calcMagicDoubleHitMultiple( self ):
		"""
		计算法术暴击倍数
		"""
		self.magic_double_hit_multiple = calcProperty( self.magic_double_hit_multiple_base / csconst.FLOAT_ZIP_PERCENT, \
													self.magic_double_hit_multiple_extra / csconst.FLOAT_ZIP_PERCENT, \
													self.magic_double_hit_multiple_percent / csconst.FLOAT_ZIP_PERCENT, \
													self.magic_double_hit_multiple_value / csconst.FLOAT_ZIP_PERCENT )

	def calcResistHitDerate( self ):
		"""
		计算招架减伤
		"""
		self.resist_hit_derate = calcProperty( self.resist_hit_derate_base / csconst.FLOAT_ZIP_PERCENT, \
											self.resist_hit_derate_extra / csconst.FLOAT_ZIP_PERCENT, \
											self.resist_hit_derate_percent / csconst.FLOAT_ZIP_PERCENT, \
											self.resist_hit_derate_value / csconst.FLOAT_ZIP_PERCENT )
		if self.resist_hit_derate > 10000:
			self.resist_hit_derate = 10000

	# ----------------------------------------------------------------------------------------------------
	# 元素相关
	# ----------------------------------------------------------------------------------------------------
	def initElemProperty( self ):
		"""
		virtual method.
		初始化各种元素属性的初始值
		"""
		CombatUnitConfig.ENTITY_COMBAT_BASE_EXPRESSION[self.getClass()].initElemProperty( self )

	def calcElemHuoDamage( self ):
		"""
		计算火元素伤害
		"""
		elem_huo_damage = calcProperty( self.elem_huo_damage_base, \
									self.elem_huo_damage_extra, \
									self.elem_huo_damage_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.elem_huo_damage_value )
		if elem_huo_damage < 0:elem_huo_damage = 0
		if self.elem_huo_damage != elem_huo_damage: self.elem_huo_damage = elem_huo_damage

	def calcElemXuanDamage( self ):
		"""
		计算玄元素伤害
		"""
		elem_xuan_damage = calcProperty( self.elem_xuan_damage_base, \
									self.elem_xuan_damage_extra, \
									self.elem_xuan_damage_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.elem_xuan_damage_value )
		if elem_xuan_damage < 0:elem_xuan_damage = 0
		if self.elem_xuan_damage != elem_xuan_damage: self.elem_xuan_damage = elem_xuan_damage

	def calcElemLeiDamage( self ):
		"""
		计算雷元素伤害
		"""
		elem_lei_damage = calcProperty( self.elem_lei_damage_base, \
									self.elem_lei_damage_extra, \
									self.elem_lei_damage_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.elem_lei_damage_value )
		if elem_lei_damage < 0:elem_lei_damage = 0
		if self.elem_lei_damage != elem_lei_damage: self.elem_lei_damage = elem_lei_damage

	def calcElemBingDamage( self ):
		"""
		计算冰元素伤害
		"""
		elem_bing_damage = calcProperty( self.elem_bing_damage_base, \
									self.elem_bing_damage_extra, \
									self.elem_bing_damage_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.elem_bing_damage_value )
		if elem_bing_damage < 0:elem_bing_damage = 0
		if self.elem_bing_damage != elem_bing_damage: self.elem_bing_damage = elem_bing_damage

	def calcElemHuoDeepRatio( self ):
		"""
		火元素伤害加深率
		"""
		self.elem_huo_deep_ratio = calcProperty( self.elem_huo_deep_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_huo_deep_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_huo_deep_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_huo_deep_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT

	def calcElemXuanDeepRatio( self ):
		"""
		玄元素伤害加深率
		"""
		self.elem_xuan_deep_ratio = calcProperty( self.elem_xuan_deep_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_xuan_deep_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_xuan_deep_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_xuan_deep_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT

	def calcElemLeiDeepRatio( self ):
		"""
		雷元素伤害加深率
		"""
		self.elem_lei_deep_ratio = calcProperty( self.elem_lei_deep_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_lei_deep_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_lei_deep_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_lei_deep_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT

	def calcElemBingDeepRatio( self ):
		"""
		冰元素伤害加深率
		"""
		self.elem_bing_deep_ratio = calcProperty( self.elem_bing_deep_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_bing_deep_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_bing_deep_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_bing_deep_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT

	def calcElemHuoDerateRatio( self ):
		"""
		计算火元素抗性
		"""
		self.elem_huo_derate_ratio = max(0, min( 10000, calcProperty( self.elem_huo_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_huo_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_huo_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_huo_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT ) )

	def calcElemXuanDerateRatio( self ):
		"""
		计算玄元素抗性
		"""
		self.elem_xuan_derate_ratio = max(0, min( 10000, calcProperty( self.elem_xuan_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_xuan_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_xuan_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_xuan_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT ) )

	def calcElemLeiDerateRatio( self ):
		"""
		计算雷元素抗性
		"""
		self.elem_lei_derate_ratio = max(0, min( 10000, calcProperty( self.elem_lei_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_lei_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_lei_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_lei_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT ) )

	def calcElemBingDerateRatio( self ):
		"""
		计算冰元素抗性
		"""
		self.elem_bing_derate_ratio = max(0, min( 10000, calcProperty( self.elem_bing_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_bing_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_bing_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_bing_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT ) )

	# ---------------------------------------
	def affectPropValue( self, propName, delta, calcMethodName ) :
		"""
		defined method
		影响基础属性值（用于给附属 Entity 需要影响自身属性值时调用，譬如骑宠技能影响角色属性，宠物属性等）
		hyw--2009.08.07
		@type			propName		: str
		@param			propName		: 要硬性的属性名
		@type			delta			: INT32
		@param			delta			: 影响的属性值(这里定为 32 位，不做检测，前提是，影响的属性值不会超过 2^32 - 1)
		@type			calcMethodName  : str
		@param			calcMethodName  : 触发计算（可以为空字符串，为空串时，将不重新计算属性）
		"""
		if not hasattr( self, propName ): return
		value = getattr( self, propName )
		setattr( self, propName, value + delta )
		if calcMethodName != "" :
			getattr( self, calcMethodName )()

	# ----------------------------------------------------------------
	def setHitDelay( self ):
		"""
		重新设置攻击延迟
		"""
		hitDelay = BigWorld.time() + self.hit_speed
		if self.hitDelay != hitDelay: self.hitDelay = hitDelay

	def hitDelayOver( self ):
		"""
		判断攻击延迟是否结束

		@return: BOOL
		"""
		return BigWorld.time() >= self.hitDelay

	def updateTopSpeed( self ):
		"""
		virtual method = 0.

		更新移动速度限制(topSpeed)
		"""
		pass

	def setMoveSpeed( self, speed ):
		"""
		virtual method.
		设置移动速度
		"""
		self.move_speed = speed
		self.updateTopSpeed()

	def receiveDamage( self, casterID, skillID, damageType, damage ):
		"""
		Define and virtual method.
		接受伤害。

		@param   casterID: 施法者ID
		@type    casterID: OBJECT_ID
		@param    skillID: 技能ID
		@type     skillID: INT
		@param damageType: 伤害类型；see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: UINT8
		@param     damage: 伤害数值
		@type      damage: INT
		"""
		if self.state == csdefine.ENTITY_STATE_DEAD:
			return

		self.setHP( self.HP - damage )
		# 受到伤害时 抛出buff中断码， 所有配有在受到伤害被消除的buff都被去除
		self.clearBuff( [csdefine.BUFF_INTERRUPT_GET_HIT] )
		
		if self.HP == 0:
			self.setMP( 0 )
			self.die( casterID )
			if self.spawnMB:
				# 有spawnMB的怪物需要通知它的出生点，(可能)重新复活
				if BigWorld.entities.has_key( self.spawnMB.id ):
					BigWorld.entities[self.spawnMB.id].entityDead()
				else:
					self.spawnMB.cell.entityDead()			

	def setHP( self, value ):
		"""
		real entity method.
		virtual method
		设置HP
		"""
		if value < 0:
			value = 0
		elif value > self.HP_Max:
			value = self.HP_Max

		self.HP = value
		self.onHPChanged()

	def onHPChanged( self ):
		"""
		HP被改变回调
		"""
		pass

	def addHP( self, value ):
		"""
		real entity method.
		virtual method
		增加HP
		"""
		m_preHp = self.HP
		self.setHP( self.HP + value )
		m_addHp = self.HP - m_preHp

		return m_addHp

	def setMP( self, value ):
		"""
		real entity method.
		virtual method
		设置MP
		"""
		if value < 0:
			value = 0
		elif value > self.MP_Max:
			value = self.MP_Max

		self.MP = value
		self.onMPChanged()

	def onMPChanged( self ):
		"""
		MP被改变回调
		"""
		pass

	def addMP( self, value ):
		"""
		real entity method.
		virtual method
		增加MP
		"""
		m_preMp = self.MP
		self.setMP( self.MP + value )
		m_addMp = self.MP - m_preMp

		return m_addMp

	def full( self ):
		"""
		补满HP和MP。
		"""
		self.setHP( self.HP_Max )
		self.setMP( self.MP_Max )

	def beforeDie( self, killerID ):
		"""
		virtual method.

		死亡通报。 killer可能为空
		"""
		return True

	def onDie( self, killerID ):
		"""
		virtual method.

		死亡时回调，执行一些在死亡的那一刻必须做的事情。
		"""
		pass

	def afterDie( self, killerID ):
		"""
		virtual method.

		死亡后回掉，执行一些子类在怪物死后必须做的事情。
		"""
		return

	def die( self, killerID ):
		"""
		virtual method.

		死亡函数。
		"""
		# 死亡前的判断
		
		if self.queryTemp( "inDie", False ):
			return
		self.setTemp("inDie", True )
		
		try:
			if not self.beforeDie( killerID ):
				return
		except:
			EXCEHOOK_MSG("CombatUnit die wrong")

		try:
			self.onDie( killerID )
		except:
			EXCEHOOK_MSG("CombatUnit die wrong")

		try:
			self.clearBuff( [csdefine.BUFF_INTERRUPT_ON_DIE] )					# 清除所有buff
		except:
			EXCEHOOK_MSG("CombatUnit die wrong")

		try:
			self.changeState( csdefine.ENTITY_STATE_DEAD )
		except:
			EXCEHOOK_MSG("CombatUnit die wrong")

		try:
			killer = BigWorld.entities[ killerID ]
		except KeyError:
			if killerID != 0:
				WARNING_MSG( "killer %i not found." % killerID )
			self.afterDie( killerID )
			self.removeTemp( "inDie" )
			return

		try:
			self.resetEnemyList()
		except:
			EXCEHOOK_MSG("CombatUnit die wrong")

		try:
			if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
				if self.isEntityType( csdefine.ENTITY_TYPE_ROLE ):	# 如果死亡的是玩家
					killer.remoteCall( "statusMessage", ( csstatus.ROLE_STATE_KILL_DEAD_BY_YOU, self.getName() ) )
				else:
					killer.remoteCall( "statusMessage", ( csstatus.ACCOUNT_STATE_KILL_DEAD_TO, self.getName() ) )

			if killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				roleName = self.getName()
				if killer.onFengQi:
					roleName = ST.CHAT_CHANNEL_MASED
				if killer.isReal():
					if self.isEntityType( csdefine.ENTITY_TYPE_ROLE ):	# 如果死亡的是玩家
						killer.statusMessage( csstatus.ROLE_STATE_KILL_DEAD_BY_YOU, roleName )
					else:
						killer.statusMessage( csstatus.ACCOUNT_STATE_KILL_DEAD_TO, roleName )
				else:
					if self.isEntityType( csdefine.ENTITY_TYPE_ROLE ):	# 如果死亡的是玩家
						killer.remoteCall( "statusMessage", ( csstatus.ROLE_STATE_KILL_DEAD_BY_YOU, roleName ) )
					else:
						killer.remoteCall( "statusMessage", ( csstatus.ACCOUNT_STATE_KILL_DEAD_TO, roleName ) )

				if killer.teamMailbox is not None:
					killer.team_notifyKillMessage( self )
		except:
			EXCEHOOK_MSG("CombatUnit die wrong")

		try:
			# 死亡后做些事情
			self.afterDie( killerID )
		except:
			EXCEHOOK_MSG("CombatUnit die wrong")

		self.removeTemp( "inDie" )

	def isDead( self ):
		"""
		virtual method.

		@return: BOOL，返回自己是否已经死亡的判断
		@rtype:  BOOL
		"""
		# 虽然不一定会死亡，但接口是需要的
		return self.state == csdefine.ENTITY_STATE_DEAD

	def canFight( self ):
		"""
		virtual method.

		@return: BOOL，返回自己是否能战斗的判断
		@rtype:  BOOL
		"""
		return not self.actionSign( csdefine.ACTION_FORBID_FIGHT )

	def equipDamage( self, demageValue ):
		"""
		virtual define method.
		受击者装备磨损
		"""
		pass

	def equipAbrasion( self, demageValue ):
		"""
		virtual define method.
		攻击者装备磨损
		"""
		pass

	def onStateChanged( self, old, new ):
		"""
		virtual method
		状态改变
		"""
		State.onStateChanged( self, old, new )

	def checkViewRange( self, entity ):
		"""
		virtual method
		检测entity是否在视野范围
		判断entity是否在自己的视野范围之内
		return 	:	True	在
		return	:	False	不在
		"""
		if entity.spaceID != self.spaceID or entity.position.distTo( self.position ) > self.viewRange:
			return False
		return True

	def queryRelation( self, entity ):
		"""
		virtual method.
		取得自己与目标的关系

		@param entity: 任意目标entity
		@return : RELATION_*
		"""
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
		else:
			return csdefine.RELATION_NONE

	def queryCampRelation( self, entity ):
		"""
		取得自己与目标的阵营关系
		@param entity: 任意目标entity
		@return : RELATION_*
		"""
		# 友好阵营列表判断
		# 阵营相同，或阵营在目标的友好阵营列表,表示友好关系，否则是敌对关系
		sCamp = self.getCamp()
		tCamp = entity.getCamp()
		if ( sCamp == tCamp ) or ( sCamp in entity.friendlyCamps ) or ( tCamp in self.friendlyCamps ):
			return csdefine.RELATION_FRIEND
		else:
			return csdefine.RELATION_ANTAGONIZE

	# ----------------------------------------------------------------
	def appendReceiverMonsterExp( self, skill ):
		"""
		call on real.
		增加一个在“怪物被杀死获得经验时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springReceiveMonsterExpList.append( skill )

	def removeReceiverMonsterExp( self, skillUID ):
		"""
		call on real.
		移除一个在“怪物被杀死获得经验时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springReceiveMonsterExpList ):
			if skill.getUID() == skillUID:
				self.springReceiveMonsterExpList.pop( index )
				return

	def doAddKillMonsterExp( self, exp ):
		"""
		call on real
		在玩家获得杀怪经验时触发
		"""
		for skill in self.springReceiveMonsterExpList:
			skill.addExpTrigger( self, exp )

	def appendReceiverCure( self, skill ):
		"""
		call on real.
		增加一个在“被治疗时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springReceiverCureList.append( skill )

	def removeReceiverCure( self, skillUID ):
		"""
		call on real.
		增加一个在“被治疗时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springReceiverCureList ):
			if skill.getUID() == skillUID:
				self.springReceiverCureList.pop( index )
				return

	def doReceiverOnCure( self, caster, cureHP ):
		"""
		在被治疗时（即获得伤害后，这时人可能已经挂了）被触发，主要用于一些需要在被命中后再触发的效果；

		适用于：
		    被击中目标时$1%几率给予目标额外伤害$2
		    etc.
		@param skill:技能实例
		@type skill: SKILL
		@param caster:施法者
		@type caster: ENTITY
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		caster = BigWorld.entities.get( caster.id, None )
		if caster:
			for spell in self.springReceiverCureList:
				spell.springOnCure( caster, self, cureHP )

	def appendCasterCure( self, skill ):
		"""
		call on real.
		增加一个在“治疗目标时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springCasterCureList.append( skill )

	def removeCasterCure( self, skillUID ):
		"""
		call on real.
		增加一个在“治疗目标时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springCasterCureList ):
			if skill.getUID() == skillUID:
				self.springCasterCureList.pop( index )
				return

	def doCasterOnCure( self, receiver, cureHP ):
		"""
		在治疗目标时（即获得伤害后，这时人可能已经挂了）被触发，主要用于一些需要在命中后再触发的效果；

		适用于：
		    击中目标时$1%几率给予目标额外伤害$2
		    击中目标时$1%几率使目标攻击力降低$2，持续$3秒
		    被击中时$1几率恢复$2生命
		    被击中时$1%几率提高闪避$2，持续$3秒
		    etc.
		@param skill:技能实例
		@type skill: SKILL
		@param caster:施法者
		@type caster: ENTITY
		"""
		for spell in self.springCasterCureList:
			spell.springOnCure( self, receiver, cureHP )

	def appendVictimHit( self, skill ):
		"""
		call on real.
		增加一个在“被命中后……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springVictimHitList.append( skill )

	def removeVictimHit( self, skillUID ):
		"""
		call on real.
		增加一个在“被命中后……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springVictimHitList ):
			if skill.getUID() == skillUID:
				self.springVictimHitList.pop( index )
				return

	def doVictimOnHit( self, caster, damageType ):
		"""
		在被命中后（即获得伤害后，这时人可能已经挂了）被触发，主要用于一些需要在被命中后再触发的效果；

		适用于：
		    被击中目标时$1%几率给予目标额外伤害$2
		    etc.
		@param skill:技能实例
		@type skill: SKILL
		@param caster:施法者
		@type caster: ENTITY
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		caster = BigWorld.entities.get( caster.id, None )
		if caster:
			for spell in self.springVictimHitList:
				spell.springOnHit( caster, self, damageType )

	def appendAttackerHit( self, skill ):
		"""
		call on real.
		增加一个在“命中后……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springAttackerHitList.append( skill )

	def removeAttackerHit( self, skillUID ):
		"""
		call on real.
		增加一个在“命中后……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springAttackerHitList ):
			if skill.getUID() == skillUID:
				self.springAttackerHitList.pop( index )
				return

	def removeAttackerHitByID( self, skillID ):
		"""
		call on real.
		增加一个在“命中后……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springAttackerHitList ):
			if skill.getID() == skillID:
				self.springAttackerHitList.pop( index )
				return

	def doAttackerOnHit( self, receiver, damageType ):
		"""
		在命中后（即获得伤害后，这时人可能已经挂了）被触发，主要用于一些需要在命中后再触发的效果；

		适用于：
		    击中目标时$1%几率给予目标额外伤害$2
		    击中目标时$1%几率使目标攻击力降低$2，持续$3秒
		    被击中时$1几率恢复$2生命
		    被击中时$1%几率提高闪避$2，持续$3秒
		    etc.
		@param skill:技能实例
		@type skill: SKILL
		@param caster:施法者
		@type caster: ENTITY
		"""
		for spell in self.springAttackerHitList:
			spell.springOnHit( self, receiver, damageType )

	def onAttackerMiss( self, receiver, damageType ):
		"""
		攻击者未命中
		"""
		pass

	def appendVictimDodge( self, skill ):
		"""
		call on real.
		增加一个在“闪避成功时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springVictimDodgeList.append( skill )

	def removeVictimDodge( self, skillUID ):
		"""
		call on real.
		增加一个在“闪避成功时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springVictimDodgeList ):
			if skill.getUID() == skillUID:
				self.springVictimDodgeList.pop( index )
				return

	def doVictimOnDodge( self, caster, damageType ):
		"""
		在闪避成功时（即获得伤害后，这时人可能已经挂了）被触发
		@param skill:技能实例
		@type skill: SKILL
		@param caster:施法者
		@type caster: ENTITY
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		caster = BigWorld.entities.get( caster.id, None )
		if caster:
			for spell in self.springVictimDodgeList:
				spell.springOnDodge( caster, self, damageType )

	def appendAttackerDodge( self, skill ):
		"""
		call on real.
		增加一个在“目标闪避成功时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springAttackerDodgeList.append( skill )

	def removeAttackerDodge( self, skillUID ):
		"""
		call on real.
		增加一个在“目标闪避成功时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springAttackerDodgeList ):
			if skill.getUID() == skillUID:
				self.springAttackerDodgeList.pop( index )
				return

	def doAttackerOnDodge( self, receiver, damageType ):
		"""
		在目标闪避成功时（即获得伤害后，这时人可能已经挂了）被触发
		@param skill:技能实例
		@type skill: SKILL
		@param caster:施法者
		@type caster: ENTITY
		"""
		for spell in self.springAttackerDodgeList:
			spell.springOnDodge( self, receiver, damageType )

	def appendVictimDoubleHit( self, skill ):
		"""
		call on real.
		增加一个在“被物理暴击时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springVictimDoubleHitList.append( skill )

	def removeVictimDoubleHit( self, skillUID ):
		"""
		call on real.
		增加一个在“被物理暴击时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springVictimDoubleHitList ):
			if skill.getUID() == skillUID:
				self.springVictimDoubleHitList.pop( index )
				return

	def doVictimOnDoubleHit( self, caster, damageType ):
		"""
		在被物理暴击时（即获得伤害后，这时人可能已经挂了）被触发
		@param skill:技能实例
		@type skill: SKILL
		@param caster:施法者
		@type caster: ENTITY
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		caster = BigWorld.entities.get( caster.id, None )
		if caster:
			for spell in self.springVictimDoubleHitList:
				spell.springOnDoubleHit( caster, self, damageType )

	def appendAttackerDoubleHit( self, skill ):
		"""
		call on real.
		增加一个在“产生物理暴击时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springAttackerDoubleHitList.append( skill )

	def removeAttackerDoubleHit( self, skillUID ):
		"""
		call on real.
		增加一个在“产生物理暴击时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springAttackerDoubleHitList ):
			if skill.getUID() == skillUID:
				self.springAttackerDoubleHitList.pop( index )
				return

	def doAttackerOnDoubleHit( self, receiver, damageType ):
		"""
		在产生物理暴击时（即获得伤害后，这时人可能已经挂了）被触发
		@param skill:技能实例
		@type skill: SKILL
		@param caster:施法者
		@type caster: ENTITY
		"""
		for spell in self.springAttackerDoubleHitList:
			spell.springOnDoubleHit( self, receiver, damageType )

	def appendVictimResistHit( self, skill ):
		"""
		call on real.
		增加一个在“招架成功时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springVictimResistHitList.append( skill )

	def removeVictimResistHit( self, skillUID ):
		"""
		call on real.
		增加一个在“招架成功时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springVictimResistHitList ):
			if skill.getUID() == skillUID:
				self.springVictimResistHitList.pop( index )
				return

	def doVictimOnResistHit( self, caster, damageType ):
		"""
		在招架成功时（即获得伤害后，这时人可能已经挂了）被触发
		@param skill:技能实例
		@type skill: SKILL
		@param caster:施法者
		@type caster: ENTITY
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		caster = BigWorld.entities.get( caster.id, None )
		if caster:
			for spell in self.springVictimResistHitList:
				spell.springOnResistHit( caster, self, damageType )

	def appendAttackerResistHit( self, skill ):
		"""
		call on real.
		增加一个在“目标招架成功时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springAttackerResistHitList.append( skill )

	def removeAttackerResistHit( self, skillUID ):
		"""
		call on real.
		增加一个在“目标招架成功时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springAttackerResistHitList ):
			if skill.getUID() == skillUID:
				self.springAttackerResistHitList.pop( index )
				return

	def doAttackerOnResistHit( self, receiver, damageType ):
		"""
		在目标招架成功时（即获得伤害后，这时人可能已经挂了）被触发
		@param skill:技能实例
		@type skill: SKILL
		@param caster:施法者
		@type caster: ENTITY
		"""
		for spell in self.springAttackerResistHitList:
			spell.springOnResistHit( self, receiver, damageType )

	def appendVictimBeforeDamage( self, skill ):
		"""
		call on real.
		增加一个在“在伤害计算前……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springVictimBeforeDamageList.append( skill )

	def removeVictimBeforeDamage( self, skillUID ):
		"""
		call on real.
		增加一个在“在伤害计算前……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springVictimBeforeDamageList ):
			if skill.getUID() == skillUID:
				self.springVictimBeforeDamageList.pop( index )
				return

	def appendAttackerAfterDamage( self, skill ):
		"""
		call on real.
		增加一个在“在伤害计算后……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springAttackerAfterDamageList.append( skill )

	def removeAttackerAfterDamage( self, skillUID ):
		"""
		call on real.
		增加一个在“在伤害计算后……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springAttackerAfterDamageList ):
			if skill.getUID() == skillUID:
				self.springAttackerAfterDamageList.pop( index )
				return

	def doAttackerAfterDamage( self, skill, receiver, damage ):
		"""
		在伤害计算后（即获得伤害后，这时人可能已经挂了）被触发，主要用于一些需要在受到伤害以后再触发的效果；

		适用于：
		    击中目标时$1%几率给予目标额外伤害$2
		    击中目标时$1%几率使目标攻击力降低$2，持续$3秒
		    被击中时$1几率恢复$2生命
		    被击中时$1%几率提高闪避$2，持续$3秒
		    etc.
		@param skill:技能实例
		@type skill: SKILL
		@param receiver:受术者( 不一定是一个real entity )
		@type receiver: ENTITY
		"""
		for spell in self.springAttackerAfterDamageList:
			spell.springOnDamage( self, receiver, skill, damage )

	def appendVictimAfterDamage( self, skill ):
		"""
		call on real.
		增加一个在“在伤害计算后……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springVictimAfterDamageList.append( skill )

	def removeVictimAfterDamage( self, skillUID ):
		"""
		call on real.
		增加一个在“在伤害计算后……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springVictimAfterDamageList ):
			if skill.getUID() == skillUID:
				self.springVictimAfterDamageList.pop( index )
				return

	def doVictimOnDamage( self, skill, caster, damage ):
		"""
		在伤害计算后（即获得伤害后，这时人可能已经挂了）被触发，主要用于一些需要在受到伤害以后再触发的效果；

		适用于：
		    击中目标时$1%几率给予目标额外伤害$2
		    击中目标时$1%几率使目标攻击力降低$2，持续$3秒
		    被击中时$1几率恢复$2生命
		    被击中时$1%几率提高闪避$2，持续$3秒
		    etc.
		@param skill:技能实例
		@type skill: SKILL
		@param caster:施法者
		@type caster: ENTITY
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		caster = BigWorld.entities.get( caster.id, None )
		if caster:
			caster.setTemp( "lastDPS", damage )
			for spell in self.springVictimAfterDamageList:
				spell.springOnDamage( caster, self, skill, damage )

	def appendImmunityBuff( self, skill ):
		"""
		call on real.
		增加一个免疫性BUFF
		由于需要免疫的类型非常的多非常的不确定因此使用该处理方式
		@param skill:技能实例
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springImmunityBuffList.append( skill )

	def removeImmunityBuff( self, skillUID ):
		"""
		call on real.
		删除免疫性BUFF
		由于需要免疫的类型非常的多非常的不确定因此使用该处理方式
		@param skill:技能实例
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springImmunityBuffList ):
			if skill.getUID() == skillUID:
				self.springImmunityBuffList.pop( index )
				return

	def doImmunityBuff( self, caster, buffData ):
		"""
		执行所有免疫性BUFF
		由于需要免疫的类型非常的多非常的不确定因此使用该处理方式
		此接口需要保证receiver是real
		@param skill:技能实例
		@type skill: SKILL
		@param caster:施法者
		@type caster: ENTITY
		"""
		for spell in self.springImmunityBuffList:
			state = spell.springOnImmunityBuff( caster, self, buffData )
			if state != csstatus.SKILL_GO_ON:
				return state
		return csstatus.SKILL_GO_ON

	def appendOnUseSkill( self, skill ):
		"""
		call on real.
		增加一个在“使用技能时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springOnUseSkillList.append( skill )

	def removeOnUseSkill( self, skillUID ):
		"""
		call on real.
		增加一个在“使用技能时……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springOnUseSkillList ):
			if skill.getUID() == skillUID:
				self.springOnUseSkillList.pop( index )
				return

	def doOnUseSkill( self, skill ):
		"""
		在使用技能时被触发 可以解决一些 如降低增加吟唱时间 减少或增加施法消耗等
		@param skill:技能实例
		@type skill: SKILL
		@param caster:施法者
		@type caster: ENTITY
		"""
		for spell in self.springOnUseSkillList:
			spell.springOnUseSkill( self, skill )

	def appendOnUseMaligSkill( self, skill ):
		"""
		call on real.
		增加一个在“进入战斗状态后……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springOnUseMaligSkill.append( skill )

	def removeOnUseMaligSkill( self, skillUID ):
		"""
		call on real.
		增加一个在“进入战斗状态后……”触发的普通技能或BUFF
		@param skill:技能实例
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springOnUseMaligSkill ):
			if skill.getUID() == skillUID:
				self.springOnUseMaligSkill.pop( index )
				return

	def doOnUseMaligSkill( self, skill ):
		"""
		在使用恶性技能后触发
		"""
		for spell in self.springOnUseMaligSkill:
			spell.springOnUseMaligSkill( self, skill )

	def appendShield( self, skill ):
		"""
		call on real.
		增加一个护盾

		@param shieldDict: 护盾类型数据实例, definition in alias.xml
		@type  shieldDict: SHIELD
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.shields.append( skill )

	def removeShield( self, skillUID ):
		"""
		删除一个护盾

		@param skillID: 与之关联的技能ID
		@type  skillID: SKILLID
		"""
		for index, skill in enumerate( self.shields ):
			if skill.getUID() == skillUID:
				self.shields.pop( index )
				return

	def getShieldsByType( self, dmgType ):
		"""
		获取玩家身上吸收某种伤害类型的护盾

		@param dmgType: 伤害类型; SkillDefine::DAMAGE_TYPE_*
		@type  dmgType: INT
		@return: 被找到的匹配的护盾列表；format: [ (index,SHIELD type data), ... ]
		"""
		a = []
		for i, buff in enumerate( self.shields ):
			if buff["skill"].getShieldType() == dmgType:
				a.append( i )
		return a

	def shieldConsume( self, index, dmgType, damage ):
		"""
		护盾的消耗处理  注意: 它是一个本地接口 在本地会正常执行而且正确的返回一个值后会转到real cell上执行真正的实例
		操作，最后达到2个cell上的该护盾一致。
		@param index:护盾所在的索引
		@param damageType: 伤害类型
		@param damage : 本次伤害值
		@return: 返回处理后的伤害值
		"""
		try:
			shield = self.shields[index]
		except IndexError:
			# 可能某个护盾因为持续时间到了而删除了 破坏了此次循环, 因此直接返回
			WARNING_MSG( "can not find the shield (%i)" % index )
			return damage
		# 这里处理护盾真正的吸收
		nDamage = shield.doShield( self, dmgType, damage )
		if not self.isReal():
			self.remoteCall( "shieldConsume", ( index, dmgType, damage ) )
		else:
			self.shields[index] = self.shields[index]	# 这样才能够导致数据向其他ghostcell上广播自身实例与其同步
			#这里不能做护盾的消耗删除操作 详细参见filtrateMarShields接口说明
		return nDamage

	def filtrateMarShields( self ):
		"""
		define method.
		过滤损坏的护盾
		之所以放在这里做 是因为在shieldConsume接口中删除会破坏数组循环导致不可预料的错误
		而且因为BUFF有持续时间结束会删除自己也会导致数组循环过程中移位而跳过本该判断的护盾,所以在这里重新过滤一次才能保证安全
		"""
		m = []
		for shield in self.shields:
			if shield.isDisabled( self ):
				m.append( shield )

		m.reverse()
		for shield in m:
			rmb = []
			for idx in self.findBuffsByBuffID( shield.getBuffID() ):
				if self.getBuff( idx )["skill"].isDisabled( self ):
					rmb.append( idx )
			rmb.reverse()	# 从后面往前删除
			for r in rmb:
				self.removeBuff( r, [csdefine.BUFF_INTERRUPT_NONE] )

	def calcShieldSuck( self, receiver, damage, damageType ):
		"""
		virtual method.
		计算被攻击方护盾对伤害的吸收 因为这个流程之后其他功能会参考此次的消减后的最终伤害所以此接口不能放到receiveDamage中
		公式：最终伤害=伤害 – 当前剩余护盾值
		最终伤害下限为0。
		然后，再对护盾进行削弱，剩余护盾值=当前剩余护盾值 – 最终伤害
		剩余护盾值下限为0。
		注：护盾有三种类型，物理型护盾仅能吸收物理伤害，法术型护盾仅能吸收法术伤害，无类型护盾可吸收任何伤害。
		当一次攻击过程中包含物理及法术伤害时，将分别根据类型进行吸收。
		当被攻击方存在多个护盾效果时，先根据类型吸收，多个同类型护盾以剩余存在时间短的先吸收，当无类型护盾与其他两种并存时，则无类型护盾在物理/法术型护盾之后作用。

		@param target: 被攻击方
		@type  target: entity
		@param  damage: 经过招架判断后的伤害
		@type   damage: INT
		@return: INT32
		"""
		#之所以护盾计算放在caster里是因为 攻击流程中caster是real，receiver.shields是被定义过的
		#因此在caster本地也是可以这么计算的，错误几率比较小。
		if len( receiver.shields ) > 0:
			for index, shield in enumerate( receiver.shields ):
				damage = receiver.shieldConsume( index, damageType, damage )
				if damage <= 0:
					break
			receiver.filtrateMarShields()
		return damage

	def calcDamageScissor( self, receiver, damage ):
		"""
		virtual method.
		计算被攻击方物理伤害削减
		伤害=物理伤害x (1 – 被攻击方物理伤害减免率)
		– 被攻击方物理伤害减免值
		伤害下限为0。
		注：伤害为DOT型持续伤害则对其伤害总值削减后再分次作用。
		其中，物理伤害减免率及物理伤害减免值参考公式文档，公式如下：
		角色基础物理伤害减免点数（总公式中的基础值）=0
		角色基础物理伤害减免值（总公式中的基础值）=0
		@param target: 被攻击方
		@type  target: entity
		@param  damage: 经过招架判断后的伤害
		@type   damage: INT
		@return: INT32
		"""
		damage = damage * ( 1 - receiver.damage_derate_ratio / csconst.FLOAT_ZIP_PERCENT ) - receiver.damage_derate
		if damage < 0:
			damage = 0
		return damage

	def calcMagicDamageScissor( self, receiver, damage ):
		"""
		virtual method.
		计算被攻击方物理伤害削减
		伤害=物理伤害x (1 – 被攻击方物理伤害减免率)
		– 被攻击方物理伤害减免值
		伤害下限为0。
		注：伤害为DOT型持续伤害则对其伤害总值削减后再分次作用。
		其中，物理伤害减免率及物理伤害减免值参考公式文档，公式如下：
		角色基础物理伤害减免点数（总公式中的基础值）=0
		角色基础物理伤害减免值（总公式中的基础值）=0
		@param target: 被攻击方
		@type  target: entity
		@param  damage: 经过招架判断后的伤害
		@type   damage: INT
		@return: INT32
		"""
		damage = damage * ( 1 - receiver.magic_damage_derate_ratio / csconst.FLOAT_ZIP_PERCENT ) - receiver.magic_damage_derate
		if damage < 0:
			damage = 0
		return damage

	def reboundDamage_Phy( self, caster, skillID, damage, rebound_damage_extra, rebound_damage_percent ):
		"""
		物理伤害反弹处理流程
		@param casterID: 攻击者ID
		@param damage: 攻击者造成的伤害数值
		"""
		# 开始伤害反弹计算
		rebound_damage = rebound_damage_extra
		rebound_damage += int( damage * rebound_damage_percent )
		rebound_damage = int( self.calcDamageScissor( caster, rebound_damage ) )
		rebound_damage = int( self.calcShieldSuck( caster, rebound_damage, csdefine.DAMAGE_TYPE_PHYSICS ) )
		if rebound_damage <= 0:
			return

		caster.receiveSpell( self.id, skillID, csdefine.DAMAGE_TYPE_PHYSICS|csdefine.DAMAGE_TYPE_REBOUND, rebound_damage, 0 )
		caster.receiveDamage( self.id, skillID, csdefine.DAMAGE_TYPE_PHYSICS|csdefine.DAMAGE_TYPE_REBOUND, rebound_damage )

	def reboundDamage_Magic( self, caster, skillID, damage, rebound_magic_damage_extra, rebound_magic_damage_percent ):
		"""
		法术伤害反弹处理流程
		@param casterID: 攻击者ID
		@param damage: 攻击者造成的伤害数值
		"""
		# 开始伤害反弹计算
		rebound_damage = rebound_magic_damage_extra
		rebound_damage += int( damage * rebound_magic_damage_percent )
		rebound_damage = int( self.calcMagicDamageScissor( caster, rebound_damage ) )
		rebound_damage = int( self.calcShieldSuck( caster, rebound_damage, csdefine.DAMAGE_TYPE_MAGIC ) )
		if rebound_damage <= 0:
			return

		caster.receiveSpell( self.id, skillID, csdefine.DAMAGE_TYPE_MAGIC|csdefine.DAMAGE_TYPE_REBOUND, rebound_damage, 0 )
		caster.receiveDamage( self.id, skillID, csdefine.DAMAGE_TYPE_MAGIC|csdefine.DAMAGE_TYPE_REBOUND, rebound_damage )


	def reboundDamage( self, casterID, skillID, damage, damageType ):
		"""
		伤害反弹处理流程
		@param damage: 攻击者造成的伤害数值
		"""
		if damageType & csdefine.DAMAGE_TYPE_REBOUND == csdefine.DAMAGE_TYPE_REBOUND:
			return

		try:
			caster = BigWorld.entities[ casterID ]
		except:
			WARNING_MSG( "not find the entityID %d" % casterID )
			return

		if damageType & ( csdefine.DAMAGE_TYPE_PHYSICS_NORMAL | csdefine.DAMAGE_TYPE_PHYSICS ):
			reboud_probability = self.queryTemp( "rebound_damage_probability", 0.0 )
			if reboud_probability > 0 and reboud_probability > random.random():
				rebound_damage_extra = self.queryTemp( "rebound_damage_extra", 0 )
				rebound_damage_percent = self.queryTemp( "rebound_damage_percent", 0.0 )
				if rebound_damage_extra > 0 or rebound_damage_percent > 0.0:
					self.reboundDamage_Phy( caster, skillID, damage, rebound_damage_extra, rebound_damage_percent )
		if damageType & csdefine.DAMAGE_TYPE_MAGIC:
			reboud_probability = self.queryTemp( "rebound_magic_damage_probability", 0.0 )
			if reboud_probability > 0 and reboud_probability > random.random():
				rebound_damage_extra = self.queryTemp( "rebound_magic_damage_extra", 0 )
				rebound_damage_percent = self.queryTemp( "rebound_magic_damage_percent", 0.0 )
				if rebound_damage_extra > 0 or rebound_damage_percent > 0.0:
					self.reboundDamage_Magic( caster, skillID, damage, rebound_damage_extra, rebound_damage_percent )

	# ----------------------------------------------------------------------------------------------------
	# race, class, gender, faction
	# ----------------------------------------------------------------------------------------------------
	def isRaceclass( self, rc, mask = csdefine.RCMASK_ALL):
		"""
		是否为指定种族职业。
		@return: bool
		"""
		return self.raceclass & mask == rc

	def getGender( self ):
		"""
		取得自身性别
		@return: INT
		"""
		return self.raceclass & csdefine.RCMASK_GENDER

	def getRace( self ):
		"""
		取得自身种族
		@return: INT
		"""
		return self.raceclass & csdefine.RCMASK_RACE

	def getFaction( self ):
		"""
		取得自身所属的势力
		@return: INT
		"""
		return ( self.raceclass & csdefine.RCMASK_FACTION ) >> 12

	def getCamp( self ):
		"""
		取得自身阵营
		@return: INT
		"""
		return ( self.raceclass & csdefine.RCMASK_CAMP ) >> 20
		
	def getLevel( self ):
		"""
		获得自身级别
		"""
		return self.level
	
	def getDaoheng( self ):
		# 获取自身道行值
		return self.daoheng
	
	def addDaoheng( self, addValue, reason = 0 ):
		# 添加自身道行值
		self.daoheng += addValue
	
	def setDaoheng( self, dxValue, reason = 0 ):
		# 设置自身道行值
		self.daoheng = dxValue

	def isRealLook( self, entityID ):
		"""
		Define Method
		是否侦测到目标
		"""
		target = BigWorld.entities.get( entityID )
		if target is None: return True
		
		if target.isEntityType( csdefine.ENTITY_TYPE_PET ): #如果是宠物，判断其主人的侦测情况 add by wxuo 2012-6-8
			owner = target.getOwner()
			target = owner.entity
		# 没有在潜行，目标肯定能侦测到
		if target.effect_state & csdefine.EFFECT_STATE_PROWL == 0: return True
		difLevel = ( target.level - self.level )*5 + target.sneakLevelAmend - self.realLookLevelAmend
		if difLevel > 25:
			odds = 0.0
		elif difLevel < -25:
			odds = 1.0
		else:
			odds = ( 1 - ( difLevel + 25 )/50.0 ) ** 2 + ( self.realLookAmend - target.lessRealLookAmend )/csconst.FLOAT_ZIP_PERCENT
		if random.random() <= odds:
			return True
		return False


	def addEnemyCheck( self, entityID ):
		"""
		"""
		if not EntityRelationTable.addEnemyCheck( self, entityID ):
			return False

		if self.getState() == csdefine.ENTITY_STATE_DEAD:
			return False
		
		entity = BigWorld.entities.get( entityID, None )
		if not entity:
			return False
			
		if self.queryRelation( entity ) != csdefine.RELATION_ANTAGONIZE:
			return False

		return True

	def moveToPosFC( self, endDstPos, targetMoveSpeed, targetMoveFace ):
		"""
		连击移动
		"""
		pass
		
	def getCombatCamp( self ):
		"""
		获取战斗阵营
		"""
		return self.combatCamp
		
	def getIsUseCombatCamp( self ):
		"""
		获取是否使用战斗阵营
		"""
		return self.isUseCombatCamp
	
	def addCombatRelationIns( self, type, id ):
		inst = RelationDynamicObjImpl.createRelationObjSpecial( type, id )
		self.relationInsList.append( inst )
		pass
		
	def queryCombatRelationIns( self, type, id ):
		relationIns = None
		for inst in self.relationInsList:
			if inst.getID() == id and inst.getType() == type:
				relationIns = inst
				return relationIns
		return relationIns
		
	def removeCombatRelationIns( self, type, id ):
		removeInst = self.queryCombatRelationIns( type, id )
		if removeInst:
			self.relationInsList.remove( removeInst )
				
	def changeRelationMode( self, type ):
		if type in csconst.RELATION_TYPE_STATIC_SPACE or type == csdefine.RELATION_STATIC_CAMP:
			self.relationMode = type
		
	def queryCombatRelation( self, entity ):
		"""
		查询战斗关系接口
		"""
		relation = 0
		ownRelationInsList = self.getRelationInsList()
		if ownRelationInsList:
			for inst in ownRelationInsList:
				relation = inst.queryCombatRelation( entity )
				if relation != csdefine.RELATION_NONE:
					return relation
					
		entityRelationInsList = entity.getRelationInsList()
		if entityRelationInsList:
			for inst in entityRelationInsList:
				relation = inst.queryCombatRelation( self )
				if relation != csdefine.RELATION_NONE:
					return relation
					
		type = self.getRelationMode()
		relationIns = g_relationStaticMgr.getRelationInsFromType( type )
		relation = relationIns.queryCombatRelation( self, entity )
		if relation != csdefine.RELATION_NONE:
			return relation
		
		return csdefine.RELATION_NEUTRALLY
	
	def getRelationMode( self ):
		"""
		获取战斗关系模式
		"""
		return self.relationMode
	
	def getRelationEntity( self ):
		"""
		获取真实比较的entity实体
		"""
		return self
		
	def getRelationInsList( self ):
		"""
		获取自身的relationInsList，也就是关系实例列表
		"""
		return self.relationInsList
	
	def isNeedQueryRelation( self, entity ):
		"""
		是否需要查询两者之间的关系，如果已经销毁或者不是CombatUnit对象，
		就不需要往下查询了
		"""
		if self.isDestroyed and entity.isDestroyed:
			return False
		elif not isinstance( entity, CombatUnit ):
			return False
		else:
			return True
	
# CombatUnit.py
