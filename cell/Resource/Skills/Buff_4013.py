# -*- coding: gb18030 -*-

import BigWorld
import csconst
import csdefine
import csstatus
from bwdebug import *
from Buff_Normal import Buff_Normal

class Buff_4013( Buff_Normal ):
	"""
	�ò�BUFF
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
		#�� = ( ����/1800.0)/( ��ɫ��ǰ�ȼ�/92.0) )
		value = ( self._p1/1800.0)/( receiver.level/92.0 ) * csconst.FLOAT_ZIP_PERCENT
		receiver.dodge_probability_value += value
		receiver.calcDodgeProbability()

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
		value = ( self._p1/1800.0)/( receiver.level/92.0 ) * csconst.FLOAT_ZIP_PERCENT
		receiver.dodge_probability_value += value

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
		value = ( self._p1/1800.0)/( receiver.level/92.0 ) * csconst.FLOAT_ZIP_PERCENT
		receiver.dodge_probability_value -= value
		receiver.calcDodgeProbability()
