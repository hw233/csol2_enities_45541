# -*- coding: gb18030 -*-

import BigWorld
import Math
import csconst
import ECBExtend
from SkillTrap import SkillTrap
from bwdebug import *

class MoveTrap( SkillTrap ):
	"""
	���ƶ�������
	"""
	def __init__( self ):
		"""
		"""
		SkillTrap.__init__( self )
		self.dstPos = Math.Vector3()
		self.isSafe = True
		self.lifeTimer = 0

	def setDstPos( self, pos ):
		"""
		�����˶�����Ŀ���
		"""
		if not self.isReal():
			self.remoteCall( "setDstPos", ( pos ) )
		else:
			self.dstPos = Math.Vector3( pos )

	def setSafe( self, isSafe ):
		"""
		���������Ƿ���Ч
		"""
		if not self.isReal():
			self.remoteCall( "setSafe", ( isSafe ) )
		else:
			self.isSafe = isSafe

	def setLifeTime( self, lifeTime ):
		"""
		����������ʱ��
		"""
		if not self.isReal():
			self.remoteCall( "setLifeTime", ( lifeTime ) )
		else:
			# �������Timer
			self.lifetime = lifeTime
			self.lifeTimer = self.addTimer( lifeTime, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )

	def delayLineToPoint( self, delayTime ):
		"""
		�ӳ��˶�
		"""
		self.addTimer( delayTime, 0, ECBExtend.DELAY_LINE_TO_POINT_TIMER_CBID )

	def onDelayLineToPointTimer( self, timerID, cbID ):
		"""
		��ʼ�˶���Ŀ���
		"""
		self.setSafe( False ) 		# ��������Ϊ��Ч
		self.startEnterTrapDo()		# ����������
		self.planesAllClients( "moveToPosFC", ( self.dstPos, self.move_speed, True ) ) # �ͻ��˷��б���
		self.lineToPoint( self.dstPos, self.move_speed, True )		 # ���������б���

	def enterTrapDo( self, entity ):
		"""
		�����������
		"""
		if self.isSafe: return  # ���������Ч
		SkillTrap.enterTrapDo( self, entity )

	def leaveTrapDo( self, entity ):
		"""
		�뿪�������
		"""
		if self.isSafe: return	# ���������Ч
		SkillTrap.leaveTrapDo( self, entity )

	def onDestroySelfTimer( self, timerID, cbID ):
		"""
		virtual method.
		ɾ������
		"""
		self.delayDestroySelf()

	def delayDestroySelf( self ):
		"""
		�ӳ�����������Ҫ��entity�뿪����
		"""
		if self.isTrigger and self.lifeTimer > 0:	# ����ǰ����������
			self.cancel( self.lifeTimer )
			self.lifeTimer = 0
		self.planesAllClients( "onDestroy", () )	 # �ͻ��˱���
		self.setSafe( True )		 # ��Ϊ��Ч
		self.addTimer( csconst.MOVE_TRAP_DELAY_DESTROY_TIME, 0, ECBExtend.DELAY_DESTROY_SELF_TIMER_CBID )

	def onDelayDestroySelfTimer( self, timerID, cbID ):
		"""
		��ʽ��������
		"""
		self.destroy()

	def startEnterTrapDo( self ):
		"""
		�տ�ʼ�˶���ʱ������һ�ν��������⡣
		��ֹ���������Ŀ��պ��ںܽ���λ�ö�û���˺����������
		"""
		entities = self.entitiesInRangeExt( self.radius )
		for entity in entities:
			if abs( entity.position.y - self.position.y ) < self.radius:
				self.enterTrapDo( entity )
