# -*- coding: gb18030 -*-

from Function import Function

class FuncYXLMEquipTrade( Function ):

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ�����ܣ���������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.client.enterTradeWithNPC( talkEntity.id )
		player.endGossip( talkEntity )