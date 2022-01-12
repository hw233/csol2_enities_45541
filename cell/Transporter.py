# -*- coding: gb18030 -*-
#
# $Id: Transporter.py,v 1.6 2007-11-23 06:36:22 phw Exp $

"""
Transporter
"""

from bwdebug import *
import NPC
import BigWorld
import Love3
import csstatus
import cschannel_msgs

class Transporter( NPC.NPC ):
	"""
	Transporter
	"""
	def __init__( self ):
		"""
		初始化状态。要在Fight初始化之前
		"""
		NPC.NPC.__init__( self )

	def isInteractionRange( self, entity ):
		"""
		判断一个entity是否在自己的交互范围内
		"""
		return self.position.flatDistTo( entity.position ) < self.enterRange + 1 # 由于延时我们在范围这里加大1米

	# 回答
	def transportDialog( self, srcEntityID, talkID ):
		"""
		virtual method.
		exposed method.
		与玩家对话；未声明(不能声明)的方法，因此重载此方法的上层如果需要访问自己的私有属性请自己判断self.isReal()。

		@param srcEntityID: 说话的玩家ID
		@type  srcEntityID: EntityID
		@param       talkID: 对话关键字
		@type        talkID: str
		@return: 无
		"""
		try:
			playerEntity = BigWorld.entities[srcEntityID]
		except KeyError:
			INFO_MSG( "entity %i not exist in world" % srcEntityID )	# 这个应该永远都不可能到达
			return

		if self.isTransportDoor:
			if not self.isInteractionRange( playerEntity ):
				WARNING_MSG( "%s(%i): target too far." % (playerEntity.playerName, playerEntity.id) )
				return
		else:
			if not NPC.NPC.isInteractionRange( self, playerEntity ):
				WARNING_MSG( "%s(%i): target too far." % (playerEntity.playerName, playerEntity.id) )
				return

		transportHistory = playerEntity.transportHistory

		# 对话处理
		if talkID == "Talk":
			# 标记传送器
			if not transportHistory & self.transportSign:
				playerEntity.tagTransport( self.transportSign )
				transportHistory = transportHistory & self.transportSign

			# 让client显示已经激活的传送门
			show = False
			for space, value in Love3.g_transporterData.getData().iteritems():
				for sign, sect in value.iteritems():
					if transportHistory & sign and sign != self.transportSign:
						self.addGossipOption( playerEntity, "DOOR" + str(sign), sect["name"] )
						show = True
			if show:
				self.setGossipText( playerEntity, cschannel_msgs.CELL_Transporter_1 )
				if self.isTransportDoor:
					self.sendGossipComplete( playerEntity )
		else:
			# 选择传送
			for space, value in Love3.g_transporterData.getData().iteritems():
				for sign, sect in value.iteritems():
					if transportHistory & sign and str(sign) == talkID[4:]:
						self.endGossip( playerEntity )
						playerEntity.gotoSpace( space, sect["pos"], sect["direction"] )
						break

#
# $Log: not supported by cvs2svn $
# Revision 1.5  2007/05/14 06:25:23  panguankong
# 修改传送门标志
#
# Revision 1.4  2007/05/14 05:40:34  phw
# method modified: transportDialog(), playerEntity.goto -> playerEntity.gotoSpace
#
# Revision 1.3  2007/05/14 00:36:15  panguankong
# 修改传送门对话接口
#
# Revision 1.2  2007/05/10 03:36:13  panguankong
# 修改传送门对话接口
#
# Revision 1.1  2007/05/10 02:26:50  panguankong
# 添加文件
#
#