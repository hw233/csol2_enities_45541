# -*- coding: gb18030 -*-

from SpellBase import *
import csdefine
import csstatus
from bwdebug import *
from SpellBase.HomingSpell import ActiveHomingSpell
import SkillTargetObjImpl

# �ڶ����Ӽ��ܵ�ID�����ڵ�ǰ���ܵ�ʩ��Ŀ����һ��λ�ã����ڶ����Ӽ��ܵ�Ŀ������������Ҫ��һ��ת��
SECOND_SKILL_ID = [ 323096 ]

class Spell_323083( ActiveHomingSpell ):
	# ��ɱ
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
