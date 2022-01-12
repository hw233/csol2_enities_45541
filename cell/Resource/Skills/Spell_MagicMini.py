# -*- coding: gb18030 -*-

import random
import csdefine
import csstatus
from SpellBase import *
import BigWorld
import csconst
from bwdebug import *
from CombatSystemExp import CombatExp
import SkillTargetObjImpl

class Spell_MagicMini( MiniCombatSpell ):
	"""
	精简法术单体技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		MiniCombatSpell.__init__( self )
		self._damageType = csdefine.DAMAGE_TYPE_MAGIC				# 伤害类别

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		MiniCombatSpell.init( self, dict )

	def getType( self ):
		"""
		取得基础分类类型
		这些值是BASE_SKILL_TYPE_*之一
		"""
		return csdefine.BASE_SKILL_TYPE_MAGIC

	def getRangeMax( self, caster ):
		"""
		virtual method.
		@param caster: 施法者，通常某些需要武器射程做为距离的法术就会用到。
		@return: 施法距离
		"""
		return ( self._rangeMax + caster.magicSkillRangeVal_value ) * ( 1 + caster.magicSkillRangeVal_percent / csconst.FLOAT_ZIP_PERCENT )

	def getCastRange( self, caster ):
		"""
		法术释放距离
		"""
		return ( self._skillCastRange + caster.magicSkillRangeVal_value ) * ( 1 + caster.magicSkillRangeVal_percent / csconst.FLOAT_ZIP_PERCENT )

	def calcSkillHitStrength( self, source, receiver,dynPercent, dynValue ):
		"""
		virtual method.
		计算技能攻击力
		基础法术攻击力(总公式中的基础值)=智力*0.14
		法术技能攻击力(总公式中的基础值)=(法术技能本身的攻击力+角色法术攻击力受2秒规则计算后的值)*(1+法术攻击力加成)+法术攻击力加值
		注意：法术技能攻击力这里稍稍有些不同，计算后的角色法术攻击力，对法术技能攻击力起效时，是处于附加值的位置。
		@param source:	攻击方
		@type  source:	entity
		@param dynPercent:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加成
		@param  dynValue:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加值
		"""
		return source.magic_damage

	def calcVictimResist( self, source, target ):
		"""
		virtual method.
		计算被攻击方法术防御减伤
		角色基础法术防御值(总公式中的基础值)=0
		法术防御减伤(总公式中的基础值)= 法术防御值/(法术防御值+40*攻击方等级+350)-0.23
		@param source:	攻击方
		@type  source:	entity
		@param target:	被攻击方
		@type  target:	entity
		@return: FLOAT
		"""
		exp = CombatExp( source, target )
		val = max( 0.0, exp.getMagicDamageReductionRate() )
		if val > 0.95:
			val = 0.95
		return self.calcProperty( val, target.magic_armor_reduce_damage_extra / csconst.FLOAT_ZIP_PERCENT, target.magic_armor_reduce_damage_percent / csconst.FLOAT_ZIP_PERCENT, target.magic_armor_reduce_damage_value / csconst.FLOAT_ZIP_PERCENT )

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
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			
		# 防止其他原因导致的不可施法
		if caster.actionSign( csdefine.ACTION_FORBID_SPELL_MAGIC ):
			return csstatus.SKILL_CANT_CAST
		return CombatSpell.useableCheck( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver or receiver.isDestroyed:
			return
		armor = self.calcVictimResist( caster, receiver )
		skillDamage = self.calcSkillHitStrength( caster,receiver, 0, 0 )
		finiDamage = skillDamage * ( 1 - armor )
		#计算御敌、破敌带来的实际减免 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		finiDamage *= rm
			
		self.persentDamage( caster, receiver, self._damageType, finiDamage )

class Spell_MagicVolleyMini( Spell_MagicMini ):
	"""
	精简法术群体技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_MagicMini.__init__( self )
		self._skill = ChildSpell( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_MagicMini.init( self, dict )
		self._skill.init( dict )

	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		法术抵达目标通告。在默认情况下，此处执行可受术人员的获取，然后调用receive()方法进行对每个可受术者进行处理。
		注：此接口为旧版中的receiveSpell()

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""

		# 获取所有受术者
		receivers = self.getReceivers( caster, target )
		for receiver in receivers:
			self._skill.cast( caster, SkillTargetObjImpl.createTargetObjEntity( receiver ) )
			self.receiveEnemy( caster, receiver )

#