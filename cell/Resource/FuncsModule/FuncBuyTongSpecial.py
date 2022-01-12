# -*- coding: gb18030 -*-
#
from bwdebug import *
import csdefine
import csconst
import csstatus

class FuncBuyTongSpecial:
	"""
	购买帮会特殊商品
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass
		
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if talkEntity is None:
			return
		if player.tong_dbID != talkEntity.ownTongDBID:
			return
		player.client.onTradeWithTongSpecialChapman( talkEntity.id )
		player.endGossip( talkEntity )
		
	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True