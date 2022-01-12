# -*- coding: gb18030 -*-
#
# $Id: Buff_13007.py,v 1.2 2008-09-04 07:46:27 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_13009( Buff_Normal ):
	"""
	example:�����˺�����ٷֱ�/�����˺�����ٷֱȣ������ܹ�ʽ�еļӳ�λ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0 #�����˺�����ٷֱ�
		self._p2 = 0 #�����˺�����ٷֱ�
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  * 100	
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )  * 100	
		
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
		receiver.damage_derate_ratio_value += self._p1
		receiver.magic_damage_derate_ratio_value += self._p2
		receiver.calcDamageDerateRatio()
		receiver.calcMagicDamageDerateRatio()

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
		receiver.damage_derate_ratio_value += self._p1
		receiver.magic_damage_derate_ratio_value += self._p2
		
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
		receiver.damage_derate_ratio_value -= self._p1
		receiver.magic_damage_derate_ratio_value -= self._p2
		receiver.calcDamageDerateRatio()
		receiver.calcMagicDamageDerateRatio()
		
#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
# 
#