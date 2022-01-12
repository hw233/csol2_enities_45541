# -*- coding: gb18030 -*-

"""
轻功系统-冲刺技能
"""
import Math
import math
import Const
import Define
import BigWorld
import csstatus
import csarithmetic
from bwdebug import *
from SpellBase import *
from gbref import rds

class Spell_Sprint( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.time  = 0.0
		self.moveSpeed = 0.0
		self.needEnergy = 0
		
	def init( self, data ):
		Spell.init( self, data )	
		self.moveSpeed = float( data["param1"] )
		self.time = float( data["param2"] )
		self.needEnergy = int( data["param3"] )
		
	def useableCheck( self, caster, target ):
		"""
		校验技能是否可以使用。
		"""
		if caster.energy < self.needEnergy : #判断跳跃能量值
			return csstatus.SKILL_NO_MSG 
		return Spell.useableCheck( self, caster, target)

	def cast( self, caster, targetObject ):
		"""
		"""
		Spell.cast( self, caster, targetObject )
		if  self.time > 0.0:
			yaw = caster.yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) ) 
			direction.normalise()
			dstPos = caster.position + direction * self.moveSpeed * self.time
			endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
			if ( endDstPos - dstPos ).length < 0.1:
				endDstPos = csarithmetic.getCollidePoint( caster.spaceID, Math.Vector3( endDstPos[0],endDstPos[1]+10,endDstPos[2]), Math.Vector3( endDstPos[0],endDstPos[1]-10,endDstPos[2]) )
			def __onMoveToDirectlyOver():
				if not caster.isJumpProcess:
					rds.actionMgr.playActions(caster.model, [Const.MODEL_ACTION_JUMP_END_STAND] )
				else:
					rds.actionMgr.playActions(caster.model, [Const.MODEL_ACTION_JUMP_AIR] )
				caster.isSprint = False
				caster.setArmCaps()
				if hasattr(caster,"physics"):
					caster.stopMove()
					caster.physics.fall = True
					caster.delBlurEffect()
				caster.removeControlForbid( Define.CONTROL_FORBID_ROLE_MOVE,Define.CONTROL_FORBID_ROLE_MOVE_SPRINT )
				rds.skillEffect.interrupt( caster )#光效中断
			caster.isSprint = True
			caster.setArmCaps()
			if hasattr(caster,"physics"):
				caster.physics.fall = False
				caster.addBlurEffect()
				caster.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE,Define.CONTROL_FORBID_ROLE_MOVE_SPRINT )
				caster.moveToDirectly( endDstPos )
			t = ( endDstPos - caster.position ).length / caster.move_speed
			BigWorld.callback( t, __onMoveToDirectlyOver )
