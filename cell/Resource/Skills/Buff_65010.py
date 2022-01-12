# -*- coding: gb18030 -*-
#
from bwdebug import *
from Buff_Normal import Buff_Normal
import csconst

class Buff_65010( Buff_Normal ):
	"""
	�ӱ���������buff
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._param1 = 0
		self._param2 = 0
		self._param3 = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		if dict["Param1"] != "":
			self._param1 = int( float( dict["Param1"] )* csconst.FLOAT_ZIP_PERCENT ) # ���������ʼ�%
		if dict["Param2"] != "":
			self._param2 = int( float( dict["Param2"] )* csconst.FLOAT_ZIP_PERCENT ) # �����������ʼ�%
		if  dict["Param3"] != "":
			self._param3 = int( float( dict["Param3"] )* csconst.FLOAT_ZIP_PERCENT ) # ���ܼ��ʼ�%

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
		receiver.double_hit_probability_percent += self._param1
		receiver.calcDoubleHitProbability()
		receiver.magic_double_hit_probability_percent += self._param2
		receiver.calcMagicDoubleHitProbability()
		receiver.dodge_probability_percent += self._param3
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
		receiver.double_hit_probability_percent += self._param1
		receiver.magic_double_hit_probability_percent += self._param2
		receiver.dodge_probability_percent += self._param3

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
		receiver.double_hit_probability_percent -= self._param1
		receiver.calcDoubleHitProbability()
		receiver.magic_double_hit_probability_percent -= self._param2
		receiver.calcMagicDoubleHitProbability()
		receiver.dodge_probability_percent -= self._param3
		receiver.calcDodgeProbability()