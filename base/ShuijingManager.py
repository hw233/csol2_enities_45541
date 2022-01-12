# -*- coding: gb18030 -*-
#

# $Id:  Exp $

import BigWorld
from bwdebug import *
import uuid
import csdefine
import cschannel_msgs
import Love3
import time
import csstatus
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()

TIME_CLOSE_SPACE = 1 * 60
THREE_CHECKPOINT = 3

class ShuijingItem:
	"""
	不同的队伍会产生不同的ShuijingItem
	"""
	def __init__( self, cmgr, playerEntitys, reqLevel, teamMailbox ):
		"""
		"""
		self.cmgr = cmgr
		self.playerEntitys = playerEntitys
		self.reqLevel = reqLevel
		self.shuijingKey = self._getShuijingUUID()
		self.currentSpaceMailBox = None
		self.teamMailbox = teamMailbox
		self.currentCheckPoint = 1
	
	def _getShuijingUUID( self ):
		"""
		获取水晶副本唯一识别码
		"""
		return str( uuid.uuid1() )
		
	def getShuijingKey( self ):
		"""
		获取水晶副本key
		"""
		return self.shuijingKey
	
	def start( self ):
		"""
		水晶副本开始
		"""
		spaceInfo = self.cmgr.getSpaceInfo( self.currentCheckPoint )
		for playerBaseMailbox in self.playerEntitys:
			playerBaseMailbox.cell.shuijingSpaceOnStart( self.shuijingKey, self.currentCheckPoint, spaceInfo[0], spaceInfo[1], spaceInfo[2] )
	
	def registerShuijingMB( self, baseMailbox ):
		if self.currentSpaceMailBox:
			self.currentSpaceMailBox.mgrDestorySelf()
		self.currentSpaceMailBox = baseMailbox
	
	def reEnter( self, playerBaseMailbox ):
		reCheckPoint = self.currentCheckPoint
		spaceInfo = self.cmgr.getSpaceInfo( reCheckPoint )
		playerBaseMailbox.cell.shuijingSpaceGoToCheckPoint( reCheckPoint, spaceInfo[0], spaceInfo[1], spaceInfo[2] )
		self.registerPlayer( playerBaseMailbox )
	
	def registerPlayer( self, playerBaseMailbox ):
		idList = []
		for mailbox in self.playerEntitys:
			idList.append( mailbox.id )
		if playerBaseMailbox.id not in idList:
			self.playerEntitys.append( playerBaseMailbox )
	
	def passCheckPointDoor( self ):
		self.currentCheckPoint += 1
		for mailbox in self.playerEntitys:
			mailbox.cell.set( "shuijing_checkPoint", self.currentCheckPoint )
	
	def getTeamMailbox( self ):
		return self.teamMailbox
		
	def endShuijing( self ):
		self.noticeCloseSpace()
		self.cmgr.destoryShuijing( self.shuijingKey )
	
	def noticeCloseSpace( self ):
		for player in self.playerEntitys:
			player.client.onStatusMessage( csstatus.SPACE_WILL_BE_CLOSED, "" )
	
	def onDestroyShuijing( self ):
		for player in self.playerEntitys:
			player.cell.shuijingSpaceOnEnd()
		if self.teamMailbox and BigWorld.globalData.has_key( "Shuijing_%i"%self.teamMailbox.id ):
			del BigWorld.globalData[ "Shuijing_%i"%self.teamMailbox.id ]
		self.cmgr.clearDBIDInfos( self.shuijingKey )
		if self.currentSpaceMailBox:
			self.currentSpaceMailBox.mgrDestorySelf()
	
	def leaveShuijing( self ):
		self.cmgr.onDestroyShuijing( self.shuijingKey )
		
	def playerLeave( self, playerBaseMailbox ):
		self.deletePlayer( playerBaseMailbox )
		playerBaseMailbox.cell.shuijingSpaceOnEnd()
		
	def deletePlayer( self, playerBaseMailbox ):
		for index,mailbox in enumerate( self.playerEntitys ):
			if mailbox.id == playerBaseMailbox.id:
				self.playerEntitys.pop( index )
		if self.playerEntitys:
			self.cmgr.onDestroyShuijing( self.shuijingKey )



