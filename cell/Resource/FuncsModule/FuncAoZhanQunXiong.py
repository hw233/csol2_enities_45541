# -*- coding: gb18030 -*-

import csstatus
import csconst
import BigWorld
from Function import Function

from FuncTeleport import FuncTeleport

class FuncAoZhanSignUp( Function ):
	"""
	鏖战群雄报名
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._minLevel = section.readInt( "param1" )	# 报名的车轮战城市
		
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
		if player.level < self._minLevel:
			player.statusMessage( csstatus.AO_ZHAN_QUN_XIONG_JOIN_MIN_LEVEL, player.level )
			return
		
		
		BigWorld.globalData[ "AoZhanQunXiongMgr" ].getSignUpList( player.base )


class FuncAoZhanEnter( FuncTeleport ):
	"""
	鏖战群雄进入
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		FuncTeleport.__init__( self, section )
	
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		FuncTeleport.do( self, player, talkEntity )