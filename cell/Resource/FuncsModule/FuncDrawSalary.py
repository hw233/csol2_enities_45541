# -*- coding: gb18030 -*-
#
"""
领取俸禄
"""
from Function import Function
import BigWorld
import csconst

class FuncDrawSalary( Function ):
	"""
	领取俸禄
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section  )

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		tongMailbox = player.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.onRequireSalaryInfo( player.base, player.databaseID )
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
		return player.tong_dbID != 0
