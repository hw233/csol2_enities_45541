# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
NPC基类
"""

import BigWorld
from bwdebug import *
import csdefine
import csstatus
from NPC import NPC

TONG_TREASURY_MGR = "10111132"				#金库管理员

class TongTerritoryNPC( NPC ):
	"""
	帮会领地NPC基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPC.__init__( self )

	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		与玩家对话；未声明(不能声明)的方法，因此重载此方法的上层如果需要访问自己的私有属性请自己判断self.isReal()。

		@param   selfEntity: 与自己对应的Entity实例，传这个参数是为了方便以后的扩充
		@type    selfEntity: Entity
		@param playerEntity: 说话的玩家
		@type  playerEntity: Entity
		@param       dlgKey: 对话关键字
		@type        dlgKey: str
		@return: 无
		"""
		if selfEntity.ownTongDBID > 0 and selfEntity.ownTongDBID != playerEntity.tong_dbID:
			playerEntity.statusMessage( csstatus.TONG_NPC_IS_TARGET_TONG_NPC )
			return
		elif selfEntity.locked:
			playerEntity.statusMessage( csstatus.TONG_NPC_LOCKED )
			return			
		NPC.gossipWith( self, selfEntity, playerEntity, dlgKey )

	def questStatus( self, selfEntity, playerEntity ):
		"""
		查询一个游戏对象所有任务相对于玩家的状态，状态将通过回调返回给client相对应的GameObject。

		@param   selfEntity: 与自己对应的Entity实例，传这个参数是为了方便以后的扩充
		@type    selfEntity: Entity
		@param playerEntity: 玩家
		@type  playerEntity: Entity
		@return: 无
		"""

		level,signID = self.getQuestStateLevel( playerEntity )
		if selfEntity.className == TONG_TREASURY_MGR and level > 500:
			signID = 101
		playerEntity.clientEntity( selfEntity.id ).onQuestStatus( signID )
	
# NPC.py
