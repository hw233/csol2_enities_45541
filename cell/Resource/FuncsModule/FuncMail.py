# -*- coding: gb18030 -*-
#
# $Id: FuncMail.py,v 1.1 2008-03-06 09:13:08 fangpengjun Exp $

"""
实现与邮件NPC对话函数
"""
from Function import Function
from bwdebug import *

class FuncMail( Function ):
	"""
	"""
	def __init__( self, section ):

		pass

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.client.enterMailWithNPC( talkEntity.id )
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