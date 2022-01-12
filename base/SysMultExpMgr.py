# -*- coding: gb18030 -*-
#
# 系统多倍经验活动 kebiao
#
import Love3
import csdefine
import cschannel_msgs
import BigWorld
import random
import Math
from bwdebug import *
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()

CONST_EXP_RATE = 1.0

class SysMultExpMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# 把自己注册为globalData全局实体
		self.registerGlobally( "SysMultExpMgr", self._onRegisterManager )

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register SysMultExpMgr Fail!" )
			self.registerGlobally( "SysMultExpMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["SysMultExpMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("SysMultExpMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"SysMultExpMgr_ready" : "onReady",
						"SysMultExpMgr_start2" : "onStart2",
						"SysMultExpMgr_end2" : "onEnd2",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )

		crond.addAutoStartScheme( "SysMultExpMgr_start2", self, "onStart2" )

	def onReady( self ):
		"""
		define method.
		通知10分钟之后开始
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_DBJY_WILL_BEGIN_NOTIFY, [] )
		INFO_MSG( "SysMultExpMgr", "notice", "" )
		

	def open( self, mult ):
		"""
		define method.
		2倍经验开始
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_DBJY_GODSEND_NOTIFY % ( mult * 100 ), [] )
		BigWorld.globalData[ "AS_SysMultExp" ] = mult

	def onStart2( self ):
		"""
		define method.
		2倍经验开始
		"""
		self.open( CONST_EXP_RATE )
		INFO_MSG( "SysMultExpMgr", "start", "" )

	def onEnd2( self ):
		"""
		define method.
		2倍经验结束
		"""
		if BigWorld.globalData.has_key( "AS_SysMultExp" ):
			del BigWorld.globalData[ "AS_SysMultExp" ]
		
		INFO_MSG( "SysMultExpMgr", "end", "" )
