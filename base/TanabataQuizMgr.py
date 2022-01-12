# -*- coding:gb18030 -*-

from bwdebug import *
import BigWorld
import Love3
import cschannel_msgs
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()

class TanabataQuizMgr( BigWorld.Base ):
	"""
	七夕情感问答管理器
	"""
	def __init__( self ):
		BigWorld.Base.__init__( self )
		self.registerGlobally( "TanabataQuizMgr", self.registerGlobalCB )
		
	def registerGlobalCB( self, success ):
		"""
		"""
		if success:
			BigWorld.globalData[ "TanabataQuizMgr" ] = self
			self.registerCrond()
		else:
			self.registerGlobally( "TanabataQuizMgr", self.registerGlobalCB )
			
	def registerCrond( self ):
		"""
		将自己注册到计划任务系统
		"""
		taskEvents = {
					  	"TanabataQuizMgr_start" : "onStart",
					  	"TanabataQuizMgr_end" : "onEnd",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )
				
	def onStart( self ):
		"""
		Define method.
		"""
		BigWorld.globalData["TanabataQuizStart"] = True
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TANABATA_QUIZ_START, [] )
		INFO_MSG( "TanabataQuizMgr", "start", "" )
		
	def onEnd( self ):
		"""
		Define method.
		"""
		del BigWorld.globalData["TanabataQuizStart"]
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TANABATA_QUIZ_FINISH, [] )
		INFO_MSG( "TanabataQuizMgr", "end", "" )

		
		