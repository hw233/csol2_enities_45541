# -*- coding: gb18030 -*-
#
# $Id: FuncConstCityWar.py,v 1.1 2008-08-20 00:52:43 kebiao Exp $

"""
"""
from Function import Function
from bwdebug import *
import csdefine
import csstatus
import csconst
import BigWorld


class FuncQueryCityWarTable( Function ):
	"""
	查看赛程表
	"""
	def __init__( self, section ):
		"""
		param1: amount
		
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.week = section.readInt( "param1" )
		
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能
		
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.client.tong_openQueryCityWarInfoWindow(0)
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
# Revision 1.2  2008/08/02 09:25:48  kebiao
# no message
#
# Revision 1.1  2008/07/25 03:17:49  kebiao
# no message
#
#
