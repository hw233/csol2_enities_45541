# -*- coding: gb18030 -*-

from Spell_PhysSkillImprove import Spell_PhysSkillImprove
import BigWorld
import Math
import math
import csstatus
import csarithmetic

"""
向目标后背闪烁移动并造成伤害
"""
class Spell_Backstab( Spell_PhysSkillImprove ):
	def __init__( self ):
		"""
		"""
		Spell_PhysSkillImprove.__init__( self )
	
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
		skillPos = self.calcSkillPos( caster, target )
		if csarithmetic.checkSkillCollide( caster.spaceID, caster.position, skillPos ) != None:
			return csstatus.SKILL_CANT_ARRIVAL
		return Spell_PhysSkillImprove.useableCheck( self, caster, target )
	
	def calcSkillPos( self, caster, target ):
		"""
		"""
		targetEntity = target.getObject()
		pos = target.getObjectPosition()
		yaw = target.getObject().yaw
		distPos = pos + Math.Vector3(math.sin(yaw),0,math.cos(yaw))* ( targetEntity.distanceBB(targetEntity) + caster.distanceBB(caster) )
		return distPos
		
	def cast( self, caster, target ):
		"""
		"""
		targetEntity = target.getObject()
		Spell_PhysSkillImprove.cast( self, caster, target )
		skillPos = self.calcSkillPos( caster, target )
		endDstPos = csarithmetic.getCollidePoint( caster.spaceID, skillPos , skillPos + Math.Vector3(0.0,targetEntity.distanceBB(targetEntity),0.0) )
		caster.teleport( None, endDstPos, (0,0,target.getObject().yaw))
		caster.planesAllClients( "unifyYaw", () )
		