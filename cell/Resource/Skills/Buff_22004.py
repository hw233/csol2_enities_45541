# -*- coding: gb18030 -*-
#
# $Id: Buff_22004.py,v 1.2 2008-05-19 08:01:12 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_22004( Buff_Normal ):
	"""
	example:Ԫ�����	��ɫ���Ի�õľ����Ǳ������%i%%��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = ( int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / 100.0 )

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
		receiver.potential_percent += self._p1
		receiver.multExp += self._p1

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		receiver.potential_percent -= self._p1
		receiver.multExp += self._p1
		Buff_Normal.doEnd( self, receiver, buffData )

#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/05/19 07:23:18  kebiao
# no message
#
#
#