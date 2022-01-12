# -*- coding: gb18030 -*-
#
# $Id: FuncTongQuestStatus.py

"""
"""
from Function import Function
import BigWorld
import csdefine

class FuncTongQuestStatus( Function ):
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
		self.param02 = section.readInt( "param2" )  #任务状态
		self.param03 = section.readInt( "param3" ) #任务等级,针对帮会跑商任务
		self.param04 = section.readInt( "param4" )  #用来区分帮主与非帮主的情况

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
		scrEntity = talkEntity.getScript()
		if self.param03 > 0:							#为跑商任务
			count = 0
			for level in range( self.param03 ):
				questID = int( "%d00%d"%( self.param01, level + 1 ) )
				quest = scrEntity.getQuest( questID )
				questState = quest.query( player )
				if questState == self.param02:
					count += 1
			if count >= self.param03:						#每个等级都不可接
				return True
		else:
			quest = scrEntity.getQuest( self.param01 )
			questState = quest.query( player )
			questType = quest.getType()
			if questState == self.param02:
				return True
			elif questState == csdefine.QUEST_STATE_NOT_HAVE:
				if questType == csdefine.QUEST_TYPE_TONG_FETE and not talkEntity.feteOpen:
					return True
		return False
