# -*- coding: gb18030 -*-

import csdefine
from SpellBase import *

class Spell_111007( CombatSpell ):
	"""
	造成当前目标生命值上限的一定比例的物理伤害，无视防御
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		CombatSpell.__init__( self )
		self._damageType = csdefine.DAMAGE_TYPE_PHYSICS		# 伤害类别
		self._percentage = 0								# 伤害百分比

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		CombatSpell.init( self, dict )
		self._percentage = int( dict["param1"] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		if receiver.isDestroyed:
			return

		finiDamage = int( receiver.HP_Max * self._percentage / 100 )
		#计算御敌、破敌带来的实际减免 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		finiDamage *= rm

		self.persentDamage( caster, receiver, self._damageType, max( 1, int( finiDamage ) ) )
		self.receiveLinkBuff( caster, receiver )