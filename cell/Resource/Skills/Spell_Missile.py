# -*- coding: gb18030 -*-

import BigWorld
import Math
import math
import csarithmetic
from SpellBase import *

CIR_ANGLE = 360.0

class Spell_Missile( Spell):
	"""
	��������
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.radius = 0.0				# ���������뾶
		self.isDisposable = 0			# �Ƿ�һ���Ե�����������һ�ξ����٣�
		self.enterSpell = 0				# ��������ʩ�ŵļ���
		self.leaveSpell = 0				# �뿪����ʩ�ŵļ���
		self.modelNumber =  ""			# ������Ӧ��ģ��(����Ч��)
		self.modelScale = 1.0			# ����ģ�����ű���
		self.speed = 0.0				# �����ƶ��ٶ�
		self.distance = 0.0				# �������о���
		self.mount = 0					# ��������
		self.angle = CIR_ANGLE			# ��������Ƕ�
		self.offsetAngle = 0.0			# ��������ƫ�ƽǶ�
		self.delayTime = 0.0			# �����ӳ��˶�ʱ��

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		d1 = str( dict["param1"] ).split(";")
		if len( d1 ) >= 2:
			self.radius = float( d1[0] )
			self.isDisposable = int ( d1[1] )
		d2 = str( dict["param2"] ).split(";")
		if len( d2 ) >= 2:
			self.enterSpell = int( d2[0] )
			self.leaveSpell = int( d2[1] )
		d3 = str( dict["param3"] ).split(";")
		if len( d3 ) >= 2:
			self.modelNumber = str( d3[0] )
			self.modelScale = float( d3[1] )
		d4 = str( dict["param4"] ).split(";")
		if len( d4 ) >= 2:
			self.speed = float( d4[0] )
			self.distance = float( d4[1] )
			try:
				self.delayTime = float( d4[2] )
			except:
				self.delayTime = 0.0	# Ĭ�ϲ��ӳ�
		d5 = str( dict["param5"] ).split(";")
		if len( d5 ) >= 3:
			self.mount = int( d5[0] )
			self.angle = float( d5[1] )
			self.offsetAngle = float( d5[2] )

	def _getDict( self, caster, target ):
		"""
		"""
		dict = { "radius" : self.radius, \
			"enterSpell" : self.enterSpell, \
			"leaveSpell" : self.leaveSpell, \
			"originSkill" : self.getID(), \
			"modelNumber" : self.modelNumber, \
			"isDisposable" : self.isDisposable, \
			"lifetime" : 0, \
			"casterID" : caster.id, \
			"uname" : self.getName(), \
			"isSafe" : True  }  # ����տ�ʼ����Ĭ��Ϊ��Ч

		return dict

	def use( self, caster, target ):
		"""
		Ԥ������������entity
		"""
		pos = caster.position
		spaceID = caster.spaceID
		yaw = caster.yaw
		dir = caster.direction
		trapList = []
		for i in range( self.mount ):
			trap = caster.createEntityNearPlanes( "MoveTrap", pos, dir, self._getDict( caster, target ) )
			trap.position = pos						# ����������λ��
			trap.modelScale = self.modelScale		# ���õ���ģ�͵����ű���
			trap.move_speed = self.speed			# ���õ����ٶ�
			mount = float( self.mount )
			i = float( i )
			# ��������Ƕȵļ���
			# ����Ƕ� = ��ɫ��ǰ�Ƕ� + ��������ƫ�ƽǶ� + ��������Ƕ�/2 - ��������Ƕ�*ÿ��������ƫ�ƽǶȰٷֱ�
			if self.angle == CIR_ANGLE:		# ��������Ƕ�Ϊ360�ȵ��������
				y = yaw + (math.pi*2) * (self.offsetAngle/CIR_ANGLE) + (math.pi*2) * (i/mount)
			else:
				try:
					y = yaw + (math.pi*2) * (self.offsetAngle/CIR_ANGLE) + (math.pi*2) * (self.angle/(CIR_ANGLE*2.0)) - (math.pi*2) * (self.angle/CIR_ANGLE) * (i/(mount-1.0))
				except:		# ������������1�����
					y = yaw + (math.pi*2) * (self.offsetAngle/CIR_ANGLE)
			direction = Math.Vector3( math.sin( y ), 0, math.cos( y ) )
			direction.normalise()
			dstPos = pos + direction * self.distance
			endDstPos = csarithmetic.getCollidePoint( spaceID, pos, dstPos )	# ����ײ
			lifeTime = endDstPos.flatDistTo( pos ) / self.speed		# ���¼�����ʱ��
			lifeTime += self.getIntonateTime( caster )  # ����Ԥ����ʱ�䣨������ʱ�䣩
			lifeTime += self.delayTime	# �����ӳ��˶�ʱ��
			trap.setLifeTime( lifeTime )
			trap.setDstPos( endDstPos )
			trapList.append( trap )

		caster.setTemp( "MOVE_TRAP_LIST", trapList )
		Spell.use( self, caster, target )

	def cast( self, caster, target ):
		"""
		ʩ�ż��ܣ������ó�����
		"""
		Spell.cast( self, caster, target )  # �ͻ��˹�Ч��

		trapList = caster.queryTemp( "MOVE_TRAP_LIST", [] )
		for trap in trapList:
			trap.delayLineToPoint( self.delayTime )		# �ӳ��˶�

	def onSpellInterrupted( self, caster ):
		"""
		��ʩ�������ʱ��֪ͨ��
		��Ϻ���Ҫ��һЩ����,���ٵ���
		"""
		trapList = caster.queryTemp( "MOVE_TRAP_LIST", [] )
		for trap in trapList:
			trap.destroy()