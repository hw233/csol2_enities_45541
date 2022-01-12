# -*- coding: gb18030 -*-

"""
Spell�����ࡣ
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import csarithmetic
import Math
import math
from gbref import rds

class Spell_GroupPush( Spell ):
	"""
	Ⱥ��λ��
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

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
		��ȡ����
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, data )

		param1 = data["param1"].split(";")
		self.param1 = len( param1 )
		if self.param1 >= 2:
			self.casterMoveSpeed = float( param1[0] )
			self.casterMoveDistance = float( param1[1] )
		param2 = data["param2"].split(";")
		self.param2 = len( param2 )
		if self.param2 >= 2:
			self.targetMoveSpeed = float( param2[0] )
			self.targetMoveDistance = float( param2[1] )

	def cast( self, caster, targetObject ):
		"""
		virtual method
		ϵͳʩ�ţ�û�������壬���Զ���˲��
		"""
		Spell.cast( self, caster, targetObject )

		target = targetObject.getObject()
		# ʩ����λ��
		if self.casterMoveDistance == 0.0:
			yaw = target.yaw
			dstPos = target.position - Math.Vector3( math.sin(yaw), 0, math.cos(yaw) ) * target.distanceBB( target )
		else:
			direction = Math.Vector3( target.position ) - Math.Vector3( caster.position )
			direction.normalise()
			if direction == Math.Vector3():    #ʩ�����������߸պ���һ��λ��
				yaw = caster.yaw
				direction = direction - ( Math.Vector3( math.sin(yaw), 0, math.cos(yaw) ) )
			dstPos = caster.position + direction * self.casterMoveDistance
		endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
		if self.casterMoveSpeed and self.param1 >= 2:
			if caster == BigWorld.player():
				def __onMoveOver( success ):
					caster.stopMove()
					if not  success:
						DEBUG_MSG( "player move is failed." )
					rds.skillEffect.interrupt( caster )#��Ч�ж�
				caster.moveToDirectly( endDstPos, __onMoveOver )

	def receiveSpell( self, target, casterID, damageType, damage  ):
		"""
		���ܼ��ܴ���

		@type   casterID: OBJECT_ID
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		player = BigWorld.player()
		caster = None
		if casterID:
			try:
				caster = BigWorld.entities[casterID]
			except KeyError:
				#�����������ԭ���� �ڷ�������һ��entity����һ��entityʩ�� ���������ǿ��ĵ�ʩ���ߵ�
				#���ͻ��˿��ܻ���Ϊĳԭ�� �磺�����ӳ� ���ڱ���û�и��µ�AOI�е��Ǹ�ʩ����entity����
				#��������ִ��� written by kebiao.  2008.1.8
				return

		# ������Ч����
		self._skillAE( player, target, caster, damageType, damage  )
