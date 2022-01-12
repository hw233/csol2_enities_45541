# -*- coding:gb18030 -*-

#edit by wuxo 2012-2-23


import Math
import math
import csdefine
import ECBExtend
import csarithmetic
import SkillTargetObjImpl
from Spell_PhysSkillImprove import Spell_PhysSkillImprove

class Spell_Charge( Spell_PhysSkillImprove ):
	"""
	排兵布阵-冲锋技能
	"""
	def __init__( self ):
		"""
		"""
		Spell_PhysSkillImprove.__init__( self )
		# 受术者位移数据
		self.targetMoveSpeed = 0.0	#击退速度
		self.targetMoveDistance = 0.0		#击退距离
		#施法者位移数据
		self.casterMoveDistance = 0.0	#冲刺距离
		self.casterMoveSpeed    = 0.0	#冲刺速度
		self.casterMoveFace     = False  #冲刺方向和释放者朝向是否一致

		self.chargeDirection    = None	#冲刺方向


	def init( self, data ):
		"""
		"""
		Spell_PhysSkillImprove.init( self, data )

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



	def cast( self, caster, target ) :
		"""
		virtual method
		"""
		# 施法者位移
		if self.casterMoveDistance and self.casterMoveSpeed:
			yaw = caster.yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			direction.normalise()
			dstPos = caster.position + direction * self.casterMoveDistance
			endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
			if caster.__class__.__name__ != "Role":
				caster.moveToPosFC( endDstPos, self.casterMoveSpeed, self.casterMoveFace )
			else:
				caster.move_speed = self.casterMoveSpeed
				caster.updateTopSpeed()
				timeData = ( endDstPos - caster.position ).length/self.casterMoveSpeed
				caster.addTimer( timeData, 0, ECBExtend.CHARGE_SPELL_CBID )

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

		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return


		# 受术者位移
		#如果当前目标处于霸体状态，将不会位移
		if receiver.effect_state & ( csdefine.EFFECT_STATE_HEGEMONY_BODY | csdefine.EFFECT_STATE_INVINCIBILITY | csdefine.EFFECT_STATE_FIX ) > 0:
			return
		if  self.targetMoveDistance and self.targetMoveSpeed:
			
			yaw = caster.yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			direction.normalise()
			dstPos = receiver.position + direction * self.targetMoveDistance
			endDstPos = csarithmetic.getCollidePoint( receiver.spaceID, receiver.position, dstPos )
			if receiver.__class__.__name__ != "Role" :
				receiver.moveToPosFC( endDstPos, self.targetMoveSpeed, False )
			else:
				receiver.move_speed = self.targetMoveSpeed
				receiver.updateTopSpeed()
				timeData = (endDstPos - receiver.position).length/self.targetMoveSpeed
				receiver.addTimer( timeData, 0, ECBExtend.CHARGE_SPELL_CBID )
	
	def getReceivers( self, caster, target ):
		"""
		virtual method
		取得所有的符合条件的受术者Entity列表；
		所有的onArrive()方法都应该调用此方法来获取有效的entity。
		@return: array of Entity
		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		dstPos = caster.position
		target = SkillTargetObjImpl.createTargetObjPosition(dstPos)
		return Spell_PhysSkillImprove.getReceivers( self, caster, target )

