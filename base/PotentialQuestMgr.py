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

class PotentialQuestMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# 把自己注册为globalData全局实体
		self.registerGlobally( "PotentialQuestMgr", self._onRegisterManager )
		self._npcs = {}
		
	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register PotentialQuestMgr Fail!" )
			self.registerGlobally( "PotentialQuestMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["PotentialQuestMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("PotentialQuestMgr Create Complete!")

	def onRegisterPotentialObject( self, playerDBID, npcBaseMailbox ):
		"""
		define method.
		注册某个玩家接潜能任务的NPC
		"""
		DEBUG_MSG( playerDBID, npcBaseMailbox )
		if playerDBID in self._npcs:
			npc = self._npcs.pop( playerDBID )
			if hasattr( npc, "cell" ) and npc.cell:
				npc.cell.remoteScriptCall( "onDestroySelf", () )
				
		self._npcs[ playerDBID ] = npcBaseMailbox
	
	def onUnRegisterPotentialObject( self, playerDBID ):
		"""
		define method.
		反注册某个玩家接潜能任务的NPC
		"""
		DEBUG_MSG( playerDBID )
		if playerDBID in self._npcs:
			npc = self._npcs.pop( playerDBID )
			if hasattr( npc, "cell" ) and npc.cell:
				npc.cell.remoteScriptCall( "onDestroySelf", () )
