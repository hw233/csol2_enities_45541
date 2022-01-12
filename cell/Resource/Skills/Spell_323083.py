# -*- coding: gb18030 -*-

from SpellBase import *
import csdefine
import csstatus
from bwdebug import *
from SpellBase.HomingSpell import ActiveHomingSpell
import SkillTargetObjImpl

# 第二个子技能的ID，由于当前技能的施法目标是一个位置，但第二个子技能的目标是自身，这里要做一个转换
SECOND_SKILL_ID = [ 323096 ]

class Spell_323083( ActiveHomingSpell ):
	# 暗杀
	def __init__( self ):
		ActiveHomingSpell.__init__( self )

	def onTick( self, caster ):
		spell = Spell.skillLoader[ self.getChildSpellID() ]
		if spell is None: return csstatus.SKILL_NOT_EXIST

 		target = self._target 
		if int( spell.getID() / 1000 ) in SECOND_SKILL_ID:
			target = SkillTargetObjImpl.createTargetObjEntity( caster )

		state = spell.castValidityCheck( caster, target  )
		if state != csstatus.SKILL_GO_ON: return state

		state = spell.checkRequire_( caster )
		if state != csstatus.SKILL_GO_ON: return state

		state = spell._castObject.valid( caster, target )
		spell.cast( caster, target )

		return csstatus.SKILL_GO_ON
