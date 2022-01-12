# -*- coding: gb18030 -*-
#
# $Id:  $

"""
"""
from Function import Function
from bwdebug import *
import BigWorld
import csconst
import csstatus
import csdefine
import utils

class FuncLeavePrison( Function ):
	"""
	离开监狱
	"""
	def __init__( self, section ):
		"""
		param1: CLASS_*

		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.param01 = section.readInt( "param1" )  # 小于某个pk值才显示选项
		self.spaceName = section.readString( "param2" )
		self.pos = None
		self.direction = None
		
		position = section.readString( "param3" )
		pos = utils.vector3TypeConvert( position )
		if pos is None:
			ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section param3 " % ( self.__class__.__name__, position ) )
		else:
			self.pos = pos
		
		direction = section.readString( "param4" )
		dir = utils.vector3TypeConvert( direction )
		if dir is None:
			ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section param4 " % ( self.__class__.__name__, direction ) )
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
		player.endGossip( talkEntity )
		if player.pkValue >= self.param01:
			player.statusMessage( csstatus.PRISON_LEAVE_VALID, self.param01 )
			return

		player.setTemp( "leavePrison", True )
		player.gotoSpace( self.spaceName, self.pos, self.direction )

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