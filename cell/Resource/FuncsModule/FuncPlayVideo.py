# -*- coding: gb18030 -*-

from bwdebug import *
from Function import Function
import csconst
import csstatus

class FuncPlayVideo( Function ):
	"""
	������Ƶ
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self._param1 = section.readString( "param1" )			#��Ƶ�ļ�����
		
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		�Ի�ѡ����Ч�Լ��
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		return True
		
	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		�����Ի�ѡ��Ҫ��������
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		#DEBUG_MSG( "-->>rlt_askForStartAlly" )
		player.endGossip( talkEntity )
		player.client.playVideo( self._param1 )
		
		