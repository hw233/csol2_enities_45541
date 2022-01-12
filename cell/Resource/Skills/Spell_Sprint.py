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
	�Ṧϵͳ-��̼���
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
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		if getCurrVehicleID( caster ): # �����޷��ͷ��Ṧ����
			return csstatus.SKILL_NO_MSG 
		if caster.energy < self.needEnergy : #�ж���Ծ����ֵ
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
			#������ܻᱻ��ײ�����𲻻�����ô��
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

