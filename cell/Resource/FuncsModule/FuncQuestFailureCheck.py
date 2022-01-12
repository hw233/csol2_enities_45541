# -*- coding: gb18030 -*-
#
# 检查任务的失败情况，0：失败，1：未失败
# by ganjinxing 2012-01-10

from Function import Function


class FuncQuestFailureCheck( Function ):
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
		if not player.has_quest( self.param01 ) :
			return False
		if self.param02 == 0 :
			return player.questIsFailed( self.param01 )
		elif self.param02 == 1 :
			return not player.questIsFailed( self.param01 )
		return False

#