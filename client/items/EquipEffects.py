# -*- coding: gb18030 -*-

# $Id: EquipEffects.py,v 1.9 2008-05-13 00:57:19 zhangyuxing Exp $

import math
import skills
from bwdebug import *
from config.client.labels.items import lbs_EquipEffects


# 格式化器
_iFormatter = lambda name, value : "%s + %i" % ( name, math.ceil( value ) )
_iListFormatter = lambda name, value : [name, "+%i" % math.ceil( value )]
_iFormatter2 = lambda name, value : "%s + %i%%" % ( name, math.ceil( value ) )
_iListFormatter2 = lambda name, value : [name, "+%i%%" % math.ceil( value )]
_fFormatter = lambda name, value : "%s + %0.1f%%" % ( name, value * 100 )
_fListFormatter = lambda name, value : [name, "+%0.1f%%" % ( value * 100 ) ]
_fFormatter2 = lambda name, value : "%s + %0.2f" % ( name, value / 100.0 )	# 元素抗性用
_fListFormatter2 = lambda name, value : [name, "+%0.2f" % ( value / 100.0 ) ]	# 元素抗性用
_fFormatter3 = lambda name, value : "%s + %0.2f%%" % ( name, value / 100.0 )	# 元素用
_fListFormatter3 = lambda name, value : [name, "+%0.2f%%" % ( value / 100.0 ) ]	# 元素用

# -----------------------------------------------
# 体质加值
# -----------------------------------------------
class AddValueCorporeity:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[1], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[1], param )

class AddPercentCorporeity:
	@staticmethod
	def description( param ):
		return _iFormatter2( lbs_EquipEffects[1], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter2( lbs_EquipEffects[1], param )

# -----------------------------------------------
# 智力加值
# -----------------------------------------------
class AddValueIntellect:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[2], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[2], param )

class AddPercentIntellect:
	@staticmethod
	def description( param ):
		return _iFormatter2( lbs_EquipEffects[2], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter2( lbs_EquipEffects[2], param )

# -----------------------------------------------
# 力量加值
# -----------------------------------------------
class AddValueStrength:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[3], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[3], param )

class AddPercentStrength:
	@staticmethod
	def description( param ):
		return _iFormatter2( lbs_EquipEffects[3], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter2( lbs_EquipEffects[3], param )

# -----------------------------------------------
# 敏捷加值
# -----------------------------------------------
class AddValueDexterity:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[4], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[4], param )

class AddPercentDexterity:
	@staticmethod
	def description( param ):
		return _iFormatter2( lbs_EquipEffects[4], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter2( lbs_EquipEffects[4], param )

# -----------------------------------------------
# 生命加值
# -----------------------------------------------
class AddValueHP:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[5], param)

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[5], param )

class AddPercentHP:
	@staticmethod
	def description( param ):
		return _iFormatter2( lbs_EquipEffects[5], param)

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter2( lbs_EquipEffects[5], param )

# -----------------------------------------------
# 法力加值
# -----------------------------------------------
class AddValueMP:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[6], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[6], param )

class AddPercentMP:
	@staticmethod
	def description( param ):
		return _iFormatter2( lbs_EquipEffects[6], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter2( lbs_EquipEffects[6], param )

# -----------------------------------------------
# 物理防御加值
# -----------------------------------------------
class AddValueArmor:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[7], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[7], param )

class AddPercentArmor:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[7], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[7], param )

# -----------------------------------------------
# 法术防御加值
# -----------------------------------------------
class AddValueMagicArmor:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[8], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[8], param )

class AddPercentMagicArmor:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[8], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[8], param )

# -----------------------------------------------
# 角色物理攻击力
# -----------------------------------------------
class AddValueDamage:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[9], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[9], param )

class AddPercentDamage:
	@staticmethod
	def description( param ):
		return _iFormatter2( lbs_EquipEffects[9], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter2( lbs_EquipEffects[9], param )

# -----------------------------------------------
# 角色法术攻击力
# -----------------------------------------------
class AddValueMagicDamage:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[10], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[10], param )

class AddPercentMagicDamage:
	@staticmethod
	def description( param ):
		return _iFormatter2( lbs_EquipEffects[10], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter2( lbs_EquipEffects[10], param )

# -----------------------------------------------
# 物理攻击力
# -----------------------------------------------
class AddValueSkillExtra:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[9], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[9], param )

