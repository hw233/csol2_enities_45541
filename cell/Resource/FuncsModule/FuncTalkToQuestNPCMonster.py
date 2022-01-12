# -*- coding: gb18030 -*-

from Function import Function
from bwdebug import *
import csdefine
import csstatus

class FuncTalkToQuestNPCMonster( Function ):
	"""
	与任务怪NPC的对话，任务未完成对话
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		questStrs = section.readString( "param1" )	# 该NPC拥有的任务ID
		self._questIDs = questStrs.split( '|' )
		dialogStrs = section.readString( "param2" )	# 玩家看到的对话
		self._dialogs = dialogStrs.split( '|' )

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
		talkDatas = {}
		valid = False
		if len( self._questIDs ) != len( self._dialogs ): return valid
		for index in range( len( self._questIDs ) ):
			talkDatas[ self._questIDs[index] ] = self._dialogs[index]
		# 优先显示低等级任务对话内容
		questID = 0
		questLevel = 150
		for qID in self._questIDs:
			if player.questsTable._quests.has_key( int( qID ) ):
				quest = player.getQuest( int( qID ) )
				if quest.query( player ) == csdefine.QUEST_STATE_NOT_FINISH:
					if quest.getLevel() <= questLevel:
						questLevel = quest.getLevel()
						questID = qID
						valid = True
		if valid:
			player.setGossipText( talkDatas[questID] )
		return valid