# -*- coding: gb18030 -*-
#
# $Id: Spell_Physics.py,v 1.28 2008-08-13 07:55:41 kebiao Exp $

"""
持续性效果
"""

import random
import csdefine
import csstatus
from SpellBase import *
import BigWorld
from bwdebug import *
import Const
import csconst
from CombatSystemExp import CombatExp

class Spell_PhysicsMini( MiniCombatSpell ):
	"""
	普通物理攻击
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		MiniCombatSpell.__init__( self )
		self._baseType = csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL
		self._damageType = csdefine.DAMAGE_TYPE_PHYSICS_NORMAL				# 伤害类别
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		MiniCombatSpell.init( self, dict )

	def calcSkillHitStrength( self, source, receiver,dynPercent, dynValue ):
		"""
		virtual method.
		计算技能攻击力
		技能攻击力（总公式中的基础值）= 角色的物理攻击力
		"""
		#普通物理攻击 只需要返回source.damage
		return random.randint( int( source.damage_min ), int( source.damage_max ) )

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