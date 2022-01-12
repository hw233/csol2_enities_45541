# -*- coding: gb18030 -*-
#
# $Id: FuncWarehouse.py,v 1.12 2008-01-15 06:06:34 phw Exp $

"""
"""

from bwdebug import *
import cschannel_msgs
import ShareTexts as ST
from Function import Function
import csdefine
import items
import Const
import ItemTypeEnum
import sys

class FuncCheckUsedWallow( Function ):
	"""
	是否受防沉迷系统限制
	"""
	def __init__( self, section ):
		Function.__init__( self, section )
	
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
		return not player.wallow_isEffected()