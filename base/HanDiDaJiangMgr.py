# -*- coding: gb18030 -*-
#
# 撼地大将管理器 2009-10-07 SongPeifang
#

from interface.WXActivityMgr import WXActivityMgr
import cschannel_msgs
import BigWorld


class HanDiDaJiangMgr( BigWorld.Base, WXActivityMgr ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.noticeMsg 			= cschannel_msgs.BCT_PHZHDD_BEGAIN_0
		self.startMsg 			= cschannel_msgs.BCT_PHZHDD_BEGAIN
		self.endMgs 			= ""
		self.globalFlagKey		= "HanDiDaJiangAlive"
		self.managerName 		= "HanDiDaJiangMgr"
		self.crondNoticeKey		= "HanDiDaJiangMgr_start_notice"
		self.crondStartKey		= "HanDiDaJiangMgr_start"
		self.crondEndKey		= "HanDiDaJiangMgr_end"
		self._monsClassName		= "20754012"
		self.spaceName			= "liu_wang_mu_004"
		self.position			= ( 40.264, 9.500, -56.092 )
		self.direction			= ( 0, 0, 0 )
		WXActivityMgr.__init__( self )