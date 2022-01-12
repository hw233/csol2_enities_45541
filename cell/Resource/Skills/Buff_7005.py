# -*- coding: gb18030 -*-
#

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_7005( Buff_Normal ):
	"""
	�ָ�Ŀ�꣺�������������ٷֱ�
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
		self._p1 = float( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 ) / 100	# hp�İٷֱ�
		self._p2 = float( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 ) / 100	# mp�İٷֱ�
		
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
		if self._p1 > 0:
			hp_value = receiver.HP_Max * self._p1
			receiver.addHP( int( hp_value ) )
		if self._p2 > 0:
			mp_value = receiver.MP_Max * self._p2
			receiver.addMP( int( mp_value ) )

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
		if self._p1 > 0:
			hp_value = receiver.HP_Max * self._p1
			receiver.addHP( int( hp_value ) )
		if self._p2 > 0:
			mp_value = receiver.MP_Max * self._p2
			receiver.addMP( int( mp_value ) )

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
		if self._p1 > 0:
			hp_value = receiver.HP_Max * self._p1
			receiver.addHP( int( hp_value ) )
		if self._p2 > 0:
			mp_value = receiver.MP_Max * self._p2
			receiver.addMP( int( mp_value ) )
		return Buff_Normal.doLoop( self, receiver, buffData )
#