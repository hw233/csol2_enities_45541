# -*- coding: gb18030 -*-
#
# $Id:  Exp $


from SpellBase import *
import random
import csdefine
import csstatus
from bwdebug import *
from Spell_BuffNormal import *

class Spell_BuffRacehorse( Spell_BuffNormal ):
	"""
	"""
	def useableCheck( self, caster, target ):
		"""
		"""
		# 检查技能cooldown
		if not self.isCooldown( caster ):
			return csstatus.SKILL_ITEM_NOT_READY
		return csstatus.SKILL_GO_ON