# -*- coding: gb18030 -*-
#
# 疯狂祭师管理器 2009-10-7 SongPeifang
#

from interface.WXActivityMgr import WXActivityMgr
import cschannel_msgs
import BigWorld


class CrazyJiShiMgr( BigWorld.Base, WXActivityMgr ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.noticeMsg 			= cschannel_msgs.BCT_PHFKJS_BEGAIN_0
		self.startMsg 			= cschannel_msgs.BCT_PHFKJS_BEGAIN
		self.endMgs 			= ""
		self.globalFlagKey		= "CrazyJiShiAlive"
		self.managerName 		= "CrazyJiShiMgr"
		self.crondNoticeKey		= "CrazyJiShiMgr_start_notice"
		self.crondStartKey		= "CrazyJiShiMgr_start"
		self.crondEndKey		= "CrazyJiShiMgr_end"
		self._monsClassName		= "20144003"
		self.spaceName			= "liu_wang_mu_002"
		self.position			= ( 39.067, 15.200, 120.064 )
		self.direction			= ( 0, 0, 0 )
		WXActivityMgr.__init__( self )