# -*- coding: gb18030 -*-
#
# $Id: Transporter.py,v 1.7 2007-11-23 06:36:07 phw Exp $

"""
Transporter
"""

from bwdebug import *
import NPC
import BigWorld
import GUIFacade
from gbref import rds
import Define

class Transporter( NPC.NPC ):
	"""
	Transporter
	"""
	def __init__( self ):
		"""
		初始化状态。要在Fight初始化之前
		"""
		NPC.NPC.__init__( self )
		self.transportTrapID = 0

	def getRoleAndNpcSpeakDistance( self ):
		"""
		NPC和玩家对话的距离
		"""
		return self.enterRange

	def enterWorld( self ):
		"""
		进入世界
		"""
		NPC.NPC.enterWorld( self )
		# entity是传送门
		if self.isTransportDoor:
			self.model = rds.effectMgr.createModel( ["particles/gxcone.model"] )
			rds.effectMgr.createParticleBG( self.model, "HP_root", "particles/chuansongmen/chuansongmen.xml", type = Define.TYPE_PARTICLE_NPC )

			self.transportTrapID = self.addTrapExt(self.enterRange, self.onTransport )

	def leaveWorld( self ):
		"""
		离开世界
		"""
		NPC.NPC.leaveWorld( self )
		if self.transportTrapID:
			self.delTrap( self.transportTrapID )

	def onTransport( self, entitiesInTrap ):
		"""
		玩家进入离开陷阱的处发器
		"""
		# 玩家进入传送门
		if BigWorld.player() in entitiesInTrap:
			GUIFacade.gossipHello( self )


#
# $Log: not supported by cvs2svn $
# Revision 1.6  2007/06/14 10:32:35  huangyongwei
# 整理了全局宏定义
#
# Revision 1.5  2007/05/14 06:24:46  panguankong
# 修改传送门标志
#
# Revision 1.4  2007/05/14 03:06:43  panguankong
# 删除了进出trap标志
#
# Revision 1.3  2007/05/14 00:41:19  panguankong
# 添加与角色对话距离接口，删除自动关闭对话窗口
#
# Revision 1.2  2007/05/10 03:35:29  panguankong
# 修改传送门对话接口
#
# Revision 1.1  2007/05/10 02:26:34  panguankong
# 添加文件
#
#