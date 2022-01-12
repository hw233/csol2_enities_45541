# -*- coding: gb18030 -*-
#
# 堕落猎人管理器 2009-10-7 SongPeifang
#

from interface.WXActivityMgr import WXActivityMgr
import cschannel_msgs
import BigWorld


class DuoLuoHunterMgr( BigWorld.Base, WXActivityMgr ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.noticeMsg 			= cschannel_msgs.BCT_ZZDLLR_BEGAIN_0
		self.startMsg 			= cschannel_msgs.BCT_ZZDLLR_BEGAIN
		self.endMgs 			= ""
		self.globalFlagKey		= "DuoLuoHunterAlive"
		self.managerName 		= "DuoLuoHunterMgr"
		self.crondNoticeKey		= "DuoLuoHunterMgr_start_notice"
		self.crondStartKey		= "DuoLuoHunterMgr_start"
		self.crondEndKey		= "DuoLuoHunterMgr_end"
		self._monsClassName		= "20134003"
		self.spaceName			= "liu_wang_mu_001"
		self.position			= ( 40.224, 16.400, 67.357 )
		self.direction			= ( 0, 0, 0 )
		WXActivityMgr.__init__( self )