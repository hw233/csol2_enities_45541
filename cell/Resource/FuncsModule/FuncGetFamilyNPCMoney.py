# -*- coding: gb18030 -*-
#
# $Id: FuncGetFamilyNPCMoney.py,v 1.4 2008-07-25 03:17:24 kebiao Exp $

"""
"""
from Function import Function
from bwdebug import *
import csdefine
import csstatus
import random

class FuncGetFamilyNPCMoney( Function ):
	"""
	收取家族NPC管理费
	"""
	def __init__( self, section ):
		"""
		param1: amount

		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.p1 = abs( section.readInt( "param1" ) )
		self.p2 = abs( section.readInt( "param2" ) )

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if player.family_grade == csdefine.FAMILY_GRADE_SHAIKH:
			money = random.randint( self.p1, self.p2 )
			player.getFamilyManager().onGetContestNPCMoney( player.base, player.family_dbID, money )
		else:
			player.statusMessage( csstatus.FAMILY_GET_MONEY_NOT_SHAIKH )
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
		return player.familyNPC == talkEntity.className


#
# $Log: not supported by cvs2svn $
# Revision 1.3  2008/07/19 06:27:26  kebiao
# no message
#
# Revision 1.2  2008/07/19 04:06:38  kebiao
# no message
#
# Revision 1.1  2008/07/19 03:53:19  kebiao
# no message
#
# Revision 1.2  2008/01/15 06:06:34  phw
# 调整了初始化方式
#
# Revision 1.1  2007/05/18 08:45:52  kebiao
# no message
#
#
#