# -----------------------------------------------
# 法术攻击力
# -----------------------------------------------
class AddValueMagicSkillExtra:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[10], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[10], param )

# -----------------------------------------------
# 生命恢复速度
# -----------------------------------------------
class AddValueHPRegen:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[11], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[11], param )

# -----------------------------------------------
# 法力恢复速度
# -----------------------------------------------
class AddValueMPRegen:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[12], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[12], param )

# -----------------------------------------------
# 最小攻击力
# -----------------------------------------------
class AddValueDamageMin:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[13], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[13], param )

# -----------------------------------------------
# 最大攻击力
# -----------------------------------------------
class AddValueDamageMax:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[14], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[14], param )

# -----------------------------------------------
# 物理命中点数
# -----------------------------------------------
class AddValueHit:

	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[15], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[15], param )


# -----------------------------------------------
# 法术命中点数
# -----------------------------------------------
class AddValueMagicHit:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[16], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[16], param )

# -----------------------------------------------
# 闪避点数
# -----------------------------------------------
class AddValueDodge:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[17], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[17], param )

# -----------------------------------------------
# 物理暴击点数
# -----------------------------------------------
class AddValueDoubleHit:

	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[18], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[18], param )

# -----------------------------------------------
# 法术暴击点数
# -----------------------------------------------
class AddValueMagicDoubleHit:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[19], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[19], param )

# -----------------------------------------------
# 招架点数
# -----------------------------------------------
class AddValueResistHit:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[20], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[20], param )

# -----------------------------------------------
# 招架减伤点数
# -----------------------------------------------
class AddValueResistHitDerate:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[21], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[21], param )

# -----------------------------------------------
# 物理伤害减免
# -----------------------------------------------
class AddValueDamageDerate:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[22], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[22], param )

# -----------------------------------------------
# 法术伤害减免
# -----------------------------------------------
class AddValueMagicDamageDerate:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[23], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[23], param )


# -----------------------------------------------
# 伤害减免
# -----------------------------------------------
class AddValueAllDerate:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[24], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[24], param )

# -----------------------------------------------
# 特效触发点数
# -----------------------------------------------
class AddValueSpeciallySpring:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[25], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[25], param )

# -----------------------------------------------
# 物理暴击伤害倍数
# -----------------------------------------------
class AddValueDoubleHitMultiple:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[26], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[26], param )

# -----------------------------------------------
# 法术暴击伤害倍数
# -----------------------------------------------
class AddValueMagicDoubleHitMultiple:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[27], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[27], param )

# -----------------------------------------------
# 降低对方物理命中点数
# -----------------------------------------------
class AddValueReduceTargetHit:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[28], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[28], param )

# -----------------------------------------------
#降低对方法术命中点数
# -----------------------------------------------
class AddValueReduceTargetMagicHit:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[29], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[29], param )

# -----------------------------------------------
# 抵抗沉默点数
# -----------------------------------------------
class AddValueResistChenmo:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[30], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[30], param )

# -----------------------------------------------
# 抵抗眩晕
# -----------------------------------------------
class AddValueResistGiddy:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[31], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[31], param )

# -----------------------------------------------
# 抵抗定身
# -----------------------------------------------
class AddValueResistFix:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[32], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[32], param )

# -----------------------------------------------
# 抵抗睡眠
# -----------------------------------------------
class AddValueResistSleep:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[33], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[33], param )

# -----------------------------------------------
# 抵抗沉默几率
# -----------------------------------------------
class AddValueResistChenmoOdds:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[34], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[34], param )

# -----------------------------------------------
# 抵抗眩晕几率
# -----------------------------------------------
class AddValueResistGiddyOdds:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[35], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[35], param )

# -----------------------------------------------
# 抵抗定身几率
# -----------------------------------------------
class AddValueResistFixOdds:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[36], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[36], param )

# -----------------------------------------------
# 抵抗睡眠几率
# -----------------------------------------------
class AddValueResistSleepOdds:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[37], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[37], param )

# -----------------------------------------------
# 攻击速度
# -----------------------------------------------
class AddValueHitSpeed:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[38], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[39], param )

# -----------------------------------------------
# 移动速度
# -----------------------------------------------
class AddValueMoveSpeed:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[39], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[39], param )

