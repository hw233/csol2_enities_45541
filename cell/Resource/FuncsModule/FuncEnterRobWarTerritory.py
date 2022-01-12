# -*- coding: gb18030 -*-
#
# $Id: FuncContestFamilyNPC.py,v 1.3 2008-07-31 04:14:37 kebiao Exp $

"""
"""
from Function import Function
import BigWorld
import csstatus
import csdefine
import csconst
import utils
from bwdebug import *

class FuncEnterRobWarTerritory( Function ):
	"""
	进入帮会掠夺战对方领地
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.pos = None
		self.direction = None
		
		position = section.readString( "param1" )
		pos = utils.vector3TypeConvert( position )
		if pos is None:
			ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section param1 " % ( self.__class__.__name__, position ) )
		else:
			self.pos = pos
		
		direction = section.readString( "param2" )
		dir = utils.vector3TypeConvert( direction )
		if dir is None:
			ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section param2 " % ( self.__class__.__name__, direction ) )
		else:
			self.direction = dir

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if player.level < csconst.PK_PROTECT_LEVEL:
			player.statusMessage( csstatus.ROLE_LEVEL_LOWER_PK_ALOW_LEVEL )
			player.endGossip( talkEntity )
			return
		
		player.tong_enterTongTerritoryByDBID( player.robWarTargetTong, self.pos, self.direction )
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
		return BigWorld.globalData.has_key( "TONG_ROB_WAR_START" ) and player.robWarTargetTong > 0


#
# $Log: not supported by cvs2svn $
#
