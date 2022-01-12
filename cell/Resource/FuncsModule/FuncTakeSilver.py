# -*- coding: gb18030 -*-
#


"""
"""
from Function import Function
import BigWorld
import csdefine


class FuncTakeSilver( Function ):
	"""
	领取元宝
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass


	def do( self, player, talkEntity = None ):
		"""
		"""
		player.endGossip( talkEntity )
		player.base.takeSilver()
		


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

