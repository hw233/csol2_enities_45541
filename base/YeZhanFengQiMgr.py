# -*- coding: gb18030 -*-
import time
import random
import BigWorld

from bwdebug import *
import csstatus
import csdefine
import csconst
import cschannel_msgs

import Love3
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from ObjectScripts.GameObjectFactory import GameObjectFactory

ACTIVITY_STATE_START 	= 1
ACTIVITY_STATE_END 		= 2

TIMER_ARG_READY = 1
TIMER_ARG_END = 2

GET_ENTER_SPACE_NUMBER_FULL 			= -1
GET_ENTER_SPACE_NUMBER_LEVEL_CLOSED 	= -2

SPACE_CLASS_NAME = "fu_ben_ye_zhan_feng_qi"

class YeZhanFengQiMgr( BigWorld.Base ):
	# 组队擂台管理器
	def __init__( self ):
		BigWorld.Base.__init__( self )
		self.registerGlobally( "YeZhanFengQiMgr", self._onRegisterManager )
		self.spaceType = SPACE_CLASS_NAME
		self.activityState = ACTIVITY_STATE_END
		self.activityStarTime = 0.0
		
		self.battlefieldInfos = {}
		self.spaceNumberEnters = {}
		
		self.minLevel = 0
		self.maxLevel = 0
		self.intervalLevel = 0
		self.minPlayer = 0
		self.maxPlayer = 0
		self.maxExit = 0
		self.minLevelPlayer = 0
		
		self.spaceLife = 0
		
		self.itemRequestInfos = {}
		self.waitListInfos = {}
		self.initConfigData( self.getScript() )
	
	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register YeZhanFengQiMgr Fail!" )
			self.registerGlobally( "YeZhanFengQiMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["YeZhanFengQiMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("YeZhanFengQiMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"YeZhanFengQi_notice" : "onNotice",
						"YeZhanFengQi_start" : "onStart",
						"YeZhanFengQi_end" : "onEnd",
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )
	
	def getScript( self ):
		return GameObjectFactory.instance().getObject( self.spaceType )
	
	def initConfigData( self, objScript ):
		"""
		初始化数据
		"""
		self.maxExit = objScript.maxExit
		self.minLevel = objScript.minLevel
		self.maxLevel = objScript.maxLevel
		self.intervalLevel = objScript.intervalLevel
		self.minPlayer = objScript.minPlayer
		self.maxPlayer = objScript.maxPlayer
		self.minLevelPlayer = objScript.minLevelPlayer
		self.prepareTime = objScript.prepareTime
		self.spaceLife = objScript.spaceLife
		
	def initBattlefieldData( self, minLevel, maxLevel, intervalLevel ):
		"""
		初始化战场数据
		"""
		cLevel = minLevel
		nextLevel = minLevel + intervalLevel
		while nextLevel < maxLevel:
			self.battlefieldInfos[ ( cLevel, nextLevel  ) ] = [ 0 for i in xrange( self.maxExit ) ]
			cLevel = nextLevel + 1
			nextLevel += intervalLevel
		self.battlefieldInfos[ ( cLevel, maxLevel  ) ] = [ 0 for i in xrange( self.maxExit ) ]
		
		self.spaceNumberEnters = {}
		
		# 为了安全起见，把排队进入信息也清除掉（调戏人员不要在别人进入的时候调用GM指令就好）
		self.itemRequestInfos = {}
		self.waitListInfos = {}
	
	def getBattlefieldItemKey( self, level ):
		"""
		获取key
		"""
		for k in self.battlefieldInfos.iterkeys():
			if k[ 0 ] <= level and k[ 1 ] >= level:
				return k
		
		return None
	
	def onNotice( self ):
		"""
		define method
		公告
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.WIZCOMMAND_YE_ZHAN_FENG_QI_NOTICE, [] )
		INFO_MSG( "YeZhanFengQiMgr", "notice", "" )
	
	def onStart( self ):
		"""
		define method.
		活动开始
		"""
		self.initBattlefieldData( self.minLevel, self.maxLevel, self.intervalLevel ) # 初始化战场数据
		self.activityState = ACTIVITY_STATE_START
		self.addTimer( self.prepareTime * 60, 0, TIMER_ARG_READY )
		self.addTimer( self.spaceLife * 60, 0,	 TIMER_ARG_END )
		self.activityStarTime = time.time()
		INFO_MSG( "YeZhanFengQiMgr", "start", "" )
	
	def onEnd( self ):
		"""
		define method.
		活动结束
		"""
		if self.activityState != ACTIVITY_STATE_START:
			return 
			
		self.activityState = ACTIVITY_STATE_END
		BigWorld.globalData[ "SpaceManager" ].remoteCallDomain( self.spaceType, "activityEnd", [] )
		self.activityStarTime = 0
		INFO_MSG( "YeZhanFengQiMgr", "end", "" )
	
	def requestEnterSpace( self, domainBase, position, direction, baseMailbox, params ):
		"""
		define method
		玩家申请进入战场
		"""
		if self.activityState == ACTIVITY_STATE_END: # 不在活动时间
			baseMailbox.client.onStatusMessage( csstatus.YE_ZHAN_FENG_QI_ACTIVITY_END, "" )
			return
			
		level = params[ "level" ] 
		enterNumber = self._getEnterSpaceNumber( level, [], 0 )
		k = self.getBattlefieldItemKey( level )
		if not self.battlefieldInfos.has_key( k ):
			baseMailbox.client.onStatusMessage( csstatus.YE_ZHAN_FENG_QI_CANNOT_ENTER, "" )
			return
			
		levelSpaceNumbers = self.battlefieldInfos[ k ]
		params[ "spaceKey" ] = enterNumber
		if enterNumber < 0:
			if enterNumber == GET_ENTER_SPACE_NUMBER_FULL:
			# 该等级段的三个战场进入人数全满
				baseMailbox.client.onStatusMessage( csstatus.YE_ZHAN_FENG_QI_ENTER_FULL, "" )
			elif enterNumber == GET_ENTER_SPACE_NUMBER_LEVEL_CLOSED:
				baseMailbox.client.onStatusMessage( csstatus.YE_ZHAN_FENG_QI_LEVEL_CLOSE, "" )
			return
		elif enterNumber != 0:
			self.spaceNumberEnters[ enterNumber ] += 1
		else:
			if self.itemRequestInfos.has_key( k ):
				if len( list( set( levelSpaceNumbers ) ^ set( [0] ) ) ) + self.itemRequestInfos[ k ] >= self.maxExit: # 一个等级段最多存在战场个数
					self.waitListInfos.append( [domainBase, position, direction, baseMailbox, params] )
					return
				else:
					self.itemRequestInfos[ k ] += 1
			else:
				self.itemRequestInfos[ k ] = 1
		
		params[ "spaceLevel" ] = k[1]
		params[ "actStartTime" ] = self.activityStarTime
		domainBase.teleportEntityMgr( position, direction, baseMailbox, params )
	
	def playerExit( self, spaceNumber, pMB ):
		"""
		define method
		玩家退出副本
		"""
		if self.spaceNumberEnters.has_key( spaceNumber ):
			self.spaceNumberEnters[ spaceNumber ] -= 1
	
	def _getEnterSpaceNumber( self, level, exceptNum = [] , rep = 0 ):
		# 获取进入ID
		if rep > self.maxExit: # 该等级段的三个战场进入人数全满
			return GET_ENTER_SPACE_NUMBER_FULL
		
		k = self.getBattlefieldItemKey( level )
		levelSpaceNumbers = self.battlefieldInfos[ k ]
		canEnterNumbers = list( set( levelSpaceNumbers) ^ set( exceptNum ) )
		if not len( canEnterNumbers ):
			return GET_ENTER_SPACE_NUMBER_LEVEL_CLOSED
			
		enterNumber = random.choice( canEnterNumbers )
		if enterNumber:
			if self.spaceNumberEnters[ enterNumber ] >= self.maxPlayer:
				exceptNum.append( enterNumber )
				return self._getEnterSpaceNumber( level, exceptNum, rep + 1 )
				
		return enterNumber
	
	def addNewSpaceNumber( self, level, spaceNumber ):
		"""
		define method
		创建了一个新的战场
		"""
		k = self.getBattlefieldItemKey( level )
		idx = self.battlefieldInfos[ k ].index( 0 )
		self.battlefieldInfos[ k ][ idx ] = spaceNumber
		self.spaceNumberEnters[ spaceNumber ] = 1
		copyList  = self.waitListInfos
		self.waitListInfos = []
		for wInf in copyList:
			self.requestEnterSpace( *wInf )
	
	def removeSpaceNumber( self, spaceNumber ):
		"""
		define method
		删除一个战场
		"""
		for key, value in self.battlefieldInfos.iteritems():
			if spaceNumber in value:
				idx = value.index( spaceNumber )
				value[ idx ] = 0
				break
	
	def checkEnter( self ):
		"""
		准备时间结束，检查进入人数是否合适
		"""
		closeNumber = []
		for k, v in self.spaceNumberEnters.iteritems():
			if v < self.minPlayer:
				closeNumber.append( k )
		
		for v in self.battlefieldInfos.itervalues():
			c = 0
			for num in v:
				if num in self.spaceNumberEnters:
					c += self.spaceNumberEnters[ num ]
				
			if c < self.minLevelPlayer: # 如果当前等级段的三个战场人数少于配置人数，则三个战场全关闭
				for num in v:
					if num not in closeNumber:
						closeNumber.append( num )
		
		closeNumber = list( set( closeNumber ) ^ set( [0] ) )
		for num in closeNumber:
			self.closeSpaceCopy( num )
	
	def closeSpaceCopy( self, spaceNumber ):
		"""
		关闭指定的副本
		"""
		if self.spaceNumberEnters.has_key( spaceNumber ):
			del self.spaceNumberEnters[ spaceNumber ]
		
		for v in self.battlefieldInfos.itervalues():
			if spaceNumber in v:
				v.remove( spaceNumber )
				break
				
		BigWorld.globalData[ "SpaceManager" ].remoteCallDomain( self.spaceType, "closeSpaceItem", [ spaceNumber ] )
	
	def onTimer( self, tid, arg ):
		# addTimer control
		if arg  == TIMER_ARG_READY:
			self.checkEnter()
		elif arg == TIMER_ARG_END:
			self.onEnd()
		