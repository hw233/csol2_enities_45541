# -*- coding: gb18030 -*-
#
# $Id: FuncTransporter.py,v 1.5 2008-01-15 06:06:34 phw Exp $

"""
"""
from Function import Function
import BigWorld
import Const

class FuncTransporter( Function ):
	"""
	装备强化
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
		talkEntity.transportDialog( player.id, "Talk" )

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
		if player.hasMerchantItem():
			return False
		# 如果有法术禁咒buff
		if len( player.findBuffsByBuffID( Const.FA_SHU_JIN_ZHOU_BUFF ) ) > 0:
			return False
		return True


#
# $Log: not supported by cvs2svn $
# Revision 1.4  2007/12/05 03:36:24  phw
# 修正了无法正确关闭客户端对话界面的bug
#
# Revision 1.3  2007/06/14 09:58:54  huangyongwei
# 重新整理了宏定义
#
# Revision 1.2  2007/05/18 08:42:02  kebiao
# 修改所有param 为targetEntity
#
# Revision 1.1  2007/05/10 02:28:21  panguankong
# 添加文件
#
# Revision 1.1  2007/04/06 01:33:53  panguankong
# 添加文件
#
# Revision 1.1  2007/04/05 02:04:13  panguankong
# 添加材料合成功能
#
#