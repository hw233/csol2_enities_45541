# -*- coding: gb18030 -*-


import BigWorld
import cschannel_msgs
import ShareTexts as ST
from bwdebug import *
from NormalActivityManager import NormalActivityManager



class YayuMgr( BigWorld.Base, NormalActivityManager ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.noticeMsg 			= cschannel_msgs.BCT_YAYU_BEGIN_NOTIFY_0
		self.startMsg 			= cschannel_msgs.BCT_YAYU_BEGIN_NOTIFY
		self.endMgs 			= cschannel_msgs.BCT_YAYU_END_NOTIFY
		self.errorStartLog 		= cschannel_msgs.YA_YU_VOICE2
		self.errorEndLog 		= cschannel_msgs.YA_YU_VOICE3
		self.globalFlagKey		= "AS_yayuStart"
		self.spawnMonsterCount  = 40
		self.managerName 		= "YayuMgr"
		self.crondNoticeKey		= "yayu_start_notice"
		self.crondStartKey		= "yayu_Start"
		self.crondEndKey		= "yayu_End"
		NormalActivityManager.__init__( self )		



