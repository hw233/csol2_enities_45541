# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
"""
from FuncTeleport import FuncTeleport
from bwdebug import *
import BigWorld
import csstatus
import csdefine
import csconst

class FuncEnterSunBath( FuncTeleport ):
	"""
	进入土星副本
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		FuncTeleport.__init__( self, section )
		if section.readString( "param4" ):			 # 允许召唤的守护的数量
			self.amount = section.readInt( "param4" )
		else:
			self.amount = csconst.ROLE_CALL_PGNAGUAL_LIMIT_EASY
		
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
		if player.level < self.repLevel:
			player.statusMessage( csstatus.SUN_BATHING_ENTER_LEVEL, self.repLevel )
			return
		player.setTemp("ROLE_CALL_PGNAGUAL_LIMIT", self.amount )
		player.gotoSpace( self.spaceName, self.calcPosition( self.position ), self.direction )
		