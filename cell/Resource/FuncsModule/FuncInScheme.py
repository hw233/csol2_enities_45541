# -*- coding: gb18030 -*-

"""
"""
from Function import Function
import csdefine
import csstatus
import Language
import time
import BigWorld
from CrondScheme import *


class FuncInScheme( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		"""
		if section:
			self._onSchemeTalkInfo   = section.readString( "param1" ).split("|")			#����ָ��ʱ����г��ֵĶԻ� ( key | ���� | ���� ��
			self._outSchemeTalkInfo  = section.readString( "param2" ).split("|")			#������ָ��ʱ����г��ֵĶԻ� ( key | ���� | ���� ��
			self._cmd			 = section.readString( "param3" )							#�ƻ��ַ��� �磺" * * 3 * *" (�μ� CrondScheme.py)
			self._presistMinute	 = section.readInt( "param4" )								#����ʱ��
			
			self.scheme = Scheme()
			self.scheme.init( self._cmd )
		
		
	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		pass
		#player.endGossip( talkEntity )


	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		year, month, day, hour, minute = time.localtime( time.time() - self._presistMinute * 60 )[:5]
		nextTime = self.scheme.calculateNext( year, month, day, hour, minute )
		if nextTime < time.time():
			player.addGossipOption( self._onSchemeTalkInfo[0], self._onSchemeTalkInfo[1], int( self._onSchemeTalkInfo[2] ) )
		else:
			player.addGossipOption( self._outSchemeTalkInfo[0], self._outSchemeTalkInfo[1], int( self._outSchemeTalkInfo[2] ) )
		return True


