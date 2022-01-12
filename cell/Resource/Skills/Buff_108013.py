# -*- coding: gb18030 -*-
import BigWorld
from SpellBase import *
from Buff_Normal import Buff_Normal
from bwdebug import *
import csdefine
import csconst

class Buff_108013( Buff_Normal ):
	"""
	ʰȡ��������״̬

	�ڴ�״̬��ʱ��ֻ����ʹ�����Ҽ��ƶ�������������Ч
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
		receiver.changeState( csdefine.ENTITY_STATE_PICK_ANIMA )
		receiver.vehicleModelNum = 9110151

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
		receiver.changeState( csdefine.ENTITY_STATE_PICK_ANIMA )
		receiver.vehicleModelNum = 9110151

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
		if receiver.state != csdefine.ENTITY_STATE_PICK_ANIMA:
			return
			
		if receiver.state != csdefine.ENTITY_STATE_FREE:
			receiver.changeState( csdefine.ENTITY_STATE_FREE )
		
		receiver.vehicleModelNum = 0