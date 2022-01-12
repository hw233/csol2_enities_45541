# -*- coding: gb18030 -*-

from bwdebug import *
import BigWorld
import Love3
import csdefine
import csconst
import cschannel_msgs
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()


TEN_MIN = 10 * 60			# 10分钟
FIVE_MIN = 5 * 60			# 5分钟
ONE_MIN = 60				# 1分钟
TWENTY_MIN = 20 * 60		# 20分钟
TOW_HOUR = 	2 * 3600		# 2小时

NOTIFY_MAX_COUNT = TOW_HOUR / TWENTY_MIN - 2	# 活动中一共要通知几次，开始和结束不需要通知。

# timer id
TIMER_TEN_MIN_REMAIN = 1	# 活动开始前10分钟的timer
TIMER_FIVE_MIN_REMAIN = 2	# 活动开始前5分钟的timer
TIMER_ONE_MIN_REMAIN = 3	# 活动开始前1分钟的timer
TIMER_ACTIVITY_START = 4	# 活动开始
TIMER_ACTIVITY_END = 5		# 活动结束
TIMER_ACTIVITY_BEING = 6	# 活动进行中


class LuckyBoxActivityMgr( BigWorld.Base ):
	"""
	天降宝盒活动管理器
	"""
	def __init__( self ):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.activityNotifyCount = 0	# 活动进行中通知次数

		self.registerGlobally( "LuckyBoxActivityMgr", self.registerGloballyCB )


	def registerGloballyCB( self, complete ):
		"""
		注册全局实例的回调
		"""
		if not complete:
			ERROR_MSG( "--->>>Register globally error." )
			self.registerGlobally( "LuckyBoxActivityMgr", self.registerGloballyCB )
		else:
			BigWorld.globalData[ "LuckyBoxActivityMgr" ] = self
			INFO_MSG( "--->>>Register globally complete." )
			self.registerCrond()

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		crond = BigWorld.globalData["Crond"]
		for taskEventKey, taskEvents in csconst.DROP_TASKEVENTS.iteritems():
			for taskName, callbackName in taskEvents.iteritems():
				for cmd in g_CrondDatas.getTaskCmds( taskName ):
					crond.addScheme( cmd, self, callbackName )
			crond.addAutoStartScheme( taskEventKey, self, taskEvents[taskEventKey] )
		BigWorld.globalData["LuckyActivity"] = {}
		
	def onStartLuckyBox( self ):
		"""
		define method.
		天降宝盒活动开始通知
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TJBH_TIMER_ACTIVITY_START, [] )
		# BigWorld.globalData[ key ] = csconst.LUCKY_BOX_DROP_RATE
		f = BigWorld.globalData["LuckyActivity"]
		f["AS_LuckyBoxActivityStart"] = csdefine.RCG_LUCKY_BOX
		BigWorld.globalData["LuckyActivity"] = f
		self.addTimer( TWENTY_MIN, 0, TIMER_ACTIVITY_BEING )		# 二十分钟后发一个活动中的通知
		INFO_MSG( "LuckyBoxActivityMgr", "start", "Lucky" )
			
	def onStartMidAut( self ):
		"""
		define method.
		中秋掉落活动开始通知
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_MADROP_ACTIVITY_START, [] )
		f = BigWorld.globalData["LuckyActivity"]
		f["AS_MidActivityStart"] = csdefine.RCG_MID_AUTUMN
		BigWorld.globalData["LuckyActivity"] = f
		INFO_MSG( "LuckyBoxActivityMgr", "start", "MidAut" )

	def onTimer( self, controllerID, userArg ):
		"""
		"""
		if userArg == TIMER_ACTIVITY_BEING:
			self.activityNotifyCount += 1
			DEBUG_MSG( "---->>.NOTIFY" )
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TJBH_TIMER_ACTIVITY_BEING, [] )
			if self.activityNotifyCount < NOTIFY_MAX_COUNT:
				self.addTimer( TWENTY_MIN, 0, TIMER_ACTIVITY_BEING )	# 二十分钟后发一个活动中的通知
			elif self.activityNotifyCount == NOTIFY_MAX_COUNT:
				self.activityNotifyCount = 0
			
	def onEndLuckyBox( self ):
		"""
		关闭天降宝盒活动
		"""
		# 防止服务器在活动开始时间之后启动 则找不到该标记
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TJBH_TIMER_ACTIVITY_END, [] )
		if BigWorld.globalData["LuckyActivity"].has_key( "AS_LuckyBoxActivityStart" ):
			f = BigWorld.globalData["LuckyActivity"]
			f.pop( "AS_LuckyBoxActivityStart" )
			BigWorld.globalData["LuckyActivity"] = f
		
		INFO_MSG( "LuckyBoxActivityMgr", "end", "Lucky" )
			
	def onEndMidAut( self ):
		"""
		关闭中秋掉落活动
		"""
		# 防止服务器在活动开始时间之后启动 则找不到该标记
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_MADROP_ACTIVITY_END, [] )
		if BigWorld.globalData["LuckyActivity"].has_key( "AS_MidActivityStart" ):
			f = BigWorld.globalData["LuckyActivity"]
			f.pop( "AS_MidActivityStart" )
			BigWorld.globalData["LuckyActivity"] = f
		
		INFO_MSG( "LuckyBoxActivityMgr", "end", "MidAut" )
		
	def onStartLuckyBoxNotice( self ):
		"""
		define method.
		天降宝盒活动开始通知
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TJBH_TIMER_TEN_MIN_REMAIN, [] )
		INFO_MSG( "LuckyBoxActivityMgr", "notice", "Lucky" )
		
	def onStartMidAutNotice( self ):
		"""
		define method.
		中秋掉落活动开始通知
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_MADROP_ACTIVITY_START, [] )
		INFO_MSG( "LuckyBoxActivityMgr", "notice", "MidAut" )