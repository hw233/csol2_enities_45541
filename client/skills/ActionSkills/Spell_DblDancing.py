# -*- coding: gb18030 -*-
#
# $Id: Spell_Physics.py,v 1.5 2008-07-15 04:08:27 kebiao Exp $

"""
普通物理技能
"""
import BigWorld
import csdefine
import csstatus
import ItemTypeEnum
from bwdebug import *
from skills.SpellBase import *
import Math

class Spell_DblDancing( Spell ) :
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
		return csdefine.BASE_SKILL_TYPE_ACTION

	def getRangeMax( self, caster ):
		"""
		获得射程。
		"""
		return 0

	def useableCheck( self, caster, targetWrap ):
		if not targetWrap :											# 没有邀请目标
			return csstatus.JING_WU_SHI_KE_NO_TARGET
		target = targetWrap.getObject()
		if not target.isEntityType( csdefine.ENTITY_TYPE_ROLE ) :	# 只允许角色
			return csstatus.SKILL_CAST_OBJECT_INVALID
		if caster == target :										# 不能邀请自己
			return csstatus.JING_WU_SHI_KE_ANTI_SELF
		if caster.vehicleDBID :											# 在坐骑上不允许邀请
			return csstatus.JING_WU_SHI_KE_REQUEST_NOT_VEHICLE
		if caster.isMoving() :										# 移动中不能邀请
			return csstatus.JING_WU_SHI_KE_DANCE_NO_MOVING
		if caster.isJumping() :										# 跳跃中不能邀请
			return csstatus.JING_WU_SHI_KE_DANCE_NO_JUMPING
		EffectState_List = csdefine.EFFECT_STATE_FIX | csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_SLEEP | csdefine.EFFECT_STATE_BE_HOMING
		# 角色和邀请对象在定身、眩晕、昏睡状态都不允许邀请跳舞
		if caster.effect_state & EffectState_List != 0:
			return csstatus.JING_WU_SHI_KE_REQUEST_NOT_FREE
		if target.effect_state & EffectState_List != 0:
			return csstatus.JING_WU_SHI_KE_REQUEST_NOT_FREE_TOO
		return Spell.useableCheck( self, caster, targetWrap )

	def rotate( self, caster, receiver ):
		"""
		转动方向
		"""
		if caster.id == receiver.id:
			return

		#caster.turnaround( receiver.matrix, None )
		matrix = Math.Matrix()
		caster.turnaround( matrix, None )	# 转向固定朝向
