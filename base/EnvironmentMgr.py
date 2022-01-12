# -*- coding: gb18030 -*-
#
#
import BigWorld
from bwdebug import *
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()

"""
新年的场景关键字: new_year_env
中秋的场景关键字: mid_autumn
"""

class EnvironmentMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.registerGlobally( "EnvironmentMgr", self._onRegisterManager )
		self.envMBGroup = {}			#such as { 1 :[ envMB01, envMB02, ], 2 : [], ... }
		self.currAcitivitys = set([])


	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register EnvironmentMgr Fail!" )
			self.registerGlobally( "EnvironmentMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["EnvironmentMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("EnvironmentMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
					  	"newYear_env_start" : "onNewYearEnvShowStart",
						"newYear_env_end" :	"onNewYearEnvShowEnd",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )

		crond.addAutoStartScheme( "newYear_env_start", self, "onNewYearEnvShowStart" )


	def addToMgr( self, envMB, festival_key ):
		"""
		define method
		"""
		if not festival_key in self.envMBGroup:
			self.envMBGroup[festival_key] = []
		
		self.envMBGroup[festival_key].append( envMB )
		
		if festival_key in self.currAcitivitys:
			envMB.cell.setVisible( True )
	
	def onNewYearEnvShowStart( self ):
		"""
		显示过年场景物件
		"""
		for i in self.envMBGroup["new_year_env"]:
			i.createCellEnviObject()
		self.currAcitivitys.add( "new_year_env" )
			
			
	
	def onNewYearEnvShowEnd( self ):
		"""
		隐藏过年场景物件
		"""
		for i in self.envMBGroup["new_year_env"]:
			i.destroyCellEnviObject()
		
		self.currAcitivitys.remove( "new_year_env" )