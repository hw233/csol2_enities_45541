# -*- coding:gb18030 -*-

import BigWorld
import Math
import math
import csdefine
import csarithmetic
from Spell_PhysSkillImprove import Spell_PhysSkillImprove
import ECBExtend

class Spell_HitPush( Spell_PhysSkillImprove ):
	"""
	有伤害的位移技能
	"""
	def __init__( self ):
		"""
		"""
		Spell_PhysSkillImprove.__init__( self )

		# 施法者位移数据
		self.casterMoveSpeed = 0.0
		self.casterMoveDistance = 0.0
		# 受术者位移数据
		self.targetMoveSpeed = 0.0
		self.targetMoveDistance = 0.0

		self.param2 = 0
		self.param3 = 0

	def init( self, data ):
		"""
		"""
		Spell_PhysSkillImprove.init( self, data )

		param2 = data["param2"].split(";")
		self.param2 = len( param2 )
		if self.param2 >= 2:
			self.casterMoveSpeed = float( param2[0] )
			self.casterMoveDistance = float( param2[1] )
		param3 = data["param3"].split(";")
		self.param3 = len( param3 )
		if self.param3 >= 2:
			self.targetMoveSpeed = float( param3[0] )
			self.targetMoveDistance = float( param3[1] )

	def cast( self, caster, target ) :
		"""
		virtual method
		系统施放，没有吟唱体，所以都是瞬发
		"""
		# 施法者位移
		targetObject = target.getObject()
		if self.casterMoveDistance == 0.0:
			yaw = targetObject.yaw
			dstPos = targetObject.position - Math.Vector3( math.sin(yaw), 0, math.cos(yaw) ) * targetObject.distanceBB( targetObject )
		else:
			direction = Math.Vector3( targetObject.position ) - Math.Vector3( caster.position )
			direction.normalise()
			if direction == Math.Vector3():    #施法者与受术者刚好在一个位置
				yaw = caster.yaw
				direction = direction - ( Math.Vector3( math.sin(yaw), 0, math.cos(yaw) ) )
			dstPos = caster.position + direction * self.casterMoveDistance
		endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
		if self.param2 >= 2:
			if self.casterMoveSpeed:
				if caster.__class__.__name__ != "Role":
					caster.moveToPosFC( endDstPos, self.casterMoveSpeed, False )
				else:
					caster.move_speed = self.casterMoveSpeed
					caster.updateTopSpeed()
					timeData = ( endDstPos - caster.position ).length/self.casterMoveSpeed
					caster.addTimer( timeData, 0, ECBExtend.CHARGE_SPELL_CBID )
			else:   # 速度为零则为瞬移
				caster.position = endDstPos

		Spell_PhysSkillImprove.cast( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method = 0.
		针对每一个受术者进行受术处理，如计算伤害、改变属性等等。通常情况下此接口是由onArrive()调用，
		但它亦有可能由SpellUnit::receiveOnreal()方法调用，用于处理一些需要在受术者的real entity身上作的事情。
		但对于是否需要在real entity身上接收，由技能设计者在receive()中自行判断，并不提供相关机制。
		注：此接口为旧版中的onReceive()

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		if caster.isReal():
			Spell_PhysSkillImprove.receive( self, caster, receiver )

		if receiver.isDestroyed:
			return
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		#如果当前目标处于霸体状态，将不会产生位移
		if receiver.effect_state & ( csdefine.EFFECT_STATE_HEGEMONY_BODY | csdefine.EFFECT_STATE_INVINCIBILITY | csdefine.EFFECT_STATE_FIX ) > 0:
			return
		if self.param3 < 2: return
		# 受术者位移
		if self.targetMoveDistance == 0.0:
			yaw = caster.yaw
			dstPos = caster.position - Math.Vector3( math.sin(yaw), 0, math.cos(yaw) ) * caster.distanceBB( caster )
		else:
			yaw = caster.yaw
			direction = Math.Vector3( math.sin(yaw), 0, math.cos(yaw) )
			direction.normalise()
			dstPos = receiver.position + direction * self.targetMoveDistance
		endDstPos = csarithmetic.getCollidePoint( receiver.spaceID, receiver.position, dstPos )
		if ( endDstPos - dstPos ).length < 0.1:
			endDstPos = csarithmetic.getCollidePoint( receiver.spaceID, endDstPos, Math.Vector3( endDstPos[0],endDstPos[1]-self.targetMoveDistance,endDstPos[2]) )
		if self.targetMoveDistance <= 0.0 and not receiver.hasFlag( csdefine.ENTITY_FLAG_CANT_ROTATE_IN_FIGHT_STATE ):
			receiver.rotateToPos( caster.position )
		if receiver.__class__.__name__ != "Role":
			receiver.moveToPosFC( endDstPos, self.targetMoveSpeed, False )
		else:
			receiver.move_speed = self.targetMoveSpeed
			receiver.updateTopSpeed()
			timeData = (endDstPos - receiver.position).length/self.targetMoveSpeed
			receiver.addTimer( timeData, 0, ECBExtend.CHARGE_SPELL_CBID )
