# -*- coding: gb18030 -*-
#
# ����Ѫ�����ޣ�ͬʱ���ӵ�����Ѫֵ 2009-08-06 SPF
#

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_1019( Buff_Normal ):
	"""
	example: hp_max
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
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  * 100
		self._p2 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / 100.0

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
		increaseHP = receiver.HP_Max * self._p2
		receiver.HP_Max_percent += self._p1
		receiver.calcHPMax()
		receiver.addHP( increaseHP )

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
		receiver.HP_Max_percent += self._p1

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
		receiver.HP_Max_percent -= self._p1
		receiver.calcHPMax()
		decreaseHP = 0 - receiver.HP_Max * self._p2
		if receiver.HP + decreaseHP <= 0:
			decreaseHP = 1 - receiver.HP
		if receiver.HP < receiver.HP_Max:
			receiver.addHP( decreaseHP )