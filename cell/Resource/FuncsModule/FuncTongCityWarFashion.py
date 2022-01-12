# -*- coding: gb18030 -*-
"""
帮会城战时装奖励对话 11:27 2010-12-21 by 姜毅
"""
import BigWorld
import csdefine
import csstatus
from Function import Function

class FuncTongCityWarFashionMember( Function ):
	"""
	帮会城战时装奖励 成员
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.sendGossipComplete( talkEntity.id )
		Function.do( self, player, talkEntity )
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
		if player.tong_dbID <= 0:
			return False
		if player.tong_holdCity == "":
			return False
		return True
		
class FuncTongCityWarFashionChairman( Function ):
	"""
	帮会城战时装奖励 帮主
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.sendGossipComplete( talkEntity.id )
		Function.do( self, player, talkEntity )
		player.endGossip( talkEntity )
		
		player.factionCount -= 1
		player.base.setTongFactionCount( player.factionCount )

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
		if player.tong_dbID <= 0:
			return False
		if not player.isTongChief():
			return False
		if player.tong_holdCity == "":
			return False
		if player.factionCount < 1:
			return False
		return True