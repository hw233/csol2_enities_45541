# -*- coding: gb18030 -*-

import BigWorld
import csdefine
from Buff_Normal import Buff_Normal


class Buff_108010( Buff_Normal ):
	"""
	example:��ֱ
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self.targetMoveSpeed = 6.0
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		if dict["Param1"]:
			self.targetMoveSpeed = float( dict["Param1"] )  # λ���ٶ�

	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч����ʼ�Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		# ִ�и���Ч��
		receiver.move_speed = self.targetMoveSpeed
		receiver.updateTopSpeed()


	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�����¼��صĴ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		# ִ�и���Ч��
		receiver.move_speed = self.targetMoveSpeed
		receiver.updateTopSpeed()

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.calcMoveSpeed()
		receiver.updateTopSpeed()