# -----------------------------------------------
# 攻击距离
# -----------------------------------------------
class AddValueRange:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[40], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[40], param )

# -----------------------------------------------
# 特效触发率
# -----------------------------------------------
class AddValueSpeciallySpringPro:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[41], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[41], param )

# -----------------------------------------------
# 物理暴击率
# -----------------------------------------------
class AddValueDoubleHitPro:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[42], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[42], param )

# -----------------------------------------------
# 法术暴击率
# -----------------------------------------------
class AddValueMagicDoubleHitPro:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[43], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[43], param )

# -----------------------------------------------
# 物理被暴击率减免
# -----------------------------------------------
class AddValueBeDoubleHitProReduce:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[115], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[115], param )

# -----------------------------------------------
# 法术被暴击率减免
# -----------------------------------------------
class AddValueMagicBeDoubleHitProReduce:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[116], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[116], param )

# -----------------------------------------------
# 物理命中率
# -----------------------------------------------
class AddValueHitPro:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[44], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[44], param )

# -----------------------------------------------
# 法术命中率
# -----------------------------------------------
class AddValueMagicHitPro:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[45], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[45], param )

# -----------------------------------------------
# 武器攻击力
# -----------------------------------------------
class AddValueWeaponDamage:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[46], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[46], param )

# -----------------------------------------------
# 体质加成
# -----------------------------------------------
class AddPercentCorporeity:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[47], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[47], param )

# -----------------------------------------------
# 智力加成
# -----------------------------------------------
class AddPercentIntellect:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[48], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[48], param )

# -----------------------------------------------
# 力量加成
# -----------------------------------------------
class AddPercentStrength:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[49], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[49], param )

# -----------------------------------------------
# 敏捷加成
# -----------------------------------------------
class AddPercentDexterity:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[50], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[50], param )

# -----------------------------------------------
# 生命加成
# -----------------------------------------------
class AddPercentHP:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[51], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[51], param )

# -----------------------------------------------
# 法力加成
# -----------------------------------------------
class AddPercentMP:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[52], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[52], param )

# -----------------------------------------------
# 物理防御加成
# -----------------------------------------------
class AddPercentArmor:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[53], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[53], param )

# -----------------------------------------------
# 法术防御加成
# -----------------------------------------------
class AddPercentMagicArmor:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[54], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[54], param )

# -----------------------------------------------
# 武器攻击力加成
# -----------------------------------------------
class AddPercentWeaponDamage:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[55], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[55], param )

# -----------------------------------------------
# 角色物理攻击力加成
# -----------------------------------------------
class AddPercentDamage:

	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[56], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[56], param )

# -----------------------------------------------
# 角色法术攻击力加成
# -----------------------------------------------
class AddPercentMagicDamage:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[57], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[57], param )

# -----------------------------------------------
# 物理攻击力加成（是指物理技能影响力额外的加成）
# -----------------------------------------------
class AddPercentSkillExtra:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[58], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[58], param )

# -----------------------------------------------
# 法术攻击力（是指法术技能影响力额外的加成）
# -----------------------------------------------
class AddPercentMagicSkillExtra:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[59], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[59], param )

# -----------------------------------------------
# 生命恢复速度加成
# -----------------------------------------------
class AddPercentHPRegen:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[60], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[60], param )

# -----------------------------------------------
# 法力恢复速度加成
# -----------------------------------------------
class AddPercentMPRegen:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[61], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[61], param )

# -----------------------------------------------
# 物理伤害减免加成
# -----------------------------------------------
class AddPercentDamageDerate:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[62], param )


	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[62], param )

# -----------------------------------------------
# 法术伤害减免
# -----------------------------------------------
class AddPercentMagicDamageDerate:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[63], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[63], param )

# -----------------------------------------------
# 伤害减免加成
# -----------------------------------------------
class AddPercentAllDerate:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[64], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[64], param )

# -----------------------------------------------
# 经验加成
# -----------------------------------------------
class AddPercentMultExp:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[65], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[65], param )

# -----------------------------------------------
# 潜能点加成
# -----------------------------------------------
class AddPercentMultPotential:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[66], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[66], param )


# -----------------------------------------------
# 移动速度加成
# -----------------------------------------------
class AddPercentMoveSpeed:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[67], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[67], param )

# -----------------------------------------------
# 攻击速度
# -----------------------------------------------
class AddPercentHitSpeed:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[68], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[68], param )

