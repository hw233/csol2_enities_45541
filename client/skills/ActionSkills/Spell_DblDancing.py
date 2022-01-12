# -*- coding: gb18030 -*-
#
# $Id: Spell_Physics.py,v 1.5 2008-07-15 04:08:27 kebiao Exp $

"""
��ͨ������
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
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		Spell.init( self, dict )

	def getType( self ):
		"""
		��ü������͡�
		"""
		return csdefine.BASE_SKILL_TYPE_ACTION

	def getRangeMax( self, caster ):
		"""
		�����̡�
		"""
		return 0

	def useableCheck( self, caster, targetWrap ):
		if not targetWrap :											# û������Ŀ��
			return csstatus.JING_WU_SHI_KE_NO_TARGET
		target = targetWrap.getObject()
		if not target.isEntityType( csdefine.ENTITY_TYPE_ROLE ) :	# ֻ�����ɫ
			return csstatus.SKILL_CAST_OBJECT_INVALID
		if caster == target :										# ���������Լ�
			return csstatus.JING_WU_SHI_KE_ANTI_SELF
		if caster.vehicleDBID :											# �������ϲ���������
			return csstatus.JING_WU_SHI_KE_REQUEST_NOT_VEHICLE
		if caster.isMoving() :										# �ƶ��в�������
			return csstatus.JING_WU_SHI_KE_DANCE_NO_MOVING
		if caster.isJumping() :										# ��Ծ�в�������
			return csstatus.JING_WU_SHI_KE_DANCE_NO_JUMPING
		EffectState_List = csdefine.EFFECT_STATE_FIX | csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_SLEEP | csdefine.EFFECT_STATE_BE_HOMING
		# ��ɫ����������ڶ���ѣ�Ρ���˯״̬����������������
		if caster.effect_state & EffectState_List != 0:
			return csstatus.JING_WU_SHI_KE_REQUEST_NOT_FREE
		if target.effect_state & EffectState_List != 0:
			return csstatus.JING_WU_SHI_KE_REQUEST_NOT_FREE_TOO
		return Spell.useableCheck( self, caster, targetWrap )

	def rotate( self, caster, receiver ):
		"""
		ת������
		"""
		if caster.id == receiver.id:
			return

		#caster.turnaround( receiver.matrix, None )
		matrix = Math.Matrix()
		caster.turnaround( matrix, None )	# ת��̶�����
