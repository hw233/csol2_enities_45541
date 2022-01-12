# -*- coding: gb18030 -*-
#
# $Id: FuncLearn.py,v 1.7 2008-01-15 06:06:34 phw Exp $

"""
"""
from Function import Function
import BigWorld

class FuncLearn( Function ):
	"""
	学习
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
		player.endGossip( talkEntity )
		talkEntity.sendTrainInfoToPlayer( player.id, 0 )

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
# Revision 1.6  2007/12/05 03:36:24  phw
# 修正了无法正确关闭客户端对话界面的bug
#
# Revision 1.5  2007/06/14 09:58:54  huangyongwei
# 重新整理了宏定义
#
# Revision 1.4  2007/05/18 08:42:01  kebiao
# 修改所有param 为targetEntity
#
# Revision 1.3  2006/12/11 11:21:09  huangyongwei
# 添加了结束对话：endGooip
#
# Revision 1.2  2006/02/28 08:13:07  phw
# no message
#
# Revision 1.1  2005/12/22 09:55:27  xuning
# no message
#
#
