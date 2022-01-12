# -*- coding: gb18030 -*-
#
# $Id: FuncTeachTongSkill.py,v 1.2 2008-06-21 08:08:56 kebiao Exp $

"""
"""
from Function import Function
import csdefine
import csstatus
from bwdebug import *

class FuncBuyTongItem( Function ):
	"""
	购买帮会物品
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
		if talkEntity is None:
			WARNING_MSG( "talkEntity cannot be None." )
			return
		if player.iskitbagsLocked():	# 背包上锁，by姜毅
			player.endGossip( talkEntity )
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		player.client.enterTradeWithNPC( talkEntity.id )
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
# $Log: not supported by cvs2svn $
#
#