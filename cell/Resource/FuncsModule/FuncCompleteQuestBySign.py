# -*- coding: gb18030 -*-
#created by dqh
# $Id: Exp $


from Function import Function
import BigWorld
import csdefine
import csstatus
from bwdebug import *

class FuncCompleteQuestBySign( Function ):
	"""
	根据玩家是否有某一个指定的标记，来决定任务是否完成。有则设置任务完成
	"""
	def __init__( self, section ):
		"""
		@param param : 由实现类自己解释格式; param1 - param5
		@type  param : pyDataSection
		"""
		Function.__init__( self, section )
		
		self._tempSign = section.readString( "param1")		# 标记名称
		self._questID = section.readInt( "param2" )			# 任务ID
		self._taskIndex = section.readInt( "param3" )		# 任务目标索引

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player     : 玩家
		@type  player     : Entity
		@param talkEntity : 一个扩展的参数
		@type  talkEntity : entity
		@return           : None
		"""
		player.endGossip( talkEntity )
		player.questTaskIncreaseState( self._questID, self._taskIndex )

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用
		
		@param player		: 玩家
		@type  player		: Entity
		@param talkEntity	: 一个扩展的参数
		@type  talkEntity	: entity
		@return				: True/False
		@rtype				: bool
		"""
		quest = player.getQuest( self._questID )
		if quest and quest.query( player ) == csdefine.QUEST_STATE_NOT_FINISH and player.queryTemp( self._tempSign, 0):	#任务存在且没有完成、且玩家有指定标记
			return True
		return False

