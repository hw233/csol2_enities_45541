# -*- coding: gb18030 -*-

import BigWorld
from Buff_Normal import Buff_Normal

ELEM_MAPS = {0:"huo", 1:"xuan", 2:"lei", 3:"bing"}

class Buff_299039( Buff_Normal ):
	"""
	Ԫ�ع���Ч��buff�������ױ�
	"""
	def __init__( self ):
		"""
		���캯��
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
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )

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
		# ���Ԫ�ع���Ч��
		receiver.setTemp( "ELEM_ATTACK_EFFECT", ELEM_MAPS.get( self._p1, "" ) )

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
		# ���Ԫ�ع���Ч��
		receiver.setTemp( "ELEM_ATTACK_EFFECT", ELEM_MAPS.get( self._p1, "" ) )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		# ȥ��Ԫ�ع���Ч��
		receiver.removeTemp( "ELEM_ATTACK_EFFECT" )