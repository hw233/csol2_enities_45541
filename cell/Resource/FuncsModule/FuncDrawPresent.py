# -*- coding: gb18030 -*-
#
# $Id: FuncDrawPresent.py,v 1.11 2008-01-15 06:06:34 phw Exp $

"""
"""
from Function import Function
import BigWorld
import csconst

class FuncDrawPresent( Function ):
	"""
	领取活动奖励物品
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )


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
		if self._param1 != 0:
			player.pcu_takeThings( csconst.PCU_TAKECHARGEUNITE, self._param1 )
		else:
			player.pcu_takeThings( csconst.PCU_TAKECHARGEUNITE, 0 )


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

class FuncDrawPresentSingle( Function ):
	"""
	一次领取一个活动奖励物品
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )


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
		if self._param1 != 0:
			player.pcu_takeThings( csconst.PCU_TAKECHARGEUNITE_SINGLE, self._param1 )
		else:
			player.pcu_takeThings( csconst.PCU_TAKECHARGEUNITE_SINGLE, 0 )


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
