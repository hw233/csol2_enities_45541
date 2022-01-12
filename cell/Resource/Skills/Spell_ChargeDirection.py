# -*- coding:gb18030 -*-
#edit by wuxo 2013-10-16

import Math
import math

import copy
import csstatus
import csdefine
import csarithmetic
import SkillTargetObjImpl
from Spell_PhysSkillImprove import Spell_PhysSkillImprove

class Spell_ChargeDirection( Spell_PhysSkillImprove ):
	"""
	����ʱ������淽�� ���޹���ʹ��
	"""
	def __init__( self ):
		"""
		"""
		Spell_PhysSkillImprove.__init__( self )
		#ʩ����λ������
		self.casterMoveSpeed    = 20.0   #����ٶ� 
		self.casterMoveDistance = 0.0	#��̾���

	def init( self, data ):
		"""
		"""
		Spell_PhysSkillImprove.init( self, data )
		param1 = data["param2"].split(";")
		if len( param1 ) >= 2:
			self.casterMoveSpeed = float( param1[0] )
			self.casterMoveDistance = float( param1[1] )

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
		dstPos = target.getObjectPosition()
		direction = dstPos - caster.position
		direction.normalise()
		caster.setTemp( "CHARGE_DIRECTION", direction )
		return Spell_PhysSkillImprove.useableCheck( self, caster, target )

	def cast( self, caster, target ) :
		"""
		virtual method
		"""
		# ʩ����λ��
		if self.casterMoveDistance and self.casterMoveSpeed:
			direction = caster.popTemp( "CHARGE_DIRECTION", None )
			if not direction:
				direction = Math.Vector3( math.sin(caster.yaw), 0.0, math.cos(caster.yaw) )
			dstPos = caster.position + direction * self.casterMoveDistance
			endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
			caster.moveToPosFC( endDstPos, self.casterMoveSpeed, True )
		Spell_PhysSkillImprove.cast( self, caster, target )
	
	def getReceivers( self, caster, target ):
		"""
		virtual method
		ȡ�����еķ���������������Entity�б�
		���е�onArrive()������Ӧ�õ��ô˷�������ȡ��Ч��entity��
		@return: array of Entity
		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		dstPos = caster.position
		target = SkillTargetObjImpl.createTargetObjPosition(dstPos)
		return Spell_PhysSkillImprove.getReceivers( self, caster, target )

class Spell_ChargeToPos( Spell_PhysSkillImprove ):
	"""
	����ʱ�������λ�� ���޹���ʹ��
	"""
	def __init__( self ):
		"""
		"""
		Spell_PhysSkillImprove.__init__( self )
		#ʩ����λ������
		self.casterMoveSpeed    = 20.0   #����ٶ�
		self.delayTime  = 0.5 #�ӳ��˺�ʱ��

	def init( self, data ):
		"""
		"""
		Spell_PhysSkillImprove.init( self, data )
		self.casterMoveSpeed = float( data["param2"] )

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
		state = Spell_PhysSkillImprove.useableCheck( self, caster, target )
		if state == csstatus.SKILL_GO_ON:
			if not target:
				dstPos = caster.position
			else:
				dstPos = target.getObjectPosition()
			caster.setTemp( "CHARGE_TARGET_POS", copy.deepcopy( dstPos ))
		return state

	def cast( self, caster, target ) :
		"""
		virtual method
		"""
		# ʩ����λ��
		if self.casterMoveSpeed:
			pos = caster.popTemp( "CHARGE_TARGET_POS", None )
			if not pos:
				pos = target.getObjectPosition()
			self.delayTime = ( pos - caster.position ).length / self.casterMoveSpeed
			caster.moveToPosFC( pos, self.casterMoveSpeed, True )
		Spell_PhysSkillImprove.cast( self, caster, target )
	
	def calcDelay( self, caster, target ):
		"""
		virtual method.
		ȡ���˺��ӳ�
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: float(��)
		"""
		return  self.delayTime
	
	def getReceivers( self, caster, target ):
		"""
		virtual method
		ȡ�����еķ���������������Entity�б�
		���е�onArrive()������Ӧ�õ��ô˷�������ȡ��Ч��entity��
		@return: array of Entity
		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		dstPos = caster.position
		target = SkillTargetObjImpl.createTargetObjPosition( dstPos )
		return Spell_PhysSkillImprove.getReceivers( self, caster, target )