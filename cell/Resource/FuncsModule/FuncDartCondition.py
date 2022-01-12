# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
"""
from Function import Function
import csdefine

class FuncDartCondition( Function ):
	"""
	运镖条件对话
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._presitigeID = section.readInt( "param1" )		
		self._presitige = section.readInt( "param2" )
		levelCondition = section.readString( "param3" )
		self._preTalk  = section.readInt( "param4" )
		self._levelTalk  = section.readInt( "param5" )
		
		self._minLevel = int( levelCondition.split(':')[0] )
		self._maxLevel = int( levelCondition.split(':')[1] )

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
		if player.getPrestige( self._presitigeID ) > self._presitige:
			player.setGossipText( self._preTalk )
			player.sendGossipComplete( talkEntity.id )
		elif player.level < self._minLevel and player.level > self._maxLevel:
			player.setGossipText( self._levelTalk )
			player.sendGossipComplete( talkEntity.id )
		return False

