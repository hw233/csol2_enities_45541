# -*- coding: gb18030 -*-


from Spell_BuffNormal import Spell_BuffNormal
from Spell_Dispersion import Spell_EffectDispersion
import csconst
import csstatus


class Spell_Rabbit_Run( Spell_BuffNormal ):
	def useableCheck( self, caster, target ):
		"""
		"""
		if target.getObject().findBuffByID( csconst.RABBIT_RUN_CATCH_RABBIT_RABBIT_BUFF_ID ) is None:
			return csstatus.RABBIT_RUN_NOT_RABBIT
		if target.getObject().findBuffByID( csconst.RABBIT_RUN_WAIT_BUFF_ID ) is not None:
			return csstatus.SKILL_CANT_CAST
		if target.getObject().findBuffByID( csconst.RABBIT_RUN_QUESTION_BUFF_ID ) is not None:
			return csstatus.RABBIT_RUN_HAS_QUESTION_BUFF
		return Spell_BuffNormal.useableCheck( self, caster, target )
		

class Spell_Rabbit_Run_Rabbit_Skill( Spell_EffectDispersion ):
	def useableCheck( self, caster, target ):
		"""
		"""
		if target.getObject().findBuffByID( csconst.RABBIT_RUN_CATCH_RABBIT_RABBIT_BUFF_ID ) is None:
			return csstatus.RABBIT_RUN_NOT_RABBIT
		if target.getObject().findBuffByID( csconst.RABBIT_RUN_WAIT_BUFF_ID ) is not None:
			return csstatus.SKILL_CANT_CAST
		return Spell_EffectDispersion.useableCheck( self, caster, target )