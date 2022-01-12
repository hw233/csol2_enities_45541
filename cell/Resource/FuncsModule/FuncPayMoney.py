# -*- coding: gb18030 -*-
#
# $Id: FuncPayMoney.py,v 1.2 2008-01-15 06:06:34 phw Exp $

"""
"""
import csdefine
from Function import Function
from bwdebug import *

class FuncPayMoney( Function ):
	"""
	支付
	"""
	def __init__( self, section ):
		"""
		param1: amount
		
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._payMoneyValue = abs( section.readInt( "param1" ) )
	
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能
		
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.payMoney( self._payMoneyValue, csdefine.CHANGE_MONEY_NPC_TALK )
	
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
		return player.money >= self._payMoneyValue


#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/05/18 08:45:52  kebiao
# no message
#
#
#
