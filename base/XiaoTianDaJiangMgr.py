# -*- coding: gb18030 -*-
#
# 啸天大将管理器 2009-10-07 SongPeifang
#

from interface.WXActivityMgr import WXActivityMgr
import cschannel_msgs
import BigWorld


class XiaoTianDaJiangMgr( BigWorld.Base, WXActivityMgr ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.noticeMsg 			= cschannel_msgs.BCT_JBXTDJ_BEGAIN_0
		self.startMsg 			= cschannel_msgs.BCT_JBXTDJ_BEGAIN
		self.endMgs 			= ""
		self.globalFlagKey		= "XiaoTianDaJiangAlive"
		self.managerName 		= "XiaoTianDaJiangMgr"
		self.crondNoticeKey		= "XiaoTianDaJiangMgr_start_notice"
		self.crondStartKey		= "XiaoTianDaJiangMgr_start"
		self.crondEndKey		= "XiaoTianDaJiangMgr_end"
		self._monsClassName		= "20724005"
		self.spaceName			= "liu_wang_mu_005"
		self.position			= ( 39.784, 8.400, 75.038 )
		self.direction			= ( 0, 0, 0 )
		WXActivityMgr.__init__( self )