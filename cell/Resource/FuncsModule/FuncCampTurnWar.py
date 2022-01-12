# -*- coding: gb18030 -*-

import csstatus
import csconst
import BigWorld
from Function import Function

class FuncCampTurnWarSignUp( Function ):
	"""
	报名帮会车轮战
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._param1 = section.readString( "param1" )	# 报名的车轮战城市
		
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
		if BigWorld.globalData["CampTurnWarStep"] == csconst.CAMP_TURN_STEP_SIGNUP :
			return True
		return False
	
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
		if not player.isCaptain():
			player.statusMessage( csstatus.CAMP_TURN_WAR_SIGNUP_NOT_CAPTAIN )
			return

		if player.level < csconst.CAMP_TURN_LEVEL_MIN:
			player.statusMessage( csstatus.CAMP_TURN_WAR_SIGNUP_LEVEL_WRONG )
			return
		player.client.campTurnWar_signUpCheck( self._param1, csconst.CAMP_TURN_MEMBER_NUM)