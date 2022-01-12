# -*- coding: gb18030 -*-

import csstatus

class FuncOpenTongDartQuest:
	"""
	开启帮会运镖任务
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
		player.endGossip( talkEntity )
		if not player.isTongChief():
			player.statusMessage( csstatus.TONG_OPEN_TONG_QUEST_REQUEST_CHIEF )
			return
		tongBase = player.tong_getSelfTongEntity()
		if tongBase:
			tongBase.openTongDartQuest( player.base )
	
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

class FuncOpenTongNormalQuest:
	"""
	开启帮会日常任务
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.type = section['param1'].asInt
		
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if not player.isTongChief():
			player.statusMessage( csstatus.TONG_OPEN_TONG_QUEST_REQUEST_CHIEF )
			return
		tongBase = player.tong_getSelfTongEntity()
		if tongBase:
			tongBase.openTongNormalQuest( player.base, self.type )
	
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