# -*- coding: gb18030 -*-
#
# $Id: SkillAttack.py,v 1.17 2008-09-04 07:46:42 kebiao Exp $

"""
技能战斗计算相关 (spell,buff)
"""

from bwdebug import *
import BigWorld
import random
import csdefine
import csstatus
import SkillMessage
import csconst
from CombatSystemExp import CombatExp
import CombatUnitConfig

class SkillAttack:
	"""
	技能战斗计算相关 (spell,buff)
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		self._damageType = csdefine.DAMAGE_TYPE_VOID				# 伤害类别
		self._shareValPercent = 1.0 #共享附加值的计算比例
		self._huo_damage = 0
		self._xuan_damage = 0
		self._lei_damage = 0
		self._bing_damage = 0

	def init( self, dictDat ):
		"""
		初始化技能实例。
		@param dicDat:	技能配置数据
		@type  dictDat:	python 字典数据
		"""
		if dictDat[ "ShareValPercent" ] != -1.0:
			self._shareValPercent = dictDat[ "ShareValPercent" ] / 100.0

		if dictDat.has_key( "huo_damage" ):
			self._huo_damage = int( dictDat[ "huo_damage" ] )
		if dictDat.has_key( "xuan_damage" ):
			self._xuan_damage = int( dictDat[ "xuan_damage" ]  )
		if dictDat.has_key( "lei_damage" ):
			self._lei_damage = int( dictDat[ "lei_damage" ]  )
		if dictDat.has_key( "bing_damage" ):
			self._bing_damage = int( dictDat[ "bing_damage" ] )

	def calcProperty( self, baseVal, extraVal, percentVal, value ):
		"""
		创世基础计算总公式
		计算值=（基础值+附加值）*（1+加成）+加值
		@param baseVal: 基础值
		@param extraVal: 附加值
		@param percentVal: 加成
		@param value: 加值
		"""
		return ( baseVal + extraVal ) * ( 1 + percentVal ) + value

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
		return max( 0.25, min( 1, hitRate ) )

	def calcSkillHitStrength( self, source, receiver, dynPercent, dynValue ):
		"""
		virtual method.
		计算技能攻击力
		技能攻击力（总公式中的基础值）= 技能本身的攻击力+角色的物理攻击力
		@param source:	攻击方
		@type  source:	entity
		@param dynPercent:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加成
		@param  dynValue:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加值
		"""
		ERROR_MSG( "missing the function is need of implement!" )

	def calcVictimResist( self, source, target ):
		"""
		virtual method.
		计算被攻击方物理防御减伤
		角色基础物理防御值（总公式中的基础值）=0
		物理防御减伤（总公式中的基础值）= 防御值/(0.1*防御值+150*攻击方等级+1000)
		在攻防的计算中，防御值会先换算成防御减伤，然后再和攻击力进行换算。
		@param source:	攻击方
		@type  source:	entity
		@param target:	被攻击方
		@type  target:	entity
		@return: FLOAT
		"""
		exp = CombatExp( source, target )

		val = max( 0.0,  exp.getPhysicsDamageReductionRate() )
		if val > 0.95:
			val = 0.95
		return self.calcProperty( val, target.armor_reduce_damage_extra / csconst.FLOAT_ZIP_PERCENT, target.armor_reduce_damage_percent / csconst.FLOAT_ZIP_PERCENT, target.armor_reduce_damage_value / csconst.FLOAT_ZIP_PERCENT )

	def calcDamage( self, source, target, skillDamage ):
		"""
		virtual method.
		计算直接伤害
		普通物理伤害（总公式中的基础值）=物理攻击力*（1-被攻击方物理防御减伤）
		技能物理伤害（总公式中的基础值）=技能攻击力*（1-被攻击方物理防御减伤）

		@param source: 攻击方
		@type  source: entity
		@param target: 被攻击方
		@type  target: entity
		@param skillDamage: 技能攻击力
		@return: INT32
		"""
		# 计算被攻击方物理防御减伤
		armor = self.calcVictimResist( source, target )
		return ( skillDamage * ( 1 - armor ) ) * ( 1 + target.receive_damage_percent / csconst.FLOAT_ZIP_PERCENT ) + target.receive_damage_value

	def calcDamageScissor( self, caster, receiver, damage ):
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
		return caster.calcDamageScissor( receiver, damage )

	def calcDoubleMultiple( self, caster ):
		"""
		virtual method.
		计算暴击伤害加倍
		@param caster: 被攻击方
		@type  caster: entity
		@return type:计算后得到的暴击倍数
		"""
		return caster.double_hit_multiple

	def calcElemDamage( self, caster, receiver, attackdamage = 0 ):
		"""
		virtual method.
		计算元素伤害
		"""
		elemEffect = caster.queryTemp( "ELEM_ATTACK_EFFECT", "" )
		if elemEffect == "huo":		# 火元素攻击效果
			return [ caster.elem_huo_damage + self._huo_damage + attackdamage, \
					caster.elem_xuan_damage + self._xuan_damage, \
					caster.elem_lei_damage + self._lei_damage, \
					caster.elem_bing_damage + self._bing_damage ]
		elif elemEffect == "xuan":	# 玄元素攻击效果
			return [ caster.elem_huo_damage + self._huo_damage, \
					caster.elem_xuan_damage + self._xuan_damage + attackdamage, \
					caster.elem_lei_damage + self._lei_damage, \
					caster.elem_bing_damage + self._bing_damage ]
		elif elemEffect == "lei":	# 雷元素攻击效果
			return [ caster.elem_huo_damage + self._huo_damage, \
					caster.elem_xuan_damage + self._xuan_damage, \
					caster.elem_lei_damage + self._lei_damage + attackdamage, \
					caster.elem_bing_damage + self._bing_damage ]
		elif elemEffect == "bing":	# 冰元素攻击效果
			return [ caster.elem_huo_damage + self._huo_damage, \
					caster.elem_xuan_damage + self._xuan_damage, \
					caster.elem_lei_damage + self._lei_damage, \
					caster.elem_bing_damage + self._bing_damage + attackdamage ]
		else:
			return [ caster.elem_huo_damage + self._huo_damage, \
					caster.elem_xuan_damage + self._xuan_damage, \
					caster.elem_lei_damage + self._lei_damage, \
					caster.elem_bing_damage + self._bing_damage ]

	def calcElemDamageDeep( self, receiver, elemDamageList ):
		"""
		virtual method.
		元素伤害加深，被攻击方受到的元素伤害提高x%
		"""
		if elemDamageList[ 0 ] > 0:
			elemDamageList[ 0 ] = self.calcElemDamageDeepByElemType( receiver, csdefine.DAMAGE_TYPE_ELEM_HUO, elemDamageList[ 0 ] )
		if elemDamageList[ 1 ] > 0:
			elemDamageList[ 1 ] = self.calcElemDamageDeepByElemType( receiver, csdefine.DAMAGE_TYPE_ELEM_XUAN, elemDamageList[ 1 ] )
		if elemDamageList[ 2 ] > 0:
			elemDamageList[ 2 ] = self.calcElemDamageDeepByElemType( receiver, csdefine.DAMAGE_TYPE_ELEM_LEI, elemDamageList[ 2 ] )
		if elemDamageList[ 3 ] > 0:
			elemDamageList[ 3 ] = self.calcElemDamageDeepByElemType( receiver, csdefine.DAMAGE_TYPE_ELEM_BING, elemDamageList[ 3 ] )

	def calcElemDamageDeepByElemType( self, receiver, elemType, elemDamage ):
		"""
		virtual method.
		根据元素伤害类型计算元素伤害加深值
		"""
		if elemDamage <= 0:
			return elemDamage

		deep_ratio = 0.0
		if elemType == csdefine.DAMAGE_TYPE_ELEM_HUO:
			deep_ratio = receiver.elem_huo_deep_ratio
		elif elemType == csdefine.DAMAGE_TYPE_ELEM_XUAN:
			deep_ratio = receiver.elem_xuan_deep_ratio
		elif elemType == csdefine.DAMAGE_TYPE_ELEM_LEI:
			deep_ratio = receiver.elem_lei_deep_ratio
		elif elemType == csdefine.DAMAGE_TYPE_ELEM_BING:
			deep_ratio = receiver.elem_bing_deep_ratio
		return elemDamage * ( 1 + deep_ratio / csconst.FLOAT_ZIP_PERCENT )

	def calcElemDamageScissor( self, receiver, elemDamageList ):
		"""
		virtual method.
		计算被攻击方元素伤害削减
		角色受到来自对方的伤害为100物理伤害+30冰元素伤害，如果自身冰元素抗性为0时，
		最终产生的伤害将是130点。如果自身冰抗性为20%，则受到的最终伤害是100物理伤害+30*(1-20%)冰元素伤害=124点。
		"""
		if elemDamageList[ 0 ] > 0:
			elemDamageList[ 0 ] = self.calcElemDamageScissorByElemType( receiver, csdefine.DAMAGE_TYPE_ELEM_HUO, elemDamageList[ 0 ] )
		if elemDamageList[ 1 ] > 0:
			elemDamageList[ 1 ] = self.calcElemDamageScissorByElemType( receiver, csdefine.DAMAGE_TYPE_ELEM_XUAN, elemDamageList[ 1 ] )
		if elemDamageList[ 2 ] > 0:
			elemDamageList[ 2 ] = self.calcElemDamageScissorByElemType( receiver, csdefine.DAMAGE_TYPE_ELEM_LEI, elemDamageList[ 2 ] )
		if elemDamageList[ 3 ] > 0:
			elemDamageList[ 3 ] = self.calcElemDamageScissorByElemType( receiver, csdefine.DAMAGE_TYPE_ELEM_BING, elemDamageList[ 3 ] )

	def calcElemDamageScissorByElemType( self, receiver, elemType, elemDamage ):
		"""
		virtual method.
		计算被攻击方元素伤害削减
		角色受到来自对方的伤害为100物理伤害+30冰元素伤害，如果自身冰元素抗性为0时，
		最终产生的伤害将是130点。如果自身冰抗性为20%，则受到的最终伤害是100物理伤害+30*(1-20%)冰元素伤害=124点。
		"""
		if elemDamage <= 0:
			return elemDamage

		derate_ratio = 0.0
		if elemType == csdefine.DAMAGE_TYPE_ELEM_HUO:
			derate_ratio = receiver.elem_huo_derate_ratio
		elif elemType == csdefine.DAMAGE_TYPE_ELEM_XUAN:
			derate_ratio = receiver.elem_xuan_derate_ratio
		elif elemType == csdefine.DAMAGE_TYPE_ELEM_LEI:
			derate_ratio = receiver.elem_lei_derate_ratio
		elif elemType == csdefine.DAMAGE_TYPE_ELEM_BING:
			derate_ratio = receiver.elem_bing_derate_ratio
		return elemDamage * ( 1 - derate_ratio / csconst.FLOAT_ZIP_PERCENT )

	def calcShieldSuck( self, caster, receiver, attackDamage, attackDamageType, elemDamageList ):
		"""
		virtual method.
		计算护盾吸收
		"""
		if len( receiver.shields ) > 0:
			if attackDamage > 0:
				newdamage = caster.calcShieldSuck( receiver, attackDamage, attackDamageType )
			else:
				newdamage = attackDamage

			if elemDamageList[ 0 ] > 0:
				elemDamageList[ 0 ] = caster.calcShieldSuck( receiver, elemDamageList[ 0 ], csdefine.DAMAGE_TYPE_ELEM_HUO )
			if elemDamageList[ 1 ] > 0:
				elemDamageList[ 1 ] = caster.calcShieldSuck( receiver, elemDamageList[ 1 ], csdefine.DAMAGE_TYPE_ELEM_XUAN )
			if elemDamageList[ 2 ] > 0:
				elemDamageList[ 2 ] = caster.calcShieldSuck( receiver, elemDamageList[ 2 ], csdefine.DAMAGE_TYPE_ELEM_LEI )
			if elemDamageList[ 3 ] > 0:
				elemDamageList[ 3 ] = caster.calcShieldSuck( receiver, elemDamageList[ 3 ], csdefine.DAMAGE_TYPE_ELEM_BING )
		else:
			newdamage = attackDamage

		return newdamage

	def calcTwoSecondRule( self, source, skillDamageExtra ):
		"""
		virtual method.
		法术的2秒规则计算 (攻击型 buff or spell)
		"""
		pass # 由需求法术的基础模块去实现

	def calcBuff15SecondRule( self, damage ):
		"""
		virtual method.
		buff的15秒规则计算 (攻击型 buff)
		@param damage: 角色的攻击力 （物理或法术）
		"""
		pass # 由需求法术的基础模块去实现

	def initMagicDotDamage( self, caster, receiver, damage ):
		"""
		virtual method.
		初始化dot效果法术攻击力(伤害)最终值  （通常用于BUFF的作用值的计算）
		一般应用与BUFF多次伤害，  在doLoop的时候需要计算最终值， 主要是过程中可能会被护盾消耗
		@param receiver	:	被攻击方
		@type  receiver	:	entity
		@param damage	: 	BUFF的最终数值
		@return type	:	调整后的伤害
		"""
		extra = self.calcTwoSecondRule( caster, caster.magic_damage ) #经过2秒规则的共享附加值分成
		damage = self.calcProperty( damage, self.calcBuff15SecondRule( extra ),( caster.magic_skill_extra_percent + receiver.receive_magic_damage_percent )/ csconst.FLOAT_ZIP_PERCENT, caster.magic_skill_extra_value + receiver.receive_magic_damage_value)
		if self._loopSpeed > 0:
			damage /= int( self._persistent / self._loopSpeed )

		# 因为这个流程之后其他功能会参考此次的消减后的最终伤害所以此接口不能放到receiveDamage中
		damage = caster.calcMagicDamageScissor( receiver, damage )
		if damage < 0:
			damage = 0 # 防止各种因素减免伤害造成负数
		return damage

	def initPhysicsDotDamage( self, caster, receiver, damage ):
		"""
		virtual method.
		初始化dot效果物理攻击力(伤害)最终值  （通常用于BUFF的作用值的计算）
		一般应用与BUFF多次伤害，  在doLoop的时候需要计算最终值， 主要是过程中可能会被护盾消耗
		@param receiver: 被攻击方
		@type  receiver: entity
		@param damage: BUFF的最终数值
		@return type:调整后的伤害
		"""
		extra = ( caster.damage_min + caster.damage_max ) / 2
		damage = self.calcProperty( damage, self.calcBuff15SecondRule( extra ), ( caster.skill_extra_percent + receiver.receive_damage_percent )/ csconst.FLOAT_ZIP_PERCENT, caster.skill_extra_value + receiver.receive_damage_value )
		if self._loopSpeed > 0:
			damage /= int( self._persistent / self._loopSpeed )

		# 因为这个流程之后其他功能会参考此次的消减后的最终伤害所以此接口不能放到receiveDamage中
		damage = caster.calcDamageScissor( receiver, damage )
		if damage < 0:
			damage = 0 # 防止各种因素减免伤害造成负数
		return damage

	def calcDotDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		计算dot效果物理攻击力(伤害)最终值  （通常用于BUFF的作用值的计算）
		@param receiver: 被攻击方
		@type  receiver: entity
		@param damage: BUFF的最终数值
		@return type:调整后的伤害
		"""
		new_damage = caster.calcShieldSuck( receiver, damage, damageType )
		damageSuck = damage - new_damage

		if damageSuck > 0:
			SkillMessage.spell_DamageSuck( caster, receiver, damageSuck )
		else:
			if new_damage < 0:
				new_damage = 0
		return int( new_damage )

