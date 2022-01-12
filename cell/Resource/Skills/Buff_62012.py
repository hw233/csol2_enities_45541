# -*- coding: gb18030 -*-
#


import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_62012( Buff_Normal ):
	"""
	example: ���������50%���ܵ����˺����80%
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0	# �������ӳ�
		self._p2 = 0	# �����˺��ӳ�
		
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
		receiver.damage_min_percent += self._p1
		receiver.calcDamageMin()
		receiver.damage_max_percent += self._p1
		receiver.calcDamageMax()
		receiver.receive_damage_percent += self._p2
		receiver.receive_magic_damage_percent += self._p2
		
	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�����¼���
		
		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.damage_min_percent += self._p1
		receiver.calcDamageMin()
		receiver.damage_max_percent += self._p1
		receiver.calcDamageMax()
		receiver.receive_damage_percent += self._p2
		receiver.receive_magic_damage_percent += self._p2
		
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
		receiver.damage_min_percent += self._p1
		receiver.damage_max_percent += self._p1
		receiver.receive_damage_percent += self._p2
		receiver.receive_magic_damage_percent += self._p2
		
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
		receiver.damage_min_percent -= self._p1
		receiver.calcDamageMin()
		receiver.damage_max_percent -= self._p1
		receiver.calcDamageMax()
		receiver.receive_damage_percent -= self._p2
		receiver.receive_magic_damage_percent -= self._p2