# -----------------------------------------------
# 元素相关
# -----------------------------------------------
#-------------火------------------------
class AddHuoDamage:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[107], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[107], param )

class AddHuoDamageBase:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[107], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[107], param )

class AddHuoDamagePercent:
	@staticmethod
	def description( param ):
		return _fFormatter3( lbs_EquipEffects[107], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter3( lbs_EquipEffects[107], param )

class AddHuoDamageExtra:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[107], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[107], param )

class AddHuoDamageValue:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[107], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[107], param )

class AddHuoDR:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[111], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[111], param )

class AddHuoDRBase:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[111], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[111], param )

class AddHuoDRPercent:
	@staticmethod
	def description( param ):
		return _fFormatter3( lbs_EquipEffects[111], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter3( lbs_EquipEffects[111], param )

class AddHuoDRExtra:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[111], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[111], param )

class AddHuoDRValue:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[111], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[111], param )
#-------------玄------------------------
class AddXuanDamage:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[108], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[108], param )

class AddXuanDamageBase:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[108], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[108], param )

class AddXuanDamagePercent:
	@staticmethod
	def description( param ):
		return _fFormatter3( lbs_EquipEffects[108], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter3( lbs_EquipEffects[108], param )

class AddXuanDamageExtra:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[108], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[108], param )

class AddXuanDamageValue:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[108], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[108], param )

class AddXuanDR:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[112], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[112], param )

class AddXuanDRBase:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[112], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[112], param )

class AddXuanDRPercent:
	@staticmethod
	def description( param ):
		return _fFormatter3( lbs_EquipEffects[112], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter3( lbs_EquipEffects[112], param )

class AddXuanDRExtra:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[112], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[112], param )

class AddXuanDRValue:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[112], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[112], param )
#-------------雷------------------------
class AddLeiDamage:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[109], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[109], param )

class AddLeiDamageBase:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[109], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[109], param )

class AddLeiDamagePercent:
	@staticmethod
	def description( param ):
		return _fFormatter3( lbs_EquipEffects[109], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter3( lbs_EquipEffects[109], param )

class AddLeiDamageExtra:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[109], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[109], param )

class AddLeiDamageValue:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[109], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[109], param )

class AddLeiDR:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[113], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[113], param )

class AddLeiDRBase:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[113], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[113], param )

class AddLeiDRPercent:
	@staticmethod
	def description( param ):
		return _fFormatter3( lbs_EquipEffects[113], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter3( lbs_EquipEffects[113], param )

class AddLeiDRExtra:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[113], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[113], param )

class AddLeiDRValue:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[113], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[113], param )
#-------------冰------------------------
class AddBingDamage:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[110], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[110], param )

class AddBingDamageBase:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[110], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[110], param )

class AddBingDamagePercent:
	@staticmethod
	def description( param ):
		return _fFormatter3( lbs_EquipEffects[110], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter3( lbs_EquipEffects[110], param )

class AddBingDamageExtra:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[110], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[110], param )

class AddBingDamageValue:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[110], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[110], param )

class AddBingDR:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[114], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[114], param )

class AddBingDRBase:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[114], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[114], param )

class AddBingDRPercent:
	@staticmethod
	def description( param ):
		return _fFormatter3( lbs_EquipEffects[114], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter3( lbs_EquipEffects[114], param )

class AddBingDRExtra:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[114], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[114], param )

class AddBingDRValue:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[114], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[114], param )
# -----------------------------------------------
#
# -----------------------------------------------
class SPEAddBuff:
	@staticmethod
	def description( param ):
		sk = skills.getSkill( param )
		return _fFormatter

	@staticmethod
	def descriptionList( param ):
		sk = skills.getSkill( param )
		return [lbs_EquipEffects[69], sk.getDescription()]

# -----------------------------------------------
#
# -----------------------------------------------
class SPEHitSpring:
	@staticmethod
	def description( param ):
		sk = skills.getSkill( param )
		return lbs_EquipEffects[100] + sk.getDescription()

	@staticmethod
	def descriptionList( param ):
		sk = skills.getSkill( param )
		return [lbs_EquipEffects[100], sk.getDescription()]


