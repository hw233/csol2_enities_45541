# -*- coding: gb18030 -*-
#

# $Id:  Exp $

import BigWorld
from bwdebug import *
import csdefine
import cschannel_msgs
import Love3
import time
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()


class CollectPointManager( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# 把自己注册为globalData全局实体
		self.registerGlobally( "CollectPointManager", self._onRegisterManager )

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register CollectPointManager Fail!" )
			# again
			self.registerGlobally( "CollectPointManager", self._onRegisterManager )
		else:
			BigWorld.globalData["CollectPointManager"] = self		# 注册到所有的服务器中
			INFO_MSG("CollectPointManager Create Complete!")
			self.registerCrond()



	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"collect_start_notice" : "onStartNotice",
					  	"collect_Start" : "onStart",
						"collect_End" :	"onEnd",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )

		crond.addAutoStartScheme( "collect_Start", self, "onStart" )

	def onStart( self ):
		"""
		define method.
		活动报名开始
		"""
		if BigWorld.globalData.has_key( "AS_collectStart" ) and BigWorld.globalData[ "AS_collectStart" ] == True:
			curTime = time.localtime()
			ERROR_MSG( "采集活动正在进行，%i点%i分试图再次开始采集活动。"%(curTime[3],curTime[4] ) )
			return
		BigWorld.globalData[ "AS_collectStart" ] = True
		INFO_MSG( "CollectPointManager" , "start", "" )


	def onEnd( self ):
		"""
		define method.
		活动报名结束
		"""
		if not BigWorld.globalData.has_key( "AS_collectStart" ):
			curTime = time.localtime()
			ERROR_MSG( "采集活动已经结束，%i点%i分试图再次结束采集活动。"%(curTime[3],curTime[4] ) )
			return
		BigWorld.globalData[ "AS_collectStart" ] = False
		INFO_MSG( "CollectPointManager" , "end", "" )

	def onStartNotice( self ):
		"""
		define method.
		活动开始通知
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TEAM_COLLECT, [] )
		INFO_MSG( "CollectPointManager" , "notice", "" )
