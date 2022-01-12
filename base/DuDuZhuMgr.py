# -*- coding: gb18030 -*-

import BigWorld
import cschannel_msgs
import ShareTexts as ST
from NormalActivityManager import NormalActivityManager

class DuDuZhuMgr( BigWorld.Base, NormalActivityManager ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.noticeMsg 			= cschannel_msgs.BCT_DUDUZHU_BEGIN_NOTIFY_0
		#self.startMsg 			= cschannel_msgs.BCT_DUDUZHU_BEGIN_NOTIFY
		#self.endMgs 			= cschannel_msgs.BCT_DUDUZHU_END_NOTIFY
		self.startMsg			= ""
		self.endMgs				= ""
		self.errorStartLog 		= cschannel_msgs.DUDUZHU_NOTICE_1
		self.errorEndLog 		= cschannel_msgs.DUDUZHU_NOTICE_2
		self.globalFlagKey		= "AS_DuDuZhu"
		self.spawnMonsterCount  = 30
		self.managerName 		= "DuDuZhuMgr"
		self.crondNoticeKey		= "duduzhu_start_notice"
		self.crondStartKey		= "duduzhu_Start"
		self.crondEndKey		= "duduzhu_End"
		NormalActivityManager.__init__( self )		



