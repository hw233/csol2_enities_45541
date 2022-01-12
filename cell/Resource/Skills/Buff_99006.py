# -*- coding: gb18030 -*-


from SpellBase import *
from Buff_Normal import Buff_Normal

from bwdebug import *
import csdefine
import csconst


class Buff_99006( Buff_Normal ):
	"""
	Ǳ�ܼ���	ɱ��Ǳ�ܸ����еĹ����õ�Ǳ�����n%��
	"""
	def __init__( self ):
		"""
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


	def doReload( self, receiver, buffData ):
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
		receiver.potential_percent -= self._p1