# -*- coding: gb18030 -*-
#


from Function import Function
from FuncSunBath import FuncEnterSunBath
import BigWorld
import csdefine
import csstatus
from bwdebug import *

class FuncEndQuestTaskThenTeleport( FuncEnterSunBath ):
	"""
	判断是否完成某个任务目标。
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		FuncEnterSunBath.__init__( self, section )
		questAndTask = section.readString( "param5" ).split( ":" )	# 任务ID；任务目标索引
		self.questID = int( questAndTask[0] )
		self.taskIndex = int( questAndTask[1] )

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
		if not player.taskIsCompleted( self.questID, self.taskIndex ):
			player.statusMessage( csstatus.ROLE_QUEST_TASK_IS_NOT_COMPLETED )
			return
		if player.level < self.repLevel:
			player.statusMessage( csstatus.SUN_BATHING_ENTER_LEVEL, self.repLevel )
			return
		player.setTemp("ROLE_CALL_PGNAGUAL_LIMIT", self.amount )
		player.gotoSpace( self.spaceName, self.calcPosition( self.position ), self.direction )


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


