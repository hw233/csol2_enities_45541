# -*- coding: gb18030 -*-

from SpellBase import *
from Buff_Normal import Buff_Normal
from bwdebug import *
import Const

class Buff_22138( Buff_Normal ):
	"""
	����λ�棬ͨ��buff��������ҽ���λ��ʱtopSpeed�ı仯ʱ��
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )

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
		receiver.setTopSpeed( Const.TELEPORT_PLANE_TOPSPEED_LIMIT )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		receiver.updateTopSpeed()
		Buff_Normal.doEnd( self, receiver, buffData )
		