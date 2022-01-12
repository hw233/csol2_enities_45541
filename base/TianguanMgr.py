# -*- coding: gb18030 -*-
#

# $Id: DartManager.py,v 1.1 2008-09-05 03:41:04 zhangyuxing Exp $

import Love3
import BigWorld
from bwdebug import *
from Function import Functor
import csstatus
import Love3
import csdefine
import cschannel_msgs
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
import time

"""
定时活动 -- 闯天关
"""


TIANGUAN_START = 1
TIANGUAN_RELOAD = 6

class TianguanMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# 把自己注册为globalData全局实体
		self.registerGlobally( "TianguanMgr", self._onRegisterManager )

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register TianguanMgr Fail!" )
			# again
			self.registerGlobally( "TianguanMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["TianguanMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("TianguanMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"TianguanMgr_start_notice" : "onStartNotice",
					  	"TianguanMgr_start" : "onStart",
					  	"TianguanMgr_end" : "onEnd",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )
		crond.addAutoStartScheme( "TianguanMgr_start", self, "onStart" )

	def onStart( self ):
		"""
		define method.
		活动开始
		"""
		if BigWorld.globalData.has_key( "AS_Tianguan" ):
			curTime = time.localtime()
			ERROR_MSG( "天关活动正在进行，%i点%i分试图再次开始天关。"%(curTime[3],curTime[4] ) )
			return
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TGHD_WILL_OPEN_NOTIFY , [])
		BigWorld.globalData[ "AS_Tianguan" ] = True
		INFO_MSG( "TianguanMgr", "start", "" )

	def onEnd( self ):
		"""
		define method.
		活动结束
		"""
		# 防止服务器在活动开始时间之后启动 则找不到该标记
		if not BigWorld.globalData.has_key( "AS_Tianguan" ):
			curTime = time.localtime()
			ERROR_MSG( "天关活动已经结束，%i点%i分试图再次结束天关。"%(curTime[3],curTime[4] ) )
			return

		if BigWorld.globalData.has_key( "AS_Tianguan" ):
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TGHD_WILL_OPEN_NOTIFY, [] )
			del BigWorld.globalData[ "AS_Tianguan" ]
		
		INFO_MSG( "TianguanMgr", "end", "" )

	def onStartNotice( self ):
		"""
		define method.
		活动开始通知
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TGHD_BEGIN_NOTIFY, [] )
		INFO_MSG( "TianguanMgr", "notice", "" )