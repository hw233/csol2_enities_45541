# -*- coding: gb18030 -*-

"""
�ű�����-��漼�ܿͻ�����
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import csstatus
import csdefine
from gbref import rds
import csarithmetic
import Math
import math

class Spell_Charge( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

		# ������λ������
		self.targetMoveSpeed = 0.0	#�����ٶ�
		self.targetMoveDistance = 0.0		#���˾���
		#ʩ����λ������
		self.casterMoveDistance = 0.0	#��̾���
		self.casterMoveSpeed    = 0.0	#����ٶ�
		self.casterMoveFace     = False  #��̷�����ͷ��߳����Ƿ�һ��

		self.chargeDirection    = None	#��̷���


	def init( self, data ):
		Spell.init( self, data )
		param2 = data["param2"].split(";")
		if len( param2 ) >= 2:
			self.targetMoveSpeed = float( param2[0] )
			self.targetMoveDistance = float( param2[1] )

		param3 = data["param3"].split(";")
		if len( param3 ) >= 3:
			self.casterMoveSpeed = float( param3[0] )
			self.casterMoveDistance = float( param3[1] )
			self.casterMoveFace = bool( int( param3[2] ) )
		if data["param4"] != "":
			self.chargeDirection = eval(data["param4"])

	def cast( self, caster, targetObject ):
		"""
		"""
		Spell.cast( self, caster, targetObject )
		if  self.casterMoveDistance and self.casterMoveSpeed:
			yaw = caster.yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			direction.normalise()
			dstPos = caster.position + direction * self.casterMoveDistance
			endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
			if caster == BigWorld.player():
				def __onMoveOver( success ):
					rds.skillEffect.interrupt( caster )#��Ч�ж�
					caster.stopMove()
					if not  success:
						DEBUG_MSG( "player move is failed." )
				caster.moveToDirectly( endDstPos, __onMoveOver )
				if self.casterMoveFace:
					BigWorld.dcursor().yaw = yaw


	def _skillAE( self, player, target, caster, damageType, damage ):
		"""
		���ܲ����˺�ʱ�Ķ���Ч���ȴ���
		@param player:			����Լ�
		@type player:			Entity
		@param target:			Spellʩ�ŵ�Ŀ��Entity
		@type target:			Entity
		@param caster:			Buffʩ���� ����ΪNone
		@type castaer:			Entity
		@param damageType:		�˺�����
		@type damageType:		Integer
		@param damage:			�˺���ֵ
		@type damage:			Integer
		"""
		Spell._skillAE( self, player, target, caster, damageType, damage )
		#�����ǰĿ�괦�ڰ���״̬�����������λ��
		if target.effect_state & ( csdefine.EFFECT_STATE_HEGEMONY_BODY | csdefine.EFFECT_STATE_INVINCIBILITY | csdefine.EFFECT_STATE_FIX ) > 0:
			return
		if self.targetMoveDistance and self.targetMoveSpeed:
			yaw = caster.yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			direction.normalise()
			dstPos = target.position + direction * self.targetMoveDistance
			endDstPos = csarithmetic.getCollidePoint( target.spaceID, target.position, dstPos )

			if target.id == BigWorld.player().id:
				def __onMoveOver( success ):
					target.stopMove()
					if not  success:
						DEBUG_MSG( "player move is failed." )
					rds.skillEffect.interrupt( caster )#��Ч�ж�
				target.moveToDirectly( endDstPos, __onMoveOver )



	def hit( self, skillID, target ):
		"""
		�����ܻ�����
		@param skillID:			����ID��
		@type skillID:			INT
		@param target:			Spellʩ�ŵ�Ŀ��Entity
		@type target:			Entity
		"""
		if target is None:
			return
		if target.actionStateMgr( ):
			weaponType = target.getWeaponType()
			vehicleType = 0
			if target.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				vehicleType = target.vehicleType
			actionNames = rds.spellEffect.getHitAction( skillID, weaponType, vehicleType )
			target.playActions( actionNames )


