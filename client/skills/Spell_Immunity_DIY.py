# -*- coding: gb18030 -*-

"""
Spell�����ࡣ
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

class Spell_Immunity_DIY( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.moveDistance = 0.0	#�ƶ�����
		self.moveSpeed    = 0.0	#�ƶ��ٶ�
		self.casterMoveDistance = 0.0 # ʩ�����ƶ��ľ���
		self.casterMoveSpeed = 0.0	# ʩ�����ƶ����ٶ�


	def init( self, data ):
		"""
		"""
		Spell.init( self, data )
		param1 = data["param1"].split(";")
		if len( param1 ) >= 2:
			self.moveDistance = float( param1[1] )
			self.moveSpeed = float( param1[0] )

		if data["param2"]:
			param2 = [ float(i) for i in  data["param2"].split(";") ]
			if len( param2 ) >= 2:
				self.casterMoveDistance, self.casterMoveSpeed = param2

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		if hasattr( caster, "state" ):
			if caster.state == csdefine.ENTITY_STATE_DEAD:	# ��ʩ�����Ƿ��������ж�
				return csstatus.SKILL_IN_DEAD

		# ���Ŀ���Ƿ����
		state = self.validTarget( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ���ʩ���ߵ������Ƿ��㹻
		state = self._checkRequire( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		if caster.intonating():
			return csstatus.SKILL_INTONATING

		# �������Ƿ��ھ��������������GM�۲���״̬
		player = BigWorld.player()
		if caster == player:
			if caster.isDeadWatcher() or caster.isGMWatcher():
				return csstatus.SKILL_NOT_IN_POSTURE

		# ��鼼��cooldown ���ݿ������ɫ��������������������ж�˳�� ���ֻ�ܷ����
		if not self.isCooldown( caster ):
			return csstatus.SKILL_NOT_READY
		if caster.isInHomingSpell:
			return csstatus.SKILL_CANT_CAST
		return csstatus.SKILL_GO_ON

	def receiveSpell( self, target, casterID, damageType, damage  ):
		"""
		���ܼ��ܴ���

		@type   casterID: OBJECT_ID
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		player = BigWorld.player()
		caster = None
		if casterID:
			try:
				caster = BigWorld.entities[casterID]
			except KeyError:
				#�����������ԭ���� �ڷ�������һ��entity����һ��entityʩ�� ���������ǿ��ĵ�ʩ���ߵ�
				#���ͻ��˿��ܻ���Ϊĳԭ�� �磺�����ӳ� ���ڱ���û�и��µ�AOI�е��Ǹ�ʩ����entity����
				#��������ִ��� written by kebiao.  2008.1.8
				return
		# ������Ч����
		self._skillAE( player, target, caster, damageType, damage  )

	def cast( self, caster, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )
		target = targetObject.getObject()
		if self.casterMoveDistance and self.casterMoveSpeed:
			direction = caster.position - target.position
			direction.normalise()
			dstPos = caster.position + direction * self.casterMoveDistance
			endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
			if caster == BigWorld.player():
				def __onMoveOver( success ):
					if success:
						caster.stopMove()
					else:
						DEBUG_MSG( "player move is failed." )
					rds.skillEffect.interrupt( caster )#��Ч�ж�
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
		if damageType & csdefine.DAMAGE_TYPE_REBOUND == csdefine.DAMAGE_TYPE_REBOUND:
			return
		id = self.getID()
		if caster:
			self.hit( id, target )
			rds.skillEffect.playHitEffects( caster, target, id )
		rds.skillEffect.playCameraEffects( caster, target, id )
		#�����ǰĿ�괦�ڰ���״̬�����������λ��
		if target.effect_state & ( csdefine.EFFECT_STATE_HEGEMONY_BODY | csdefine.EFFECT_STATE_INVINCIBILITY| csdefine.EFFECT_STATE_FIX ) > 0:
			return
		if self.moveDistance and self.moveSpeed:
			yaw = ( target.position - caster.position).yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			direction.normalise()
			dstPos = caster.position + direction * self.moveDistance
			endDstPos = csarithmetic.getCollidePoint( target.spaceID, target.position, dstPos )
			endDstPos = csarithmetic.getCollidePoint( target.spaceID, endDstPos+(0,-3,0), endDstPos+(0,3,0) )
			if target.__class__.__name__ == "PlayerRole":
				target.move_speed = self.moveSpeed
				def __onMoveOver( success ):
					target.stopMove()
					if not  success:
						DEBUG_MSG( "player move is failed." )
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
			rds.actionMgr.playActions( target.getModel(),actionNames )
