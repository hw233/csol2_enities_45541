# -*- coding: gb18030 -*-


import BigWorld
import cschannel_msgs
from NormalActivityManager import NormalActivityManager




class TianjiangqishouMgr( BigWorld.Base, NormalActivityManager ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.noticeMsg 			= cschannel_msgs.BCT_TIANJIANGQISHOU_BEGIN_NOTIFY_0
		self.startMsg 			= cschannel_msgs.BCT_TIANJIANGQISHOU_BEGIN_NOTIFY
		self.endMgs 			= cschannel_msgs.BCT_TIANJIANGQISHOU_END_NOTIFY
		self.errorStartLog 		= cschannel_msgs.TIANJIANGQISHOUMGR_NOTICE_1
		self.errorEndLog 		= cschannel_msgs.TIANJIANGQISHOUMGR_NOTICE_2
		self.globalFlagKey		= "AS_Tianjiangqishou"
		self.spawnMonsterCount  = 30
		self.managerName 		= "TianjiangqishouMgr"
		self.crondNoticeKey		= "tianjiangqishou_start_notice"
		self.crondStartKey		= "tianjiangqishou_Start"
		self.crondEndKey		= "tianjiangqishou_End"
		NormalActivityManager.__init__( self )

