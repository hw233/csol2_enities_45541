# -*- coding: gb18030 -*-
import BigWorld
from SpellBase import *
from Buff_Normal import Buff_Normal
from bwdebug import *
import csdefine
import csconst

class Buff_199027( Buff_Normal ):
	"""
	ʰȡ��������״̬

	�ڴ�״̬��ʱ��ֻ����ʹ�����Ҽ��ƶ�������������Ч
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self.decRewardValue = 0.0 #���ٽ���Ǳ�ܵ������

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self.decRewardValue = float( float( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0.0 ) )

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
		receiver.setTemp( "decRewardPotential", self.decRewardValue )

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
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.setTemp( "decRewardPotential", self.decRewardValue )

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
		receiver.removeTemp( "decRewardPotential" )