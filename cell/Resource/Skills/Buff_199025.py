# -*- coding: gb18030 -*-

import BigWorld
from Buff_Normal import Buff_Normal

class Buff_199025( Buff_Normal ):
	"""
	��ֹ��Ӳ�����ħ����־��Ч��buff����xx���ڲ������ٴδ���������ħ��Ч��
	"""
	def __init__( self ):
		"""
		���캯��
		"""
		Buff_Normal.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )

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
		# ��ӽ�ֹ����Ҫ����ħ����־
		receiver.setTemp( "FORBID_NOT_NEED_MANA", True )

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
		# ��ӽ�ֹ����Ҫ����ħ����־
		receiver.setTemp( "FORBID_NOT_NEED_MANA", True )

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
		# ȥ����ֹ����Ҫ����ħ����־
		receiver.removeTemp( "FORBID_NOT_NEED_MANA" )
