# -*- coding: gb18030 -*-


import BigWorld
import cschannel_msgs
import ShareTexts as ST
from bwdebug import *

from NormalActivityManager import NormalActivityManager



class HundunMgr( BigWorld.Base, NormalActivityManager ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.noticeMsg 			= cschannel_msgs.BCT_HUNDUN_BEGIN_NOTIFY_0
		self.startMsg 			= cschannel_msgs.BCT_HUNDUN_BEGIN_NOTIFY
		self.endMgs 			= cschannel_msgs.BCT_HUNDUN_END_NOTIFY
		self.errorStartLog 		= cschannel_msgs.HUN_DUN_RU_QIN_NOTICE_1
		self.errorEndLog 		= cschannel_msgs.HUN_DUN_RU_QIN_NOTICE_2
		self.globalFlagKey		= "AS_Hundun"
		self.spawnMonsterCount  = 40
		self.managerName 		= "HundunMgr"
		self.crondNoticeKey		= "hundun_start_notice"
		self.crondStartKey		= "hundun_Start"
		self.crondEndKey		= "hundun_End"
		NormalActivityManager.__init__( self )		



