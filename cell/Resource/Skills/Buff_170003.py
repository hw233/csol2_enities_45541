# -*- coding: gb18030 -*-
#
from bwdebug import *
from Buff_Normal import Buff_Normal
import csconst

class Buff_170003( Buff_Normal ):
	"""
	����BUFF
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self.param1 = 0
		self.param2 = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self.param1 = int( float( dict["Param1"] )* csconst.FLOAT_ZIP_PERCENT )			# ����������������%
		self.param2 = int( float( dict["Param2"] )* csconst.FLOAT_ZIP_PERCENT )			# ������������������%

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
		receiver.be_double_hit_probability += self.param1
		receiver.be_magic_double_hit_probability += self.param2

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
		receiver.be_double_hit_probability -= self.param1
		receiver.be_magic_double_hit_probability -= self.param2
