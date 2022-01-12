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
	�ű�����-��漼��
	"""
	def __init__( self ):
		"""
		"""
		Spell_PhysSkillImprove.__init__( self )
		# ������λ������
		self.targetMoveSpeed = 0.0	#�����ٶ�
		self.targetMoveDistance = 0.0		#���˾���
		#ʩ����λ������
		self.casterMoveDistance = 0.0	#��̾���
		self.casterMoveSpeed    = 0.0	#����ٶ�
		self.casterMoveFace     = False  #��̷�����ͷ��߳����Ƿ�һ��

		self.chargeDirection    = None	#��̷���


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
		# ʩ����λ��
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
		���ÿһ�������߽�����������������˺����ı����Եȵȡ�ͨ������´˽ӿ�����onArrive()���ã�
		�������п�����SpellUnit::receiveOnreal()�������ã����ڴ���һЩ��Ҫ�������ߵ�real entity�����������顣
		�������Ƿ���Ҫ��real entity���Ͻ��գ��ɼ����������receive()�������жϣ������ṩ��ػ��ơ�
		ע���˽ӿ�Ϊ�ɰ��е�onReceive()

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		if caster.isReal():
			Spell_PhysSkillImprove.receive( self, caster, receiver )

		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return


		# ������λ��
		#�����ǰĿ�괦�ڰ���״̬��������λ��
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

