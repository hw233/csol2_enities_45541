# -*- coding: gb18030 -*-
#
# $Id: FuncSubQuestStatu.py,v 1.1 2008-08-06 01:12:13 zhangyuxing Exp $

"""
"""
from Function import Function
import BigWorld
from csdefine import *		# just for "eval" expediently

class FuncSubQuestStatu( Function ):
	"""
	判断任务状态范围
	"""
	def __init__( self, section ):
		"""
		param1: CLASS_*

		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.param01 = section.readInt( "param1" )  #任务ID
		self.param02 = section.readInt( "param2" )  #字任务ID
		self.param03 = section.readInt( "param3" )  #任务状态

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		pass

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
		quest = player.getQuest( self.param01 )
		if quest != None:
			if player.questsTable.has_quest( self.param01 ) and player.questsTable[self.param01].query( "subQuestID" ) == self.param02:
				if quest.query( player ) == self.param03:
					return True
		return False
			
		


#