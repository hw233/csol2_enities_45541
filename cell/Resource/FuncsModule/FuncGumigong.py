# -*- coding: gb18030 -*-
#


"""
"""
from Function import Function
import csdefine
import BigWorld
import time
import csstatus
import ECBExtend

ENTERN_GUMIGONG_MENBER_DISTANCE = 30.0


class FuncGumigongQuestTalk( Function ):
	"""
	进入古秘宫副本
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._questID = section.readInt( "param1" )										#进入任务ID
		self._talk1 = section.readString( "param2" )									
		self._talk2 = section.readString( "param3" )									
		self._talk3 = section.readString( "param4" )									
		self._talk4 = section.readString( "param5" )									


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
		quest = player.getQuest( self._questID )
		player.setTemp( 'talkNPCID',talkEntity.id )
		
		
		if quest.query( player ) == csdefine.QUEST_STATE_NOT_ALLOW:
			player.setTemp( "talkID", self._talk1 )
			player.addTimer( 0.3, 0, ECBExtend.AUTO_TALK_CBID )	

		elif quest.query( player ) == csdefine.QUEST_STATE_NOT_HAVE:
			player.setTemp( "talkID", self._talk1 )
			player.addTimer( 0.3, 0, ECBExtend.AUTO_TALK_CBID )	

		elif quest.query( player ) == csdefine.QUEST_STATE_FINISH:
			player.setTemp( "talkID", self._talk3 )
			player.addTimer( 0.3, 0, ECBExtend.AUTO_TALK_CBID )	

		elif quest.query( player ) == csdefine.QUEST_STATE_COMPLETE:
			player.setTemp( "talkID", self._talk4 )
			player.addTimer( 0.3, 0, ECBExtend.AUTO_TALK_CBID )	


		elif quest.query( player ) == csdefine.QUEST_STATE_NOT_FINISH:
			player.setTemp( "talkID", self._talk2 )
			player.addTimer( 0.3, 0, ECBExtend.AUTO_TALK_CBID )

		return False


class FuncGumigong( Function ):
	"""
	进入古秘宫副本
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._questID = section.readInt( "param1" )										#进入任务ID


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
		
		if not player.isInTeam():
			player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
			return
		
		quest = player.getQuest( self._questID )
		if quest.query( player ) != csdefine.QUEST_STATE_NOT_FINISH:
			return
		#for i in player.getAllMemberInRange( ENTERN_SHUIJING_MENBER_DISTANCE ):
		#	if quest.query( i ) != csdefine.QUEST_STATE_NOT_FINISH :
		#		player.statusMessage( csstatus.GUMIGONG_MEMBER_NOT_HAVE_QUEST )
		#		return
		
		
		pList = player.getAllMemberInRange( ENTERN_GUMIGONG_MENBER_DISTANCE )
		
		
		for i in pList:
			i.gotoSpace('gumigong', (20,22,53), (0,0,0))
		

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

