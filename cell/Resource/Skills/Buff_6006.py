# -*- coding: gb18030 -*-
#
# $Id: Buff_6006.py,v 1.2 2008-09-05 09:28:15 yangkai Exp $

"""
������Ч��
"""

from Buff_Normal import Buff_Normal

class Buff_6006( Buff_Normal ):
	"""
	���װ����ͷר��buff
	example:�ƶ��ٶ����%
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / 100.0

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
		if receiver.vehicle and not receiver.vehicle.isDestroyed:
			receiver.vehicle.setMoveSpeed( receiver.vehicle.move_speed + receiver.move_speed * self._p1 )

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
		if receiver.vehicle and not receiver.vehicle.isDestroyed:
			receiver.vehicle.setMoveSpeed( receiver.vehicle.move_speed - receiver.move_speed * self._p1 )

# $Log: not supported by cvs2svn $
# Revision 1.1  2008/09/04 06:44:11  yangkai
# ��ͷר��buff
#