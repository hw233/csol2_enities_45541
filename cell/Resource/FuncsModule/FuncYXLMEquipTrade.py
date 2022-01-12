# -*- coding: gb18030 -*-

from Function import Function

class FuncYXLMEquipTrade( Function ):

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能，必须重载

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.client.enterTradeWithNPC( talkEntity.id )
		player.endGossip( talkEntity )