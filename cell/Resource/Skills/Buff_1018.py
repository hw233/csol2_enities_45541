# -*- coding: gb18030 -*-
#
# $Id: Buff_1013.py,v 1.2 2007-12-13 04:59:55 zds Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_1018( Buff_Normal ):
	"""
	example:�����ɫ�г�ս��������ʩչһ�����ܣ�ʹ��4�����Ծ�����i%
	��Ϊ��ɫbuff�����÷�ʽ�ǣ����ϼ���Ƿ��г�ս���������ҳ�����ָ��buff��
	��ô��������ͷ�һ�����ܣ�ʹ����ָ��buff���ڱ�buff doEndʱ�����ս�����Ƿ����ָ��buff�����ڵĻ�����֮��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._skillID = 0
		self._buffID = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._skillID = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )
		self._buffID = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )

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
		receivePet = receiver.pcg_getActPet()
		if receivePet is None:
			return
			
		if receivePet.etype == "MAILBOX" :
			return
			
		petEntity = receivePet.entity
		if petEntity.findBuffsByBuffID( self._buffID ):
			return
		receiver.spellTarget( self._skillID, petEntity.id )

	def doLoop( self, receiver, buffData ):
		"""
		"""
		receivePet = receiver.pcg_getActPet()
		if receivePet is not None:
			if receivePet.etype != "MAILBOX" :
				petEntity = receivePet.entity
				if not petEntity.findBuffsByBuffID( self._buffID  ):
					receiver.spellTarget( self._skillID, petEntity.id )

		return Buff_Normal.doLoop( self, receiver, buffData )

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
		receivePet = receiver.pcg_getActPet()
		if receivePet is None:
			return
			
		petEntity = receivePet.entity
		if receivePet.etype == "MAILBOX":
			petEntity.remoteCall( "removeBuff", ( buffIndex[0], [csdefine.BUFF_INTERRUPT_NONE] ) )
			return
		buffIndex = petEntity.findBuffsByBuffID( self._buffID )
		if buffIndex:
			if petEntity.isReal():
				petEntity.removeBuff( buffIndex[0], [csdefine.BUFF_INTERRUPT_NONE] )
			else:
				petEntity.remoteCall( "removeBuff", ( buffIndex[0], [csdefine.BUFF_INTERRUPT_NONE] ) )
