# -*- coding: gb18030 -*-
#
# $Id: Buff_107007.py,v 1.2 2008-02-13 08:41:04 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal


class Buff_107007( Buff_Normal ):
	"""
	example:ʧȥ����ֵ%	DEBUFF	��������ʧ����	��һ����ֵ����ʧȥ������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0 # ������MPֵ 

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		
		Buff_Normal.init( self, dict )
		self._p1 = int( (int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 ) /100.0) / ( self._persistent / self._loopSpeed ) )	
			
	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		����buff����ʾbuff��ÿһ������ʱӦ����ʲô��

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL�������������򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		SkillMessage.buff_ConsumeMP( buffData, receiver, receiver.MP_Max * self._p1 )
		receiver.setMP( receiver.MP - receiver.MP_Max * self._p1 )
		return Buff_Normal.doLoop( self, receiver, buffData )

#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
# 
#