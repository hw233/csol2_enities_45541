# -*- coding: gb18030 -*-
import BigWorld
import cschannel_msgs
import ShareTexts as ST
from bwdebug import *

from NormalActivityManager import NormalActivityManager

class ZeroMgr( BigWorld.Base, NormalActivityManager ):
	#零点时刻管理器，用于处于各种在零点时刻的一些处理

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.noticeMsg 			= ""
		self.startMsg 			= ""
		self.endMgs 			= ""
		self.errorStartLog 		= ""
		self.errorEndLog 		= "ZeroMgr Error Log!"
		self.globalFlagKey		= "ZeroMgr"
		self.managerName 		= "ZeroMgr"
		self.crondNoticeKey		= "Zero_start_notice"
		self.crondStartKey		= "Zero_Start"
		self.crondEndKey		= "Zero_End"
		NormalActivityManager.__init__( self )	
		
	def onStart( self ):
		"""
		define method.
		活动开始
		"""
		if BigWorld.globalData.has_key( self.globalFlagKey ) and BigWorld.globalData[self.globalFlagKey] == True:
			curTime = time.localtime()
			ERROR_MSG( self.errorStartLog%(curTime[3],curTime[4] ) )
			return
		BigWorld.globalData[self.globalFlagKey] = True
		if self.startMsg != "":
			Love3.g_baseApp.anonymityBroadcast( self.startMsg, [] )
		INFO_MSG( self.globalFlagKey, "start", "" )
		self.dealreflashDanceKingBuff()  #在零点刷新有舞厅buff的buff持续时间
		
	def dealreflashDanceKingBuff(self):
		#在零点刷新有舞厅buff的buff持续时间
		DEBUG_MSG("deal player's dancebuff at 00:00!")
		for e in self.globalData.itervalues():
			e.cell.dealreflashDanceKingBuff()
		DEBUG_MSG("deal player's dancebuff over!")
		