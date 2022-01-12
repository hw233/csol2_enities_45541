# -*- coding: gb18030 -*-
#
# $Id: FuncGuess.py,v 1.1 2008-08-06 01:12:06 zhangyuxing Exp $

"""
"""
from Function import Function
import BigWorld
from csdefine import *		# just for "eval" expediently
import random
import ECBExtend

class FuncGuess( Function ):
	"""
	判断任务状态范围
	"""
	def __init__( self, section ):
		"""
		param1: CLASS_*

		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.param01 = section.readInt( "param1" )  #猜拳随机范围
		self.param02 = section.readInt( "param2" )  #玩家出拳值
		self.param03 = section.readInt( "param3" )  #任务ID
		self.param04 = section.readInt( "param4" )  #任务目标ID

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
		player.setTemp( "talkNPCID", talkEntity.id )
		#player.setTemp( "guessValue", random.randint( 1, self.param01 ) != self.param02 )
		if random.randint( 1, self.param01 ) != self.param02:						#根据策划规定，猜拳有2/3的几率是玩家赢
			player.questTaskIncreaseState( self.param03, self.param04 )
			quest = player.getQuest( self.param03 )
			if quest.query( player ) == QUEST_STATE_FINISH:
				player.setTemp( "talkID", "finish" )
				player.addTimer( 0.3, 0, ECBExtend.AUTO_TALK_CBID )				
				return
			player.setTemp( "talkID", "win" )			
			player.addTimer( 0.3, 0, ECBExtend.AUTO_TALK_CBID )
		else:
			player.questTaskDecreaseState( self.param03, self.param04 )
			player.setTemp( "talkID", "lose" )
			player.addTimer( 0.3, 0, ECBExtend.AUTO_TALK_CBID )

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
		quest = player.getQuest( self.param03 )
		if quest.query( player ) != QUEST_STATE_NOT_FINISH:
			player.endGossip( talkEntity )
			return False
		return True
			
		


#