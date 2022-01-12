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
import csarithmetic
import Math
import math

class Spell_HomingChild( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

		# 施法者位移数据
		self.casterMoveSpeed = 0.0
		self.casterMoveDistance = 0.0
		self.casterMoveFace = False

		# 受术者位移数据
		self.targetMoveSpeed = 0.0
		self.targetMoveDistance = 0.0
		self.targetMoveFace = False

		# 追击最近距离
		self.attackTargetDis = 0.0
		# 有效的开始追击距离
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
		系统施放，没有吟唱体，所以都是瞬发
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
		技能产生伤害时的动作效果等处理
		@param player:			玩家自己
		@type player:			Entity
		@param target:			Spell施放的目标Entity
		@type target:			Entity
		@param caster:			Buff施放者 可能为None
		@type castaer:			Entity
		@param damageType:		伤害类型
		@type damageType:		Integer
		@param damage:			伤害数值
		@type damage:			Integer
		"""
		if damageType & csdefine.DAMAGE_TYPE_REBOUND == csdefine.DAMAGE_TYPE_REBOUND:
			return
		
		#加入多个人打一个目标时的表现判断
		if target.beHomingCasterID != 0 and target.beHomingCasterID != caster.id :
			return
		
		#让位移和动作表现一致		
		id = self.getID()
		actionNames = []
		if caster:
			actionNames = self.hit( id, target )
			rds.skillEffect.playHitEffects( caster, target, id )
		rds.skillEffect.playCameraEffects( caster, target, id )
		
		#如果当前目标处于霸体状态，将不会差生位移
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
				if totalTime - 0.4 > 0: #加入0.4为seek需要消耗一点额外时间的弥补
					self.targetMoveSpeed = dis / ( totalTime - 0.4 )
			if target.__class__.__name__ == "PlayerRole":
				target.move_speed = self.targetMoveSpeed
				target.stopMove() #中断前面的受击移动
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
		播放受击动作
		@param skillID:			技能ID号
		@type skillID:			INT
		@param target:			Spell施放的目标Entity
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
	固定目标连击子技能
	"""

	def __init__( self ):
		"""
		"""
		Spell_HomingChild.__init__( self )

	def cast( self, caster, targetObject ) :
		"""
		virtual method
		系统施放，没有吟唱体，所以都是瞬发
		"""
		# 重新选择目标
		spellTarget = targetObject.getObject()
		if caster.id == BigWorld.player().id and targetObject.getType() == \
			csdefine.SKILL_TARGET_OBJECT_ENTITY and caster.id != spellTarget.id:
				rds.targetMgr.bindTarget( spellTarget )
		Spell_HomingChild.cast( self, caster, targetObject )


class Spell_HomingChild_Distance( Spell_HomingChild ):
	"""
	固定目标连击子技能
	"""

	def __init__( self ):
		"""
		"""
		Spell_HomingChild.__init__( self )

	def cast( self, caster, targetObject ):
		"""
		virtual method
		系统施放，没有吟唱体，所以都是瞬发
		"""
		Spell.cast( self, caster, targetObject )
		target = targetObject.getObject()
		# 施法者位移
		direction = Math.Vector3( target.position ) - Math.Vector3( caster.position )
		direction.normalise()
		distance = caster.distanceBB( target )
		dstPos = caster.position + direction * distance  # 防止重叠在一起
		endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )  # 作碰撞
		if caster == BigWorld.player():
			def __onMoveOver( success ):
				caster.stopMove()
				if not  success:
					DEBUG_MSG( "player move is failed." )
			caster.moveToDirectly( endDstPos, __onMoveOver )
		#if caster.isEntityType( csdefine.ENTITY_TYPE_MONSTER ):
		#	caster.lineToPoint( endDstPos, self.casterMoveSpeed )