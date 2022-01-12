# -*- coding: gb18030 -*-
#
# $Id: Spell_Face.py,v 1.5 2009-07-31 04:08:27 pengju Exp $

"""
播放表情技能
2009.07.31: by pengju
"""

import BigWorld
import csdefine
import csstatus
import ItemTypeEnum
from bwdebug import *
from skills.SpellBase import *

class Spell_Face( Spell ) :
	def __init__( self ) :
		Spell.__init__( self )

	def init( self, dict ) :
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell.init( self, dict )

	def getType( self ):
		"""
		获得技能类型。
		"""
		return csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL

	def getRangeMax( self, caster ):
		"""
		获得射程。
		"""
		return 0

	def useableCheck( self, caster, target ):
		player = BigWorld.player()
		if player is None :
			return csstatus.SKILL_IN_DEAD
		if player.vehicleDBID:
			return csstatus.ACTION_CANT_USE_ON_VEHICLE
		if player.isMoving():
			return csstatus.SKILL_CAN_NOT_PLAY_FACE
		EffectState_List = csdefine.EFFECT_STATE_FIX | csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_SLEEP | csdefine.EFFECT_STATE_BE_HOMING
		if player.effect_state & EffectState_List != 0:
			return csstatus.SKILL_CAN_NOT_PLAY_FACE
		return Spell.useableCheck( self, caster, target )
