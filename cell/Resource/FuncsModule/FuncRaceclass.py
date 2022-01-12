# -*- coding: gb18030 -*-
#
# $Id: FuncRaceclass.py,v 1.6 2008-01-15 06:06:34 phw Exp $

"""
"""
from Function import Function
import BigWorld
from csdefine import *		# just for "eval" expediently

class FuncRaceclass( Function ):
	"""
	判断种族职业
	"""
	def __init__( self, section ):
		"""
		param1: CLASS_*

		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.param = section.readInt( "param1" )  << 4	# 左移4位的原因是因为当前配置混乱所致

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		pass

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
		return player.getClass() == self.param


#
# $Log: not supported by cvs2svn $
# Revision 1.5  2007/06/14 09:58:54  huangyongwei
# 重新整理了宏定义
#
# Revision 1.4  2007/05/18 08:42:01  kebiao
# 修改所有param 为targetEntity
#
# Revision 1.3  2007/04/21 02:36:01  phw
# method modified: valid(), L3Command.isRaceclass -> player.isRaceclass
#
# Revision 1.2  2005/12/28 06:29:55  phw
# 修正参数值类型不正确的问题
#
# Revision 1.1  2005/12/22 09:55:27  xuning
# no message
#
#
