# -*- coding: gb18030 -*-
"""
升级神器对话 16:22 2010-5-14 by 姜毅
"""

from Function import Function

class FuncGodWeapon( Function ):
	"""
	学习生活技能
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		# self._talkType = int( section.readString( "param1" ) )	# 需要学习(1)还是遗忘(2)还是升级(3)技能

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.client.showGodWeaponMaker()
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
		return True