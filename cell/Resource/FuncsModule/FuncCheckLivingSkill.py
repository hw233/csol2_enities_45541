# -*- coding: gb18030 -*-
#
"""
检测该生活技能是否没有学习
edit by wuxo 2013-1-30
"""

from Function import Function


class FuncCheckLivingSkill( Function ):
	"""
	判断生活技能是否没有学习
	"""
	def __init__( self, section ):
		"""
		param1: CLASS_*

		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.param1 = section.readInt( "param1" )  

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
		for id in player.livingskill:
			baseID = id / 1000
			if baseID == self.param1:
				return False
		return True


