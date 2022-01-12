# -*- coding:gb18030 -*-

from bwdebug import *
import BigWorld
import Love3
import cschannel_msgs
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()

class FruitMgr( BigWorld.Base ):
	"""
	魅力果树活动Mgr
	"""
	def __init__( self ):
		BigWorld.Base.__init__( self )
		self.registerGlobally( "FruitMgr", self.registerGlobalCB )

	def registerGlobalCB( self, success ):
		"""
		"""
		if success:
			BigWorld.globalData[ "FruitMgr" ] = self
			self.registerCrond()
		else:
			self.registerGlobally( "FruitMgr", self.registerGlobalCB )

	def registerCrond( self ):
		"""
		将自己注册到计划任务系统
		"""
		taskEvents = {
					  	"FruitMgr_start" : "onStart",
					  	"FruitMgr_end" : "onEnd",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )

	def onStart( self ):
		"""
		Define method.
		"""
		BigWorld.globalData["FruitStart"] = True
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_FRUIT_TREE_START, [] )
		INFO_MSG( "FruitMgr", "start", "" )

	def onEnd( self ):
		"""
		Define method.
		"""
		del BigWorld.globalData["FruitStart"]
		INFO_MSG( "FruitMgr", "end", "" )

