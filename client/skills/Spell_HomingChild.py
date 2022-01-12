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

class Spell_HomingChild( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

		# ʩ����λ������
		self.casterMoveSpeed = 0.0
		self.casterMoveDistance = 0.0
		self.casterMoveFace = False

		# ������λ������
		self.targetMoveSpeed = 0.0
		self.targetMoveDistance = 0.0
		self.targetMoveFace = False

		# ׷���������
		self.attackTargetDis = 0.0
		# ��Ч�Ŀ�ʼ׷������
		self.attackTrackDis = 6.0

	def init( self, data ):
		"""
		"""
		Spell.init( self, data )
		param2 = data["param2"].split(";")
		if len( param2 ) >= 3:
			self.casterMoveSpeed = float( param2[0] )
			self.casterMoveDistance = float( param2[1] )
			self.casterMoveFace = bool( int( param2[2] ) )
		param3 = data["param3"].split(";")
		if len( param3 ) >= 3:
			self.targetMoveSpeed = float( param3[0] )
			self.targetMoveDistance = float( param3[1] )
			self.targetMoveFace = bool( int( param3[2] ) )

		param4 = data["param4"].split(";")
		if len( param4 ) >= 2:
			self.attackTargetDis = float( param4[0] )
			self.attackTrackDis = float( param4[1] )

	def cast( self, caster, targetObject ) :
		"""
		virtual method
		ϵͳʩ�ţ�û�������壬���Զ���˲��
		"""
		target = targetObject.getObject()
		if caster.id == BigWorld.player().id:
			caster.setPhysicsHoming( self.attackTargetDis, self.attackTrackDis, target )
		Spell.cast( self, caster, targetObject )
		if self.casterMoveDistance and self.casterMoveSpeed:
			if target.id != caster.id:
				direction = target.position - caster.position
				direction.normalise()
			else:
				yaw = caster.yaw
				direction = Math.Vector3( math.sin( yaw ),0.0, math.cos( yaw ) )
			
			dstPos = caster.position + direction * self.casterMoveDistance
			endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
			if caster == BigWorld.player():
				def __onMoveOver( success ):
					caster.stopMove()
					if not success :
						DEBUG_MSG( "player move is failed." )
				caster.moveToDirectly( endDstPos, __onMoveOver )

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
		
		#�������˴�һ��Ŀ��ʱ�ı����ж�
		if target.beHomingCasterID != 0 and target.beHomingCasterID != caster.id :
			return
		
		#��λ�ƺͶ�������һ��		
		id = self.getID()
		actionNames = []
		if caster:
			actionNames = self.hit( id, target )
			rds.skillEffect.playHitEffects( caster, target, id )
		rds.skillEffect.playCameraEffects( caster, target, id )
		
		#�����ǰĿ�괦�ڰ���״̬�����������λ��
		if target.effect_state & ( csdefine.EFFECT_STATE_HEGEMONY_BODY | csdefine.EFFECT_STATE_INVINCIBILITY | csdefine.EFFECT_STATE_FIX  ) > 0:
			return
		if self.targetMoveDistance:
			if not target.homingDir:
				yaw = caster.yaw
				target.homingDir = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			
			direction = target.homingDir
			dstPos = target.position + direction * self.targetMoveDistance
			endDstPos = csarithmetic.getCollidePoint( target.spaceID, target.position, dstPos )
			dis = ( endDstPos - target.position ).length
			
			if self.targetMoveSpeed < 0.1:
				totalTime = 0
				for ac in actionNames:
					if target.getModel():
						totalTime += target.getModel().action( ac ).duration
				if totalTime - 0.4 > 0: #����0.4Ϊseek��Ҫ����һ�����ʱ����ֲ�
					self.targetMoveSpeed = dis / ( totalTime - 0.4 )
			if target.__class__.__name__ == "PlayerRole":
				target.move_speed = self.targetMoveSpeed
				target.stopMove() #�ж�ǰ����ܻ��ƶ�
				def __onMoveOver( success ):
					target.stopMove()
					if not  success:
						DEBUG_MSG( "player move is failed." )
				target.moveToDirectly( endDstPos, __onMoveOver )
			else:
				if self.targetMoveSpeed < 0.1:
					target.homingTotalTime = totalTime

	def hit( self, skillID, target ):
		"""
		�����ܻ�����
		@param skillID:			����ID��
		@type skillID:			INT
		@param target:			Spellʩ�ŵ�Ŀ��Entity
		@type target:			Entity
		"""
		if target is None:
			return []
		if target.actionStateMgr( ):
			weaponType = target.getWeaponType()
			vehicleType = 0
			if target.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				vehicleType = target.vehicleType
			actionNames = rds.spellEffect.getHitAction( skillID, weaponType, vehicleType )
			target.playActions( actionNames )
			return actionNames
		else:
			return []

class Spell_FixTargetHomingChild( Spell_HomingChild ):
	"""
	�̶�Ŀ�������Ӽ���
	"""

	def __init__( self ):
		"""
		"""
		Spell_HomingChild.__init__( self )

	def cast( self, caster, targetObject ) :
		"""
		virtual method
		ϵͳʩ�ţ�û�������壬���Զ���˲��
		"""
		# ����ѡ��Ŀ��
		spellTarget = targetObject.getObject()
		if caster.id == BigWorld.player().id and targetObject.getType() == \
			csdefine.SKILL_TARGET_OBJECT_ENTITY and caster.id != spellTarget.id:
				rds.targetMgr.bindTarget( spellTarget )
		Spell_HomingChild.cast( self, caster, targetObject )


class Spell_HomingChild_Distance( Spell_HomingChild ):
	"""
	�̶�Ŀ�������Ӽ���
	"""

	def __init__( self ):
		"""
		"""
		Spell_HomingChild.__init__( self )

	def cast( self, caster, targetObject ):
		"""
		virtual method
		ϵͳʩ�ţ�û�������壬���Զ���˲��
		"""
		Spell.cast( self, caster, targetObject )
		target = targetObject.getObject()
		# ʩ����λ��
		direction = Math.Vector3( target.position ) - Math.Vector3( caster.position )
		direction.normalise()
		distance = caster.distanceBB( target )
		dstPos = caster.position + direction * distance  # ��ֹ�ص���һ��
		endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )  # ����ײ
		if caster == BigWorld.player():
			def __onMoveOver( success ):
				caster.stopMove()
				if not  success:
					DEBUG_MSG( "player move is failed." )
			caster.moveToDirectly( endDstPos, __onMoveOver )
		#if caster.isEntityType( csdefine.ENTITY_TYPE_MONSTER ):
		#	caster.lineToPoint( endDstPos, self.casterMoveSpeed )