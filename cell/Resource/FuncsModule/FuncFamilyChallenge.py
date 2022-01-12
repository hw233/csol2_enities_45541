# -*- coding: gb18030 -*-
#
#$Id:$

import BigWorld
from bwdebug import *

class FuncFamilyChallenge:
	"""
	家族挑战
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
			WARNING_MSG( "talkEntity cannot be None." )
			return
		player.client.family_askForChallenge( talkEntity.id )
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




#$Log:$
#
# 