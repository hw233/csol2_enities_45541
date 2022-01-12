# -*- coding: gb18030 -*-
#
# 封印白蛇管理器 2009-05-25 SongPeifang
#

from interface.WXActivityMgr import WXActivityMgr
import cschannel_msgs
import BigWorld


class SealSnakeMgr( BigWorld.Base, WXActivityMgr ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.noticeMsg 			= cschannel_msgs.BCT_FYBSY_BEGAIN_0
		self.startMsg 			= cschannel_msgs.BCT_FYBSY_BEGAIN
		self.endMgs 			= ""
		self.globalFlagKey		= "SnakeBossAlive"
		self.managerName 		= "SealSnakeMgr"
		self.crondNoticeKey		= "SealSnakeMgr_start_notice"
		self.crondStartKey		= "SealSnakeMgr_start"
		self.crondEndKey		= "SealSnakeMgr_end"
		self._monsClassName		= "20724004"
		self.spaceName			= "liu_wang_mu_003"
		self.position			= ( 102.502, 30.681, 96.711 )
		self.direction			= ( 0, 0, 0 )
		WXActivityMgr.__init__( self )