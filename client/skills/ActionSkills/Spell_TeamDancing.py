# -*- coding: gb18030 -*-
#
# $Id: Spell_TeamDancing.py,v 1.28 2009.11.04 10:02:41 pengju Exp $

"""
队伍共舞
2009.11.04: by pengju
"""

import BigWorld
import csdefine
import csstatus
import ItemTypeEnum
from bwdebug import *
from skills.SpellBase import *

class Spell_TeamDancing( Spell ) :
	def __init__( self ):
		Spell.__init__( self )

	def init( self, dict ):
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
			return csstatus.JING_WU_SHI_KE_DANCE_NO_MOVING
		if player.isJumping():
			return csstatus.JING_WU_SHI_KE_DANCE_NO_JUMPING
		if not player.isInTeam():
			return csstatus.JING_WU_SHI_KE_NO_TEAM
		else:
			if player.isTeamLeading():
				return csstatus.JING_WU_SHI_KE_DANCE_NO_FOLLOWING
			EffectState_List = csdefine.EFFECT_STATE_FIX | csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_SLEEP | csdefine.EFFECT_STATE_BE_HOMING
			# 定身、眩晕、昏睡状态不能邀请跳舞
			if player.effect_state & EffectState_List != 0:
				return csstatus.JING_WU_SHI_KE_REQUEST_NOT_FREE
		return Spell.useableCheck( self, caster, target )
