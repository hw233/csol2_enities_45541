# -*- coding: gb18030 -*-

import csdefine
import csstatus
from bwdebug import *

class FuncTongBattleLeague:
	"""
	帮会战争结盟
	"""
	def __init__( self, section ):
		self.camp = section.readInt( "param1")		# 阵营

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
		if not player.checkDutyRights( csdefine.TONG_RIGHT_LEAGUE_MAMAGE ):
			player.statusMessage( csstatus.TONG_BATTLE_LEAGUE_LIMIT )
			return
		
		BigWorld.globalData[ "TongManager"].reqOpenBattleLeaguesWindow( player, player.getCamp(), player.spaceType )

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
		return self.camp == player.getCamp()
