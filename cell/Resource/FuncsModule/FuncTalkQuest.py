# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
"""
from Function import Function
import csdefine
import BigWorld
import csstatus

class FuncTalkQuest( Function ):
	"""
	对话任务选项
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )			#任务ID
		self._param2 = section.readInt( "param2" )			#任务目标索引

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
		player.questTalk( talkEntity.className )

		

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
			return False
		
		if quest.query( player ) != csdefine.QUEST_STATE_NOT_FINISH:
			return False
		
		if player.getQuestTasks( self._param1 ).getTasks()[self._param2].isCompleted( player ):
			return False
		return True



class FuncTalkRandomQuest( Function ):
	"""
	组对话任务选项
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )			#组任务ID
		self._param2 = section.readInt( "param2" )			#子任务ID
		self._param3 = section.readInt( "param3" )			#任务目标索引

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
		player.questTalk( talkEntity.className )

		

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
			return False
		
		if quest.query( player ) != csdefine.QUEST_STATE_NOT_FINISH:
			return False
		
		tasks = player.getQuestTasks( self._param1 )
		subQuestID = tasks.query( "subQuestID" )
		
		if self._param2 != subQuestID:
			return
		
		if tasks.getTasks()[self._param3].isCompleted( player ):
			return False
		return True



class FuncTalkRandomQuestWithAction( FuncTalkRandomQuest ):
	"""
	有动作的对话任务
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )			#组任务ID
		self._param2 = section.readInt( "param2" )			#子任务ID
		self._param3 = section.readInt( "param3" )			#任务目标索引
		self._param4 = section.readString( "param4" )			#角色动作
		self._param5 = section.readString( "param5" )			#NPC动作


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
		player.questTalk( talkEntity.className )
		player.planesAllClients( "onPlayAction", ( self._param4, ) )
		talkEntity.planesAllClients( "onPlayAction", ( self._param5, ) )
