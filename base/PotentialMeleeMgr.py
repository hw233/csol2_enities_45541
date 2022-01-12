# -*- coding: gb18030 -*-
#
# 投机商人管理器 2008-12-25 SongPeifang
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

class PotentialMeleeMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# 把自己注册为globalData全局实体
		self.registerGlobally( "PotentialMeleeMgr", self._onRegisterManager )
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
			ERROR_MSG( "Register PotentialMeleeMgr Fail!" )
			self.registerGlobally( "PotentialMeleeMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["PotentialMeleeMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("PotentialMeleeMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"PotentialMelee_start" : "onStart",
						"PotentialMelee_end" : "onEnd",
					  }

		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )
		crond.addAutoStartScheme( "PotentialMelee_start", self, "onStart" )
		

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
		潜能乱斗开始
		"""
		if BigWorld.globalData.has_key( "AS_PotentialMelee" ):
			curTime = time.localtime()
			ERROR_MSG( "PotentialMelee is running，%i:%i try open。"%(curTime[3],curTime[4] ) )
			return
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_QNZD_WILL_OPEN, [] )
		self.checkStartMeleeTimerID = self.addTimer( 10 * 60, 0, 0 )
		INFO_MSG( "PotentialMeleeMgr", "start" )

	def onEnd( self ):
		"""
		define method.
		潜能乱斗结束
		"""
		if not BigWorld.globalData.has_key( "AS_PotentialMelee" ):
			curTime = time.localtime()
			ERROR_MSG( "PotentialMelee is over，%i:%i try close。"%(curTime[3],curTime[4] ) )
			return

		if BigWorld.globalData.has_key( "AS_PotentialMelee" ):
			del BigWorld.globalData[ "AS_PotentialMelee" ]

		self.delTimer( self.globalChatMeleeTimerID )
		self.globalChatMeleeTimerID = 0

		#self.checkEndMeleeTimerID = self.addTimer( 60, 0, 4*60 )
		#for s in self.meleeSpaces:
		#	s.cell.onMeleeMsg( 300 )
		INFO_MSG( "PotentialMeleeMgr", "end" )


	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		if self.checkStartMeleeTimerID == timerID:
			self.delTimer( self.checkStartMeleeTimerID )
			self.checkStartMeleeTimerID = 0
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_QNZD_IS_DOING, [] )
			BigWorld.globalData[ "AS_PotentialMelee" ] = True
			self.globalChatMeleeTimerID = self.addTimer( 3600, 0, 60*60 )
		elif self.globalChatMeleeTimerID == timerID:		# 间隔1小时通知一次
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_QNZD_IS_DOING, [] )
			self.globalChatMeleeTimerID = self.addTimer( 3600, 0, 60*60 )
			return
