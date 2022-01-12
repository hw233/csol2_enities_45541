# -*- coding: gb18030 -*-
import BigWorld
import cschannel_msgs
import ShareTexts as ST
from bwdebug import *

from NormalActivityManager import NormalActivityManager

class AuditionMgr( BigWorld.Base, NormalActivityManager ):
	#劲舞时刻

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.noticeMsg 			= cschannel_msgs.BCT_AUDITION_BEGIN_NOTIFY_0
		self.startMsg 			= cschannel_msgs.BCT_AUDITION_BEGIN_NOTIFY
		self.endMgs 			= cschannel_msgs.BCT_AUDITION_END_NOTIFY
		self.errorStartLog 		= cschannel_msgs.AUDITION_NOTICE_1
		self.errorEndLog 		= cschannel_msgs.AUDITION_NOTICE_2
		self.spaceCopyAuditions = []
		self.globalFlagKey		= "AS_Audition"
		self.spawnMonsterCount  = 40
		self.managerName 		= "AuditionMgr"
		self.crondNoticeKey		= "Audition_start_notice"
		self.crondStartKey		= "Audition_Start"
		self.crondEndKey		= "Audition_End"
		NormalActivityManager.__init__( self )	
	
	def regesiterSpaceCopyAudition(self, baseMailBox):
		#define method,call when spaceCopyAudition created
		#danceSpaceCopy
		if baseMailBox not in self.spaceCopyAuditions:
			self.spaceCopyAuditions.append(baseMailBox)
	
	def removeSpaceCopyAudition(self, baseMailBox):
		#define method ,call when spaceCopyAudition destroied
		#danceSpaceCopy
		if baseMailBox in self.spaceCopyAuditions:
			self.spaceCopyAuditions.pop(baseMailBox)
		
