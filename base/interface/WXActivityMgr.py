# -*- coding: gb18030 -*-
#
# WX管理器 2009-10-07 SongPeifang
#

from csconst import g_maps_info
from bwdebug import *
from CrondDatas import CrondDatas
import BigWorld
import Love3

g_CrondDatas = CrondDatas.instance()


class WXActivityMgr:

	def __init__(self):
		"""
		白蛇妖、巨灵魔、堕落猎人、疯狂祭师、撼地大将、啸天大将
		的基类管理器
		"""
		#self.noticeMsg 		= ""
		#self.startMsg 			= ""
		#self.endMgs 			= ""
		#self.globalFlagKey		= ""
		#self.managerName 		= ""
		#self.crondNoticeKey	= ""
		#self.crondStartKey		= ""
		#self.crondEndKey		= ""
		#self._monsClassName	= ""
		#self.spaceName			= ""
		#self.position			= ( 0, 0, 0 )
		#self.direction			= ( 0, 0, 0 )
		self.initActivity()
		self.registerGlobally( self.managerName, self._onRegisterManager )


	def initActivity( self ):
		"""
		"""
		BigWorld.globalData[ self.globalFlagKey ] = False


	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register %s Fail!" % self.managerName )
			self.registerGlobally( self.managerName, self._onRegisterManager )
		else:
			BigWorld.globalData[self.managerName] = self		# 注册到所有的服务器中
			INFO_MSG( "%s Create Complete!" % self.managerName )
			self.registerCrond()


	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
					  	self.crondNoticeKey : "onStartNotice",
					  	self.crondStartKey : "onStart",
						self.crondEndKey :	"onEnd",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )


	def onStartNotice( self ):
		"""
		define method.
		活动开始通知
		"""
		if self.noticeMsg != "":
			Love3.g_baseApp.anonymityBroadcast( self.noticeMsg, [] )


	def onStart( self ):
		"""
		define method.
		怪物刷出
		"""
		self.spawnMonster()


	def spawnMonster( self ):
		"""
		"""
		if not g_maps_info.has_key( self.spaceName ):
			ERROR_MSG( "%s地图信息生成错误，或者地图列表已过期！" % self.managerName )
			return
		npcSpaceNameCh = g_maps_info[ self.spaceName ]	# 地图的中文名，如“凤鸣”
		if not BigWorld.globalData.has_key( self.globalFlagKey ) or BigWorld.globalData[self.globalFlagKey] == False:
			BigWorld.globalData["SpaceManager"].createCellNPCObjectFormBase( self.spaceName, self._monsClassName, self.position, self.direction, {"spawnPos" : self.position} )
		BigWorld.globalData[ self.globalFlagKey ] = True
		if self.startMsg != "":
			Love3.g_baseApp.anonymityBroadcast( self.startMsg, [] )


	def onEnd( self ):
		"""
		define method
		"""
		if self.endMgs != "":
			Love3.g_baseApp.anonymityBroadcast( self.endMgs, [] )
		
		BigWorld.globalData[ self.globalFlagKey ] = False