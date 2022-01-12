# -*- coding: gb18030 -*-
#
# $Id: FuncQueryFamilyNPC.py,v 1.2 2008-07-19 03:53:07 kebiao Exp $

"""
"""
from Function import Function
import BigWorld
import csconst

class FuncQueryTongMoney( Function ):
	"""
	查询帮会各种资金
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
		# 暂时只能从base上获得建筑的维修费用，其它的资金客户端可以自己找到
		tongMailbox = player.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.onRequestBuildingSpendMoney( player.base )
		player.endGossip( talkEntity )
		return
	
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
		
		return player.tong_dbID != 0