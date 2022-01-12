# -*- coding: gb18030 -*-
#
# 经验乱斗管理器
#
import Love3
import csdefine
import BigWorld
import random
import Math
import time
import cschannel_msgs
from bwdebug import *
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()

class ExpMeleeMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# 把自己注册为globalData全局实体
		self.registerGlobally( "ExpMeleeMgr", self._onRegisterManager )
		self.checkStartMeleeTimerID = 0
		#self.checkEndMeleeTimerID = 0
		#self.meleeSpaces = []
		self.globalChatMeleeTimerID = 0

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register ExpMeleeMgr Fail!" )
			self.registerGlobally( "ExpMeleeMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["ExpMeleeMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("ExpMeleeMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"ExpMelee_start" : "onStart",
						"ExpMelee_end" : "onEnd",
					  }
		
		crond = BigWorld.globalData["Crond"]
		
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )
		
		crond.addAutoStartScheme( "ExpMelee_start", self, "onStart" )
		

	def onRegisterSpace( self, spaceBase ):
		"""
		define method.
		注册所有开启的活动副本base
		"""
		return
		self.meleeSpaces.append( spaceBase )

	def onUnRegisterSpace( self, spaceBaseID ):
		"""
		define method.
		取消注册活动副本base
		"""
		return
		for i, s in enumerate( self.meleeSpaces ):
			if s.id == spaceBaseID:
				self.meleeSpaces.pop( i )
				return

	def onStart( self ):
		"""
		define method.
		经验乱斗开始
		"""
		if BigWorld.globalData.has_key( "AS_ExpMelee" ):
			curTime = time.localtime()
			ERROR_MSG( "经验乱斗活动正在进行，%i点%i分试图再次开始经验乱斗。"%(curTime[3],curTime[4] ) )
			return
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_JYLD_PRE_NOTIFY, [] )
		self.checkStartMeleeTimerID = self.addTimer( 10 * 60, 0, 0 )
		INFO_MSG( "ExpMeleeMgr", "start", "" )

	def onEnd( self ):
		"""
		define method.
		经验乱斗结束
		"""
		if not BigWorld.globalData.has_key( "AS_ExpMelee" ):
			curTime = time.localtime()
			ERROR_MSG( "经验乱斗活动已经结束，%i点%i分试图再次关闭经验乱斗。"%(curTime[3],curTime[4] ) )
			return

		if BigWorld.globalData.has_key( "AS_ExpMelee" ):
			del BigWorld.globalData[ "AS_ExpMelee" ]

		self.delTimer( self.globalChatMeleeTimerID )
		self.globalChatMeleeTimerID = 0
		
		INFO_MSG( "ExpMeleeMgr", "end", "" )


		#self.checkEndMeleeTimerID = self.addTimer( 60, 0, 4*60 )
		#for s in self.meleeSpaces:
		#	s.cell.onMeleeMsg( 300 )

	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		if self.checkStartMeleeTimerID == timerID:
			self.delTimer( self.checkStartMeleeTimerID )
			self.checkStartMeleeTimerID = 0
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_JYLD_IS_DOING, [] )
			self.globalChatMeleeTimerID = self.addTimer( 3600, 0, 60*60 )
			BigWorld.globalData[ "AS_ExpMelee" ] = True
		elif self.globalChatMeleeTimerID == timerID:		# 间隔1小时通知一次
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_JYLD_IS_DOING, [] )
			self.globalChatMeleeTimerID = self.addTimer( 3600, 0, 60*60 )