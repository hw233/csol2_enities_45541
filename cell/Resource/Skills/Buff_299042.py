# -*- coding: gb18030 -*-

import BigWorld
from Buff_Normal import Buff_Normal
import csdefine

class Buff_299042( Buff_Normal ):
	"""
	�Ѻ���Ӫ�б�ר��buff��ֻ���ڹ������ҡ�����Թ����ҶԹ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._friendlyCamps = []

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		friendlyCamps = ( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else "" ).split( ";" )
		self._friendlyCamps = [int( i ) for i in friendlyCamps]

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
		if self._friendlyCamps:
			receiver.friendlyCamps = self._friendlyCamps
			for camp in self._friendlyCamps:
				receiver.addCombatRelationIns( csdefine.RELATION_DYNAMIC_COMBAT_CAMP_FRIEND, camp )

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
		if self._friendlyCamps:
			receiver.friendlyCamps = self._friendlyCamps
			for camp in self._friendlyCamps:
				receiver.addCombatRelationIns( csdefine.RELATION_DYNAMIC_COMBAT_CAMP_FRIEND, camp )

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
		receiver.friendlyCamps = [ receiver.getCamp() ]
		for camp in self._friendlyCamps:
			receiver.removeCombatRelationIns( csdefine.RELATION_DYNAMIC_COMBAT_CAMP_FRIEND, camp )
