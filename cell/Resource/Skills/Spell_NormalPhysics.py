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
from Spell_Physics import Spell_Physics

class Spell_NormalPhysics( Spell_Physics ):
	"""
	普通物理攻击
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Physics.__init__( self )


	def persentDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		对受术者呈现最终伤害
		通常用于这些情况需要重载 需要根据对某entity所产生的伤害 进行其他方面的影响
		"""
		receiver.receiveSpell( caster.id, self.getID(), damageType, damage, 0 )
		receiver.receiveDamage( caster.id, self.getID(), damageType, damage )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if receiver.isDestroyed:
			return

		# 计算命中率
		hit = 0.9
		if receiver.effect_state & csdefine.EFFECT_STATE_INVINCIBILITY > 0 or not random.random() < hit:
			self.onMiss( self._damageType, caster, receiver )				# 本技能未命中
			return

		# 计算技能攻击力和计算直接伤害
		skillDamage = self.calcSkillHitStrength( caster,receiver, 0, 0 )
		
		#计算御敌、破敌带来的实际减免 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		skillDamage *= rm
		# 给出手击者伤害 最少也得造成1点伤害
		self.persentDamage( caster, receiver, self._damageType, max( 1, int( skillDamage ) ) )
