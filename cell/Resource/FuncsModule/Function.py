# -*- coding: gb18030 -*-
#
# $Id: Function.py,v 1.4 2008-01-15 06:06:34 phw Exp $

"""
"""

class Function:
	"""
	对话抽像层
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass
	
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能，必须重载
		
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		pass
	
	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用，必须重载
		
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
# Revision 1.3  2007/05/18 08:42:02  kebiao
# 修改所有param 为targetEntity
#
# Revision 1.2  2005/12/22 09:55:27  xuning
# no message
#
# Revision 1.1  2005/12/08 01:08:03  phw
# no message
#
#
