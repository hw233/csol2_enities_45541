# -*- coding: gb18030 -*-

import BigWorld
from SpellBase import *
from Buff_Normal import Buff_Normal
from bwdebug import *
import csdefine
import csconst


class Buff_99005( Buff_Normal ):
	"""
	δ��״̬buff

	�ڴ�״̬��ʱ���޷��ƶ����޷�ʹ���κε���/���ܡ����ܹ�����ͬʱҲ���ܵ��κι������˺���
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
		receiver.changeState( csdefine.ENTITY_STATE_PENDING )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			actPet = receiver.pcg_getActPet()
			if actPet : 											# �������г�ս����
				actPet.entity.changeState( csdefine.ENTITY_STATE_PENDING )

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
		receiver.changeState( csdefine.ENTITY_STATE_PENDING )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			actPet = receiver.pcg_getActPet()
			if actPet : 											# �������г�ս����
				actPet.entity.changeState( csdefine.ENTITY_STATE_PENDING )

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
		if receiver.state != csdefine.ENTITY_STATE_PENDING:
			return
		if receiver.state != csdefine.ENTITY_STATE_FREE:
			receiver.changeState( csdefine.ENTITY_STATE_FREE )

		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			actPet = receiver.pcg_getActPet()
			if actPet : 										# �������г�ս����
				actPet.entity.changeState( csdefine.ENTITY_STATE_FREE )

		es = receiver.entitiesInRangeExt( 15.0, None, receiver.position )
		for e in es:
			if not hasattr( e, "triggerTrap" ):
				continue

			if e.initiativeRange > 0:
				range = receiver.position.flatDistTo( e.position )
				if e.initiativeRange >= range:
					e.triggerTrap( receiver.id, range )