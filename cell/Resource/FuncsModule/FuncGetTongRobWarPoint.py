# -*- coding: gb18030 -*-
#
# $Id: FuncExp2Pot.py,v 1.1 2010-01-14 05:18:39 pengju Exp $

"""
"""
import BigWorld
import csdefine
import csstatus
from Function import Function

class FuncGetTongRobWarPoint( Function ):
	"""
	领取掠夺战积分
	"""
	def __init__( self, section ):
		"""
		param1: CLASS_*

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
		if not player.isTongChief():
			player.statusMessage( csstatus.TONG_ROB_WAR_REWARD_GRADE )
			player.endGossip( talkEntity )
			return
		BigWorld.globalData["TongManager"].getTongRobWarPoint( player.base, player.tong_dbID )
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
		return True



#