# -----------------------------------------------
#
# -----------------------------------------------
class SPEMagicHitSpring:

	@staticmethod
	def description( param ):
		sk = skills.getSkill( param )
		return lbs_EquipEffects[101] + sk.getDescription()

	@staticmethod
	def descriptionList( param ):
		sk = skills.getSkill( param )
		return [lbs_EquipEffects[101], sk.getDescription() ]


# -----------------------------------------------
#
# -----------------------------------------------
class SPEBeHitSpring:
	@staticmethod
	def description( param ):
		sk = skills.getSkill( param )
		return lbs_EquipEffects[102] + sk.getDescription()

	@staticmethod
	def descriptionList( param ):
		sk = skills.getSkill( param )
		return [lbs_EquipEffects[102], sk.getDescription() ]

# -----------------------------------------------
#
# -----------------------------------------------
class SPEBeDoubleHitSpring:
	@staticmethod
	def description( param ):
		sk = skills.getSkill( param )
		return lbs_EquipEffects[103] + sk.getDescription()

	@staticmethod
	def descriptionList( param ):
		sk = skills.getSkill( param )
		return [lbs_EquipEffects[103], sk.getDescription()]

# -----------------------------------------------
#
# -----------------------------------------------
class SPEDoubleHitSpring:
	@staticmethod
	def description( param ):
		sk = skills.getSkill( param )
		return lbs_EquipEffects[104] + sk.getDescription()

	@staticmethod
	def descriptionList( param ):
		sk = skills.getSkill( param )
		return [lbs_EquipEffects[104], sk.getDescription() ]

# -----------------------------------------------
#
# -----------------------------------------------
class SPEMagicDoubleHitSpring:

	@staticmethod
	def description( param ):
		sk = skills.getSkill( param )
		return lbs_EquipEffects[105] + sk.getDescription()

	@staticmethod
	def descriptionList( param ):
		sk = skills.getSkill( param )
		return [lbs_EquipEffects[105], sk.getDescription() ]

# -----------------------------------------------
#
# -----------------------------------------------
class SPEAddSkill:
	@staticmethod
	def description( param ):
		sk = skills.getSKill( param )
		return lbs_EquipEffects[106] + sk.getDescription()

	@staticmethod
	def descriptionList( param ):
		sk = skills.getSKill( param )
		return [lbs_EquipEffects[106], sk.getDescription()]

# -----------------------------------------------
#
# -----------------------------------------------
class SPENone:
	@staticmethod
	def description( param ):
		return ""

# -----------------------------------------------
# 增加冲锋破绽
# -----------------------------------------------
class AddBuffOdds1:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[117], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[117], param )

# -----------------------------------------------
# 增加猛击破绽
# -----------------------------------------------
class AddBuffOdds2:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[118], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[118], param )

# -----------------------------------------------
# 增加横扫破绽
# -----------------------------------------------
class AddBuffOdds3:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[119], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[119], param )

# -----------------------------------------------
# 增加泰山压顶破绽
# -----------------------------------------------
class AddBuffOdds4:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[120], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[120], param )

# -----------------------------------------------
# 增加劲射破绽
# -----------------------------------------------
class AddBuffOdds5:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[121], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[121], param )

# -----------------------------------------------
# 增加乱射破绽
# -----------------------------------------------
class AddBuffOdds6:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[122], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[122], param )

# -----------------------------------------------
# 增加落日破绽
# -----------------------------------------------
class AddBuffOdds7:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[123], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[123], param )

# -----------------------------------------------
# 增加快剑破绽
# -----------------------------------------------
class AddBuffOdds8:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[124], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[124], param )

# -----------------------------------------------
# 增加连绵剑破绽
# -----------------------------------------------
class AddBuffOdds9:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[125], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[125], param )

# -----------------------------------------------
# 增加追魂夺命破绽
# -----------------------------------------------
class AddBuffOdds10:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[126], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[126], param )

# -----------------------------------------------
# 增加火球术破绽
# -----------------------------------------------
class AddBuffOdds11:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[127], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[127], param )


# -----------------------------------------------
# 增加电击术破绽
# -----------------------------------------------
class AddBuffOdds12:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[128], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[128], param )


# -----------------------------------------------
# 增加风卷残云破绽
# -----------------------------------------------
class AddBuffOdds13:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[129], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[129], param )

#御敌
class AddValueReduceRoleD:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[130], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[130], param )
	
#破敌
class AddValueAddRoleD:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[131], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[131], param )
