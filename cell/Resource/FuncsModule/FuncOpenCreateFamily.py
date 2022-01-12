# -*- coding: gb18030 -*-
#
# $Id: FuncOpenCreateFamily.py,v 1.4 2008-06-09 01:22:12 fangpengjun Exp $

"""
"""
from Function import Function
import BigWorld

class FuncOpenCreateFamily( Function ):
	"""
	打开家族创建界面
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
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
		player.client.family_enterFound( talkEntity.id )
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
# Revision 1.3  2008/06/05 07:54:14  fangpengjun
# no message
#
# Revision 1.2  2008/06/05 02:03:14  kebiao
# no message
#
#
