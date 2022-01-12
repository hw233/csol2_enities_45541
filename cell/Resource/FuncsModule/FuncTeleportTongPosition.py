# -*- coding: gb18030 -*-
#
# $Id: FuncTeleport.py,v 1.16 2008-07-24 08:46:32 kebiao Exp $

"""
"""
from Function import Function
from bwdebug import *
import random
import math
import csstatus
import csdefine
import re
import utils

class FuncTeleportTongPosition( Function ):
	"""
	传送到帮会领地指定位置
	"""
	def __init__( self, section ):
		"""
		param1: spaceName
		param2: x, y, z
		param3: d1, d2, d3
		param4: radius
		
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
		player.endGossip( talkEntity )
		player.gotoSpace( "fu_ben_bang_hui_ling_di", self.pos, self.direction )
		
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



