# -*- coding: gb18030 -*-
#
# $Id: Buff_1015.py,v 1.2 2007-12-13 04:59:55 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
from Function import newUID

class Buff_116001( Buff_Normal ):
	"""
	example:��ɫ���ڴ�DEBUFFʱ������ɵ��κ��˺����ɽ�ɫ����е�һ���ٷֱȣ�ʣ�ಿ�ֲ�����Ŀ��е���
			BUFF�Ĳ���Ϊ�ٷֱȡ��ڴ˼����У��˲���Ϊ100%��
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
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 ) * 100

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
		receiver.damage_share_percent += self._p1
		


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
		receiver.damage_share_percent -= self._p1
		


#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
#
#