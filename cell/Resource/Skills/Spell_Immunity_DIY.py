# -*- coding:gb18030 -*-

#edit by wuxo 2013-2-1

import Math
import math
import csdefine
import csarithmetic
import ECBExtend
import csstatus
from Spell_BuffNormal import Spell_CertainBuffNormal

class Spell_Immunity_DIY( Spell_CertainBuffNormal ):
	"""
	主动霸体
	"""
	def __init__( self ):
		"""
		"""
		Spell_CertainBuffNormal.__init__( self )
		#施法者位移数据
		self.moveDistance = 0.0	#移动距离
		self.moveSpeed    = 0.0	#移动速度
		self.casterMoveDistance = 0.0 # 施法者移动的距离
		self.casterMoveSpeed = 0.0	# 施法者移动的速度


	def init( self, data ):
		"""
		"""
		Spell_CertainBuffNormal.init( self, data )
		param1 = data["param1"].split(";")
		if len( param1 ) >= 2:
			self.moveDistance = float( param1[1] )
			self.moveSpeed = float( param1[0] )

		if data["param2"]:
			param2 = [ float(i) for i in  data["param2"].split(";") ]
			if len( param2 ) >= 2:
				self.casterMoveDistance, self.casterMoveSpeed = param2


	def calcDelay( self, caster, target ):
		"""
		virtual method.
		取得伤害延迟
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: float(秒)
		"""
		return  0.7

	def cast( self, caster, target ):
		"""
		virtual method.
		正式向一个目标或位置施放（或叫发射）法术，此接口通常直接（或间接）由intonate()方法调用。

		注：此接口即原来旧版中的castSpell()接口

		@param     caster: 使用技能的实体
		@type      caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		# 施法者位移
		Spell_CertainBuffNormal.cast( self, caster, target )
		caster.clearBuff( self._triggerBuffInterruptCode ) #中断buff
		for buff in self._buffLink:
			if buff.getBuff()._buffID == 11001:
				if self.canLinkBuff( caster, caster, buff ):
					buff.getBuff().receive( caster, caster )
					break
		if self.casterMoveDistance and self.casterMoveSpeed:
			pos = target.getObjectPosition()
			yaw = ( caster.position - pos ).yaw

			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			direction.normalise()
			dstPos = caster.position + direction * self.casterMoveDistance
			endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
			if ( endDstPos - dstPos ).length < 0.1:
				endDstPos = csarithmetic.getCollidePoint( caster.spaceID, endDstPos, Math.Vector3( endDstPos[0],endDstPos[1] - self.casterMoveDistance,endDstPos[2]) )
			if caster.__class__.__name__ != "Role" :
				caster.moveToPosFC( endDstPos, self.casterMoveSpeed, False )
			else:
				caster.move_speed = self.casterMoveSpeed
				caster.updateTopSpeed()
				timeData = (endDstPos - caster.position).length/self.casterMoveSpeed
				caster.addTimer( timeData+0.1, 0, ECBExtend.CHARGE_SPELL_CBID )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if receiver.isDestroyed:
			return
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		for buff in self._buffLink:
			if buff.getBuff()._buffID != 11001:
				if self.canLinkBuff( caster, caster, buff ):
					buff.getBuff().receive( caster, receiver )

		# 受术者位移
		#如果当前目标处于霸体状态，将不会差生位移
		if receiver.effect_state & ( csdefine.EFFECT_STATE_HEGEMONY_BODY | csdefine.EFFECT_STATE_INVINCIBILITY | csdefine.EFFECT_STATE_FIX ) > 0:
			return
		if self.moveDistance and self.moveSpeed:
			yaw = ( receiver.position - caster.position).yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			direction.normalise()
			dstPos = caster.position + direction * self.moveDistance
			endDstPos = csarithmetic.getCollidePoint( receiver.spaceID, receiver.position, dstPos )
			if ( endDstPos - dstPos ).length < 0.1:
				endDstPos = csarithmetic.getCollidePoint( receiver.spaceID, endDstPos, Math.Vector3( endDstPos[0],endDstPos[1]-self.moveDistance,endDstPos[2]) )
			if receiver.__class__.__name__ != "Role" :
				receiver.moveToPosFC( endDstPos, self.moveSpeed, False )
			else:
				perID = receiver.queryTemp( "HOMING_TIMMER", 0 )
				if perID:
					receiver.cancel( perID )
				receiver.move_speed = self.moveSpeed
				receiver.updateTopSpeed()
				timeData = (endDstPos - receiver.position).length/self.moveSpeed
				tid = receiver.addTimer( timeData + 0.1 , 0, ECBExtend.CHARGE_SPELL_CBID )	
				receiver.setTemp( "HOMING_TIMMER", tid )
		receiver.receiveSpell( caster.id, self.getID(), 0, 0, 0 )