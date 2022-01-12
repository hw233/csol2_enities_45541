# -*- coding: gb18030 -*-
#
# $Id: Buff_1003.py,v 1.2 2007-12-13 04:59:55 huangyongwei Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_22100( Buff_Normal ):
	"""
	�չ�ԡ��ʹ����ˬ����ʹ�þ��鷭��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
						# ʹ����������ܹ����ı���( ������˫������1.5�� )
		self._p1 = 1.0	# Ĭ��Ϊ1�����飬Ҳ���ǲ�����
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = float( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0.0 ) 		# �����ٱ�
		if self._p1 == 0.0:
			self._p1 = 1.0
		
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
		receiver.setTemp( "has_cleanlily_drink", 1 )		# ���ñ�Ǳ�ʾ���ʹ������ˬ����
		receiver.setTemp( "drink_exp_rate", self._p1 )		# ���ñ�Ǳ�ʾ��ˬ�����ܷ��ı���
	
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
		receiver.setTemp( "has_cleanlily_drink", 1 )		# ���ñ�Ǳ�ʾ���ʹ������ˬ����
		receiver.setTemp( "drink_exp_rate", self._p1 )		# ���ñ�Ǳ�ʾ��ˬ�����ܷ��ı���
		
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
		receiver.removeTemp( "has_cleanlily_drink" )		# �����ʾ
		receiver.removeTemp( "drink_exp_rate" )