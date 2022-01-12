# -*- coding: gb18030 -*-

"""
Spell技能类。
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import csstatus
import csdefine
from gbref import rds

MODEL_PATH = "particles/model/gw1355.model"

class Spell_112051( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )


	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		caster.setVisibility( False )
		Spell.cast( self, caster, targetObject )
