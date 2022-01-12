# -*- coding: gb18030 -*-
#


from Function import Function
import BigWorld
import csdefine
import csstatus
from bwdebug import *

class FuncCompletedQuest( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )	# 任务ID

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
		quest = player.getQuest( self._param1 )
		if quest is None:
			ERROR_MSG( "cell/FuncCompletedQuest.py: There is no quest which ID is %i" % self._param1 )
			return False
		return quest.query( player ) == csdefine.QUEST_STATE_COMPLETE


