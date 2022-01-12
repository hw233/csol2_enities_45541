# -*- coding: gb18030 -*-
#
# $Id: Buff_addElementProp.py,v 1.0 9:56 2010-4-7 jiangyi Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_1113( Buff_Normal ):
	"""
	example:����Ŀ��Ԫ������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._elementVal = 0		# ���Լ�ֵ
		self._elementType = 0	# ����ֵ��

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._elementVal = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )
		self._elementType = str( dict[ "Param2" ] )

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
		if hasattr( receiver, self._elementType ):
			eleProp = getattr( receiver, self._elementType )
			eleProp += self._elementVal
			setattr( receiver, self._elementType, eleProp )
			receiver.calcDynamicProperties()


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
		if hasattr( receiver, self._elementType ):
			eleProp = getattr( receiver, self._elementType )
			eleProp += self._elementVal
			setattr( receiver, self._elementType, eleProp )

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
		if hasattr( receiver, self._elementType ):
			eleProp = getattr( receiver, self._elementType )
			eleProp -= self._elementVal
			setattr( receiver, self._elementType, eleProp )
			receiver.calcDynamicProperties()