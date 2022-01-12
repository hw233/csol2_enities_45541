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
	��������
	"""
	def __init__( self ):
		"""
		"""
		Spell_CertainBuffNormal.__init__( self )
		#ʩ����λ������
		self.moveDistance = 0.0	#�ƶ�����
		self.moveSpeed    = 0.0	#�ƶ��ٶ�
		self.casterMoveDistance = 0.0 # ʩ�����ƶ��ľ���
		self.casterMoveSpeed = 0.0	# ʩ�����ƶ����ٶ�


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
		ȡ���˺��ӳ�
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: float(��)
		"""
		return  0.7

	def cast( self, caster, target ):
		"""
		virtual method.
		��ʽ��һ��Ŀ���λ��ʩ�ţ���з��䣩�������˽ӿ�ͨ��ֱ�ӣ����ӣ���intonate()�������á�

		ע���˽ӿڼ�ԭ���ɰ��е�castSpell()�ӿ�

		@param     caster: ʹ�ü��ܵ�ʵ��
		@type      caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		# ʩ����λ��
		Spell_CertainBuffNormal.cast( self, caster, target )
		caster.clearBuff( self._triggerBuffInterruptCode ) #�ж�buff
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
		����������Ҫ��������
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

		# ������λ��
		#�����ǰĿ�괦�ڰ���״̬�����������λ��
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