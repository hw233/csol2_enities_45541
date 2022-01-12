# -*- coding: gb18030 -*-
#
# $Id: FuncGetjackarooCardGift.py,v 1.11 2008-01-15 06:06:34 phw Exp $

"""
"""
from Function import Function
import BigWorld
from bwdebug import *

class FuncGetjackarooCardGift( Function ):
	"""
	领取新手卡奖励物品
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )		# 领取需求的等级
		self._param2 = section.readInt( "param2" )		# 领取的物品ID


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
		if not self._param1 or not self._param2:
			ERROR_MSG("FuncGetjackarooCardGift, parameter is wrong param = %s, param = %s " % (self._param1,self._param2) )
			return
		player.base.getjackarooCardGift( self._param1, self._param2 )


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


