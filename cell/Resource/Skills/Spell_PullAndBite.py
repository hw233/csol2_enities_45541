# -*- coding:gb18030 -*-


import Math
import math
import csdefine
import csarithmetic
import ECBExtend
import csstatus
from Spell_BuffNormal import Spell_BuffNormal

class Spell_PullAndBite( Spell_BuffNormal ):
	"""
	������-ҧס����
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		# ������λ������
		self.targetMoveSpeed = 0.0
		#����ʩ���߾���
		self.disToCaster  = 2.0

	def init( self, data ):
		"""
		"""
		Spell_BuffNormal.init( self, data )
		self.disToCaster     = float( data["param1"] )
		self.targetMoveSpeed = float( data["param2"] )

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
		self.receiveLinkBuff( caster, receiver )
		# ������λ��
		#�����ǰĿ�괦�ڰ���״̬�����������λ��
		if receiver.effect_state & ( csdefine.EFFECT_STATE_HEGEMONY_BODY | csdefine.EFFECT_STATE_INVINCIBILITY | csdefine.EFFECT_STATE_FIX ) > 0:
			return
		dis = ( receiver.position - caster.position ).length
		if self.targetMoveSpeed and dis > self.disToCaster:
			yaw = ( caster.position - receiver.position ).yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			direction.normalise()
			dstPos = receiver.position + direction * ( dis - self.disToCaster )
			endDstPos = csarithmetic.getCollidePoint( receiver.spaceID, receiver.position, dstPos )
			endDstPos = csarithmetic.getCollidePoint( receiver.spaceID, Math.Vector3( endDstPos[0],endDstPos[1]+3,endDstPos[2]), Math.Vector3( endDstPos[0],endDstPos[1]-3,endDstPos[2]) )
			receiver.move_speed = self.targetMoveSpeed
			receiver.updateTopSpeed()
			timeData = (endDstPos - receiver.position).length/self.targetMoveSpeed
			receiver.addTimer( timeData, 0, ECBExtend.CHARGE_SPELL_CBID )
			if receiver.__class__.__name__ != "Role" :
				receiver.moveToPosFC( endDstPos, self.targetMoveSpeed, False )
		receiver.receiveSpell( caster.id, self.getID(), 0, 0, 0 )