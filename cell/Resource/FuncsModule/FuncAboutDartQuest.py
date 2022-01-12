# -*- coding: gb18030 -*-
#
# $Id: FuncAboutRanQuest.py,v 1.8 2008-08-15 09:16:45 zhangyuxing Exp $

"""
"""
from Function import Function
import cschannel_msgs
import ShareTexts as ST
import BigWorld
import csdefine
import csstatus
import csconst
import ECBExtend

class FuncCancelDartQuest( Function ):
	"""
	放弃任务
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )
		self._param2 = section.readInt( "param2" )
		self._param3 = section.readInt( "param3" )
		self._param4 = section.readInt( "param4" )
		self._param5 = section.readInt( "param5" )

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
		questID = 0
		for id in player.questsTable._quests:
			if player.getQuest( id ).getType() in [self._param5, self._param2, self._param3, self._param4]:
				if player.questsTable[id].query('factionID') == self._param1:
					questID = id
					break
				else:
					player.setGossipText( cschannel_msgs.DART_INFO_5 )
					player.sendGossipComplete( int( talkEntity.id ) )
					return
				
		
		if questID == 0:
			player.setGossipText( cschannel_msgs.DART_INFO_6 )
			player.sendGossipComplete( int( talkEntity.id ) )
			return

		if BigWorld.time() - player.queryTemp( "acceptDartQuestTime", 0 ) < 2.0:
			player.setTemp( "abandonDartQuestID", questID )
			player.addTimer( 3.0, 0.0, ECBExtend.ROLE_ABANDON_DART_QUEST_CBID );
			return

		player.getQuest( questID ).abandoned( player, csdefine.QUEST_REMOVE_FLAG_NPC_CHOOSE )
		player.questRemove( questID, True )
		player.onQuestBoxStateUpdate()



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


class FuncGotoDart( Function ):
	"""
	到镖车去
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
 		pass

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
		
		if player.hasFlag( csdefine.ROLE_FLAG_XL_DARTING ) and talkEntity.getFaction() != csconst.FACTION_XL:
			player.statusMessage( csstatus.ROLE_QUEST_DART_NOT_SEND_SELF )
			return
		if player.hasFlag( csdefine.ROLE_FLAG_CP_DARTING ) and talkEntity.getFaction() != csconst.FACTION_CP:
			player.statusMessage( csstatus.ROLE_QUEST_DART_NOT_SEND_SELF )
			return
		
		BigWorld.globalData["DartManager"].sendOwnerToDart( player.getName(), player.base )

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
		return player.isDarting()
