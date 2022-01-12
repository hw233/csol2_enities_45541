# -*- coding: gb18030 -*-
#
# $Id: FuncSell.py,v 1.11 2008-01-15 06:06:34 phw Exp $

"""
"""
from Function import Function
import csdefine
import csstatus

class FuncSell( Function ):
	"""
	交易 -- 卖
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
		if player.iskitbagsLocked():	# 背包上锁，by姜毅
			player.endGossip( talkEntity )
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		player.client.enterTradeWithNPC( talkEntity.id )
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
# Revision 1.10  2007/12/05 03:36:24  phw
# 修正了无法正确关闭客户端对话界面的bug
#
# Revision 1.9  2007/08/18 08:05:44  yangkai
# NPC交易代码调整
#     - 优化了NPC交易状态的判断
#     - 直接通知客户端
#
# Revision 1.8  2007/06/14 09:58:54  huangyongwei
# 重新整理了宏定义
#
# Revision 1.7  2007/05/18 08:42:01  kebiao
# 修改所有param 为targetEntity
#
# Revision 1.6  2006/08/30 04:29:04  phw
# modify method: do(); close gossip window when tradeing begin.
#
# Revision 1.5  2006/02/28 08:13:07  phw
# no message
#
# Revision 1.4  2005/12/22 09:55:27  xuning
# no message
#
# Revision 1.3  2005/12/14 02:50:57  phw
# no message
#
# Revision 1.2  2005/12/12 02:00:46  phw
# no message
#
# Revision 1.1  2005/12/08 01:08:03  phw
# no message
#
#
