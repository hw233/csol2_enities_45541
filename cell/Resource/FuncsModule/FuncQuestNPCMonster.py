# -*- coding: gb18030 -*-
#
# 2009-02-11 SongPeifang
#
"""
与任务怪NPC的对话
"""
from Function import Function
from bwdebug import *
import csdefine
import csstatus

class FuncQuestNPCMonster( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		questStrs = section.readString( "param1" )	# 该NPC拥有的任务ID
		self._questIDs = questStrs.split( '|' )
		self._invalidDialog = section.readString( "param2" )	# 不符合条件的玩家看到的对话

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
		if player.getState() == csdefine.ENTITY_STATE_PENDING:
			player.statusMessage( csstatus.NPC_TRADE_FORBID_TALK )
			return
		if talkEntity != None:
			talkEntity.changeToMonster( talkEntity.level, player.id )
			talkEntity.setTemp( "ownerID", player.id )	#add by wuxo 2011-9-23
			# 在这里直接设置怪物的bootyOwner
			getEnemyTeam = getattr( player, "getTeamMailbox", None )	# 如果有队伍则记录队伍mailbox
			if getEnemyTeam and getEnemyTeam():
				talkEntity.bootyOwner = ( player.id, getEnemyTeam().id )
			else:
				talkEntity.bootyOwner = ( player.id, 0 )
			talkEntity.firstBruise = 1		# 避免怪物第一次受伤害对bootyOwner处理

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
		valid = False
		for qID in self._questIDs:
			if player.questsTable._quests.has_key( int( qID ) ):
				if player.getQuest( int( qID ) ).query( player ) == csdefine.QUEST_STATE_NOT_FINISH:
					valid = True
				else:
					valid = False
				break
		if not valid:
			player.setGossipText( self._invalidDialog )
		return valid