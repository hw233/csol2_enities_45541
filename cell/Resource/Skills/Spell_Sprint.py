# -*- coding:gb18030 -*-

#edit by wuxo 2012-7-26

import Math
import math
import csarithmetic
import ECBExtend
from SpellBase import *
import csstatus
import csdefine
from VehicleHelper import getCurrVehicleID

class Spell_Sprint( Spell):
	"""
	轻功系统-冲刺技能
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.moveSpeed = 0.0
		self.time  = 0.0
		self.needEnergy = 0
		
	def init( self, data ):
		"""
		"""
		Spell.init( self, data )	
		self.moveSpeed = float( data["param1"] )
		self.time = float( data["param2"] )
		self.needEnergy = int( data["param3"] )
		
	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		if getCurrVehicleID( caster ): # 坐骑无法释放轻功技能
			return csstatus.SKILL_NO_MSG 
		if caster.energy < self.needEnergy : #判断跳跃能量值
			return csstatus.SKILL_NO_MSG 
		return Spell.useableCheck( self, caster, target )
		
	def cast( self, caster, target ) :
		"""
		virtual method
		"""
		caster.calEnergy( - self.needEnergy )
		if not caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			return
		else:
			caster.fallDownHeight = caster.position.y
			caster.move_speed = self.moveSpeed
			caster.updateTopSpeed()
			#计算可能会被碰撞，引起不会冲刺那么久
			yaw = caster.yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) ) 
			direction.normalise()
			dstPos = caster.position + direction * self.moveSpeed * self.time
			endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
			if ( endDstPos - dstPos ).length < 0.1:
				endDstPos = csarithmetic.getCollidePoint( caster.spaceID, Math.Vector3( endDstPos[0],endDstPos[1]+10,endDstPos[2]), Math.Vector3( endDstPos[0],endDstPos[1]-10,endDstPos[2]) )
			newTime = (endDstPos - caster.position).length / self.moveSpeed
			caster.addTimer( newTime, 0, ECBExtend.CHARGE_SPELL_CBID )
		Spell.cast( self, caster, target )

