# -*- coding: gb18030 -*-
#
# 封印巨灵魔管理器 2009-05-25 SongPeifang
#

from interface.WXActivityMgr import WXActivityMgr
import cschannel_msgs
import BigWorld


class SealJuLingMgr( BigWorld.Base, WXActivityMgr ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.noticeMsg 			= cschannel_msgs.BCT_FYJLM_BEGAIN_0
		self.startMsg 			= cschannel_msgs.BCT_FYJLM_BEGAIN
		self.endMgs 			= ""
		self.globalFlagKey		= "JuLingMoAlive"
		self.managerName 		= "SealJuLingMgr"
		self.crondNoticeKey		= "SealJuLingMgr_start_notice"
		self.crondStartKey		= "SealJuLingMgr_start"
		self.crondEndKey		= "SealJuLingMgr_end"
		self._monsClassName		= "20714002"
		self.spaceName			= "liu_wang_mu_006"
		self.position			= ( 63.41, 24.813, -33.875 )
		self.direction			= ( 0, 0, 0 )
		WXActivityMgr.__init__( self )