# -*- coding: gb18030 -*-
#
# add by gjx 7/1/14

"""
"""
from Function import Function
from bwdebug import *
import csdefine


class FuncTeleportPlane( Function ):
	"""
	传送
	"""
	def __init__( self, section ):
		"""
		param1: _planeType

		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._planeType = section.readString( "param1" )

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

		# 如果有法术禁咒buff
		if player.spaceType == self._planeType:
			WARNING_MSG("Player %i teleport to plane %s which is the same as current." % (player.id, self._planeType))
			return

		player.enterPlane(self._planeType)

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
		if player.spaceType == self._planeType:
			return False

		if player.isState( csdefine.ENTITY_STATE_DEAD ):	# 如果玩家已经死亡，那么不允许传送
			return False

		return True



