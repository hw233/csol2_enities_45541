# -*- coding: gb18030 -*-

from Function import Function
from bwdebug import *


class FuncTongFeteExchange( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		@param section: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  section: pyDataSection
		"""
		Function.__init__( self, section )
		
		
	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if talkEntity is None:
			WARNING_MSG( "talkEntity cannot be None." )
			return
		player.client.tong_feteExchange( talkEntity.id )
		player.endGossip( talkEntity )
		
		
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
		return True