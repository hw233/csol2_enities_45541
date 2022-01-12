# -*- coding:gb18030 -*-

import BigWorld
import Math
import math
import csdefine
import csarithmetic
from Spell_BuffNormal import Spell_BuffNormal
import ECBExtend
from Domain_Fight import g_fightMgr

class Spell_GroupPush( Spell_BuffNormal ):
	"""
	Ⱥ��λ��
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )

		# ʩ����λ������
		self.casterMoveSpeed = 0.0
		self.casterMoveDistance = 0.0
		# ������λ������
		self.targetMoveSpeed = 0.0
		self.targetMoveDistance = 0.0

		self.param1 = 0
		self.param2 = 0

	def init( self, data ):
		"""
		"""
		Spell_BuffNormal.init( self, data )

		param1 = data["param1"].split(";")
		self.param1= len( param1 )
		if self.param1 >= 2:
			self.casterMoveSpeed = float( param1[0] )
			self.casterMoveDistance = float( param1[1] )
		param2 = data["param2"].split(";")
		self.param2 = len( param2 )
		if self.param2 >= 2:
			self.targetMoveSpeed = float( param2[0] )
			self.targetMoveDistance = float( param2[1] )

	def cast( self, caster, target ) :
		"""
		virtual method
		ϵͳʩ�ţ�û�������壬���Զ���˲��
		"""
		# ʩ����λ��
		targetObject = target.getObject()
		if self.casterMoveDistance == 0.0:
			yaw = targetObject.yaw
			dstPos = targetObject.position - Math.Vector3( math.sin(yaw), 0, math.cos(yaw) ) * targetObject.distanceBB( targetObject )
		else:
			direction = Math.Vector3( targetObject.position ) - Math.Vector3( caster.position )
			direction.normalise()
			if direction == Math.Vector3():    #ʩ�����������߸պ���һ��λ��
				yaw = caster.yaw
				direction = direction - ( Math.Vector3( math.sin(yaw), 0, math.cos(yaw) ) )
			dstPos = caster.position + direction * self.casterMoveDistance
		endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
		if self.param1 >=2:
			if self.casterMoveSpeed:
				if caster.__class__.__name__ != "Role":
					caster.moveToPosFC( endDstPos, self.casterMoveSpeed, False )
				else:
					caster.move_speed = self.casterMoveSpeed
					caster.updateTopSpeed()
					timeData = ( endDstPos - caster.position ).length/self.casterMoveSpeed
					caster.addTimer( timeData, 0, ECBExtend.CHARGE_SPELL_CBID )
			else:   # �ٶ�Ϊ����Ϊ˲��
				caster.position = endDstPos

		Spell_BuffNormal.cast( self, caster, target )

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
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		receiver.receiveSpell( caster.id, self.getID(), 0, 0, 0 )
		g_fightMgr.buildEnemyRelation( receiver, caster )

		Spell_BuffNormal.receive( self, caster, receiver )

		#�����ǰĿ�괦�ڰ���״̬�����������λ��
		if receiver.effect_state & ( csdefine.EFFECT_STATE_HEGEMONY_BODY | csdefine.EFFECT_STATE_INVINCIBILITY | csdefine.EFFECT_STATE_FIX ) > 0:
			return

		if self.param2 < 2: return
		# ������λ��
		if self.targetMoveDistance == 0.0:
			yaw = caster.yaw
			dstPos = caster.position - Math.Vector3( math.sin(yaw), 0, math.cos(yaw) ) * caster.distanceBB( caster )
		else:
			yaw = caster.yaw
			direction = Math.Vector3( math.sin(yaw), 0, math.cos(yaw) )
			direction.normalise()
			dstPos = receiver.position + direction * self.targetMoveDistance
		endDstPos = csarithmetic.getCollidePoint( receiver.spaceID, receiver.position, dstPos )
		if ( endDstPos - dstPos ).length < 0.1:
			endDstPos = csarithmetic.getCollidePoint( receiver.spaceID, endDstPos, Math.Vector3( endDstPos[0],endDstPos[1]-self.targetMoveDistance,endDstPos[2]) )
		if self.targetMoveDistance <= 0.0 and not receiver.hasFlag( csdefine.ENTITY_FLAG_CANT_ROTATE_IN_FIGHT_STATE ):
			receiver.rotateToPos( caster.position )
		receiver.moveToPosFC( endDstPos, self.targetMoveSpeed, False )