class ShuijingManager( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# 把自己注册为globalData全局实体
		self.registerGlobally( "ShuijingManager", self._onRegisterManager )
		self._spaceInfo = {}
		self._shuijingDict = {}
		self._playerDbidToItem = {}
		self._destoryDict = {}
		self.initShuijingInfo()
		
	def initShuijingInfo( self ):
		"""
		初始化水晶副本信息
		"""
		if BigWorld.globalData.has_key( "shuijingTempList" ):
			shuijingTempList = BigWorld.globalData[ "shuijingTempList" ]
			for i in shuijingTempList:
				self._spaceInfo[ i[0] ] = ( i[1], i[2], i[3] )

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register ShuijingManager Fail!" )
			# again
			self.registerGlobally( "ShuijingManager", self._onRegisterManager )
		else:
			BigWorld.globalData["ShuijingManager"] = self		# 注册到所有的服务器中
			INFO_MSG("ShuijingManager Create Complete!")
			self.registerCrond()



	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"Shuijing_start_notice" : "onStartNotice",
					  	"Shuijing_Start" : "onStart",
						"Shuijing_End" :	"onEnd",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )

		crond.addAutoStartScheme( "Shuijing_Start", self, "onStart" )

	def onStart( self ):
		"""
		define method.
		活动报名开始
		"""
		if BigWorld.globalData.has_key( "AS_shuijingStart" ) and BigWorld.globalData[ "AS_shuijingStart" ] == True:
			curTime = time.localtime()
			ERROR_MSG( "水晶副本活动正在进行，%i点%i分试图再次开始水晶副本。"%(curTime[3],curTime[4] ) )
			return
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_SJFB_BEGIN_NOTIFY, [] )
		BigWorld.globalData[ "AS_shuijingStart" ] = True
		INFO_MSG( "ShuijingManager", "start", "" )

	def onEnd( self ):
		"""
		define method.
		活动报名结束
		"""
		if not BigWorld.globalData.has_key( "AS_shuijingStart" ):
			curTime = time.localtime()
			ERROR_MSG( "水晶副本活动已经结束，%i点%i分试图再次结束水晶副本。"%(curTime[3],curTime[4] ) )
			return
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_SJFB_END_NOTIFY, [] )
		BigWorld.globalData[ "AS_shuijingStart" ] = False
#		if BigWorld.globalData.has_key("shuijing_monsterCount"):
#			del BigWorld.globalData[ "shuijing_monsterCount" ]
		INFO_MSG( "ShuijingManager", "end", "" )


	def onStartNotice( self ):
		"""
		define method.
		活动开始通知
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_SJFB_BEGIN_NOTIFY_0, [] )
		INFO_MSG( "ShuijingManager", "notice", "" )
		
#	def setShuijingMonsterCount( self, monsterCount ):
#		"""
#		设置怪物总数量
#		"""
#		if BigWorld.globalData.has_key("shuijing_monsterCount"):
#			return
#		else:
#			BigWorld.globalData["shuijing_monsterCount"] = monsterCount
			
	def registerShuijingInfo( self, checkPoint, className, enterPosition, enterDirection ):
		"""
		注册水晶副本信息
		"""
		self._spaceInfo[ checkPoint ] = ( className, enterPosition, enterDirection )
	
	def registerShuijingMB( self, shuijingKey, baseMailbox ):
		if self._shuijingDict.has_key( shuijingKey ):
			self._shuijingDict[ shuijingKey ].registerShuijingMB( baseMailbox )
	
	def onRequestShuijing( self, entities, dbidList, reqLevel, teamMailbox):
		sItem = ShuijingItem( self, entities, reqLevel, teamMailbox )
		self._shuijingDict[ sItem.getShuijingKey() ] = sItem
		sItem.start()
		for dbid in dbidList:
			self._playerDbidToItem[ dbid ] = sItem
		BigWorld.globalData[ 'Shuijing_%i'%teamMailbox.id ] = sItem.getShuijingKey()
		
	def getSpaceInfo( self, checkPoint ):
		if self._spaceInfo.has_key( checkPoint ):
			return self._spaceInfo[ checkPoint ]
		else:
			return None
		
	def reEnter( self, shuijingKey, playerBaseMailbox ):
		if self._shuijingDict.has_key( shuijingKey ):
			self._shuijingDict[ shuijingKey ].reEnter( playerBaseMailbox )
		else:
			playerBaseMailbox.cell.shuijingSpaceIsTimeOut()
		pass

	def passCheckPointDoor( self, shuijingKey ):
		if self._shuijingDict.has_key( shuijingKey ):
			self._shuijingDict[ shuijingKey ].passCheckPointDoor()
			
	def endShuijing( self, shuijingKey ):
		if self._shuijingDict.has_key( shuijingKey ):
			self._shuijingDict[ shuijingKey ].endShuijing()
			
	def destoryShuijing( self, shuijingKey ):
		timerID = self.addTimer( TIME_CLOSE_SPACE )
		self._destoryDict[ timerID ] = shuijingKey
			
			
	def onTimer( self, id, userArg ):
		shuijingKey = self._destoryDict[ id ]
		if shuijingKey:
			self._destoryDict.pop( id )
			self.onDestroyShuijing( shuijingKey )
			
	def onDestroyShuijing( self, shuijingKey ):
		if self._shuijingDict.has_key( shuijingKey ):
			self._shuijingDict[ shuijingKey ].onDestroyShuijing()
			self._shuijingDict.pop( shuijingKey )
			for tid,cid in self._destoryDict.iteritems():
				if cid == shuijingKey:
					self.delTimer( tid )
	
	def clearDBIDInfos( self, shuijingKey ):
		clearList = []
		for dbid,sItem in self._playerDbidToItem.iteritems():
			if sItem.getShuijingKey() == shuijingKey:
				clearList.append( dbid )
		for dbid in clearList:
			self._playerDbidToItem.pop( dbid )
			
	def leaveShuijing( self, shuijingKey ):
		if self._shuijingDict.has_key( shuijingKey ):
			self._shuijingDict[ shuijingKey ].leaveShuijing()
	
	def playerLeave( self, shuijingKey, playerBaseMailbox ):
		if self._shuijingDict.has_key( shuijingKey ):
			self._shuijingDict[ shuijingKey ].playerLeave( playerBaseMailbox )


#g_shuijingMgr = ShuijingManager()