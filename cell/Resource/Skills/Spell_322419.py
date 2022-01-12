# -*- coding: gb18030 -*-
#
from Spell_BuffNormal import Spell_BuffNormal
import random
import csdefine
import csstatus

class Spell_322419( Spell_BuffNormal ):
	"""
	迷香技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_BuffNormal.__init__( self )

	def useableCheck( self, caster, receiver ):
		"""
		virtual method.
		校验技能是否可以使用
		"""
		# 只能在潜行状态下使用
		if caster.effect_state & csdefine.EFFECT_STATE_PROWL == 0:
			return csstatus.SKILL_NEED_STATE_PROWL
		# 无法再骑宠上使用
		if caster.vehicleModelNum:
			return csstatus.SKILL_NEED_STATE_NO_VEHICLE
		return Spell_BuffNormal.useableCheck( self, caster, receiver )