# -*- coding: gb18030 -*-
#
# $Id: FuncLevel.py,v 1.1 2008-01-31 05:18:39 zhangyuxing Exp $

"""
"""
from Function import Function
import BigWorld
from csdefine import *		# just for "eval" expediently

class FuncLevel( Function ):
	"""
	判断等级范围
	"""
	def __init__( self, section ):
		"""
		param1: CLASS_*

		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.param01 = section.readInt( "param1" )  #最小等级
		self.param02 = section.readInt( "pramm2" )  #最大等级

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
		if self.param01 == 0:
			if self.param02 == 0 or player.level <= self.param02:
				return True
		else:
			if self.param01 <= player.level and ( self.param02 == 0 or player.level <= self.param02 ):
				return True
		
		return False
		


#