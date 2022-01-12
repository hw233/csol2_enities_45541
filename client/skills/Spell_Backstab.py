# -*- coding: gb18030 -*-

import BigWorld
import Math
import gbref
from SpellBase import *
import csstatus
import csarithmetic

"""
背刺
"""
class Spell_Backstab( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		
	def useableCheck( self, caster, target ):
		if target:
			result = csarithmetic.checkSkillCollide( caster.spaceID, caster.position, target.getObjectPosition() )
			if result:
				return csstatus.SKILL_CANT_ARRIVAL
		return Spell.useableCheck( self, caster, target )

	def rotate( self, caster, receiver ):
		pass