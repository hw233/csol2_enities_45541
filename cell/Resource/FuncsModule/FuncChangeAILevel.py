# -*- coding: gb18030 -*-
# create by TangHui


"""
"""
from Function import Function
import csdefine
import BigWorld
import time
import csstatus


class FuncChangeAILevel( Function ):
	"""
	对话改变AI等级
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.AIlevel = section.readInt( "param1" )										#AI 等级


	def do( self, player, talkEntity = None ):
		"""
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )

		talkEntity.setDefaultAILevel( self.AIlevel )
		talkEntity.setNextRunAILevel( self.AIlevel )
		talkEntity.setTemp( "talkPlayerID",player.id )

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
