# -*- coding: gb18030 -*-
import copy
import random
import math
import time
import uuid
import cPickle

import BigWorld

import Love3
from bwdebug import *
import csdefine
import csconst
import csstatus
import cschannel_msgs
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
import items
g_items = items.instance()

from AoZhanMgrData import AoZhanRoundNoFailure
from AoZhanMgrData import AoZhanRoundHasFailure
from AoZhanMgrData import AO_ZHEN_FAILURE_ENTER_NUM

AO_ZHAN_MAX_JOIN = 64

AO_ZHAN_FAILURE_RECORD	= 32	#32强后开始记录失败者
AO_ZHAN_MIN_JOIN		= 1		#需要多少人参与才能开启比赛

GET_ATHLETICS_SPACE_NUMBER = lambda matchType, roomNum: matchType * 10000 + roomNum
GET_ATHLETICS_MATCH_TYPE = lambda spaceNumber: spaceNumber / 10000
GET_ATHLETICS_ROOM_NUM = lambda spaceNumber: spaceNumber % 10000

#管理器状态
MGR_STATE_FREE 			= 0	#没比赛期间
MGR_STATE_NOFITY		= 1	#公告
MGR_STATE_SIGNUP		= 2	#报名
MGR_STATE_ENTER			= 3	#入场
MGR_STATE_UNDERWAY		= 4	#比赛中
MGR_STATE_HALF_TIME		= 5	#中场休息

#timer arg
TIMER_ARG_READY			= 1
TIMER_ARG_ROUND			= 2
TIMER_ARG_NEXT			= 3
TIMER_ARG_CLEAR			= 4

#时间
TIME_READY		= 1 * 60	#准备
TIME_ROUND		= 3 * 60	#一轮比赛
TIME_NEXT		= 1 * 60 	#开启下轮比赛
TIME_CLEAR		= 10* 60	#清除数据时间

SPACE_CLASS_NAME = "fu_ben_ao_zhan_qun_xiong"

REWARD_EXP_ITEM_ID = 60101282

class AoZhanQunXiongMgr( BigWorld.Base ):
	"""
	鏖战群雄
	"""
	def __init__( self ):
		BigWorld.Base.__init__( self )
		self.registerGlobally( "AoZhanQunXiongMgr", self._onRegisterManager )
		self.currentState = MGR_STATE_FREE
		self._currentMatchRound = 0
		
		self._spaceType = SPACE_CLASS_NAME
		self.currentActivityUUID = ""
		self.currentRoundStartTime = 0.0
		
		self.timerClearDataID = 0
	
	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register AoZhanQunXiongMgr Fail!" )
			self.registerGlobally( "AoZhanQunXiongMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["AoZhanQunXiongMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("AoZhanQunXiongMgr Create Complete!")
			self.registerCrond()
	
	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"AoZhan_notice" : "onNotice",
						"AoZhan_singn" : "startSignUp",
						"AoZhan_singnEnd" : "endSignUp",
						"AoZhan_start" : "onStart",
						"AoZhan_end" : "onEnd",
					}

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )
	
	def onNotice( self ):
		"""
		广播
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.AO_ZHAN_NOTICE_1, [] )
		self.currentState = MGR_STATE_NOFITY

	def startSignUp( self ):
		"""
		deinfe method
		开始报名
		"""
		if self.timerClearDataID: #防止GM指令出错
			self.delTimer( self.timerClearDataID )
			self.clearData()
			
		self.currentState = MGR_STATE_SIGNUP
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.AO_ZHAN_NOTICE_SIGNUP, [] )
		BigWorld.globalData[ "JueDiFanJiMgr" ].onAoZhanQunXiongRequest() #请求绝地反击的前3强
		Love3.g_baseApp.globalRemoteCallClient( "aoZhan_startSignUp" )
		self.currentActivityUUID = str( uuid.uuid1() )
		BigWorld.globalData[ "ACTIVITY_AO_ZHAN_UUID" ] = self.currentActivityUUID
		BigWorld.globalData[ "ACTIVITY_AO_ZHAN_SIGN_UP" ] = True
		
	def endSignUp( self ):
		"""
		define method
		结束报名
		"""
		self.currentState = MGR_STATE_HALF_TIME
		BigWorld.globalData[ "ACTIVITY_AO_ZHAN_SIGN_UP" ] = False
	
	def onSignUp( self, playerMB, playerDBID, playerName, playerLevel, playerClass ):
		"""
		define method.
		报名
		"""
		if self.currentState == MGR_STATE_SIGNUP:
			if not self.dataMgr.joinDatas.has_key( playerDBID ):
				self.dataMgr.addJoin( playerDBID, playerName, playerLevel, playerClass, playerMB )
				playerMB.cell.aoZhan_onSignUp()
				playerMB.cell.aoZhan_setJoinFlag( self.currentActivityUUID )
				for pInfo in self.dataMgr.joinDatas.itervalues():
					if pInfo.playerMailBox:
						self.getSignUpList( pInfo.playerMailBox )
			else:
				playerMB.client.onStatusMessage( csstatus.AO_ZHAN_QUN_XIONG_ALREADY_SIGNUP, "" )
		else:
			playerMB.client.onStatusMessage( csstatus.AO_ZHAN_QUN_XIONG_NOT_SIGNUP_TIME, "" )
	
	def onStart( self ):
		"""
		define method.
		活动开动
		"""
		if len( self.dataMgr.joinDatas ) < AO_ZHAN_MIN_JOIN:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.AO_ZHAN_NOTICE_JOIN_MIN % AO_ZHAN_MIN_JOIN, [] )
			self.currentState = MGR_STATE_FREE
			self._currentMatchRound = 0
			self.clearData()
			return 
			
		self.startRoundMatch()
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.AO_ZHAN_NOTICE_2, [] )
	
	def onEnd( self ):
		"""
		define method.
		活动结束
		"""
		if self.isLastMatch():
			self._currentMatchRound += 1
			winChampionDBID = self._getNextJoinList()[0] #冠军
			if winChampionDBID:
				winChampion = self.dataMgr.joinDatas[ winChampionDBID ]
				failChampion = self.dataMgr.getMaxJoinFailPlayer()
				failChampionName = ""
				if failChampion:
					failChampionName = failChampion.playerName
					
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.AO_ZHAN_NOTICE_END%( winChampion.playerName, failChampionName ), [] )
				# 发奖励
				self.rewarJoinWin( winChampionDBID ) #冠军奖励
				for info in self.dataMgr.joinDatas.itervalues(): #败组
					if info.databaseID != winChampionDBID:
						self.rewardJoinFailure( info.databaseID )
		
		self.currentState = MGR_STATE_FREE
		self._currentMatchRound = 0		
		self.timerClearDataID = self.addTimer( TIME_CLEAR, 0, TIMER_ARG_CLEAR )
	
	def clearData( self ):
		"""
		清除数据
		"""
		self.currentActivityUUID = ""
		if BigWorld.globalData.has_key( "ACTIVITY_AO_ZHAN_UUID" ):
			del BigWorld.globalData[ "ACTIVITY_AO_ZHAN_UUID" ]
		
		for pInfo in self.dataMgr.joinDatas.itervalues():
			if pInfo.playerMailBox:
				pInfo.playerMailBox.cell.aoZhan_removeJoinFlag()
				
		self.dataMgr.resert()
		Love3.g_baseApp.globalRemoteCallClient( "aoZhan_onEnd" )
	
	def startRoundMatch( self ):
		self.disNext()
		self.addTimer( TIME_READY, 0, TIMER_ARG_READY )
		self.addTimer( TIME_ROUND, 0, TIMER_ARG_ROUND )
		self.currentRoundStartTime = time.time()
		
	def disNext( self ):
		"""
		分配下轮
		"""
		matchType = 0
		ifFirst = False
		if self._currentMatchRound == 0:#比赛刚开始
			self._currentMatchRound = self.__getFirstMatchRound()
			matchType = self.__getMatchType()
			ifFirst = True
		else:
			self._currentMatchRound += 1
			matchType = self.__getMatchType()
		
		if ifFirst or AO_ZHEN_FAILURE_ENTER_NUM.has_key( matchType ) and AO_ZHEN_FAILURE_ENTER_NUM[ matchType ] == 0:
			self.dataMgr.infos[ matchType ] = AoZhanRoundNoFailure( matchType )
		else:
			self.dataMgr.infos[ matchType ] = AoZhanRoundHasFailure( matchType )
			
		self.dataMgr.infos[ matchType ].init( self._getNextJoinList(), self._getNextFailureList() )
		self.dataMgr.infos[ matchType ].dis( self.dataMgr )
		self.startNext( matchType ) #开始下轮
	
	def __getFirstMatchRound( self ):
		"""
		根据参赛人数，确定第一轮比赛类型
		"""
		joinNum = len( self.dataMgr.joinDatas.keys() )
		i = 0
		if joinNum > 0:
			while True:
				i += 1
				if joinNum > AO_ZHAN_MAX_JOIN >> i:
					return i
			
		return int( math.log( AO_ZHAN_MAX_JOIN, 2 ) )
	
	def __getMatchType( self ):
		return AO_ZHAN_MAX_JOIN >> self._currentMatchRound

	def _getNextJoinList( self ):
		"""
		取下轮晋级者名单
		"""
		nextList = []
		if self._currentMatchRound == self.__getFirstMatchRound(): #如果是第一轮
			nextList = self.dataMgr.joinDatas.keys()
		else:
			match = self.getPreMatch() #获取上一轮比赛的数据
			if match:
				nextList = match.getNextList()
		
		"""
		#不满的名单补满
		currentMaxJoin = AO_ZHAN_MAX_JOIN >> self._currentMatchRound
		while len( nextList ) < currentMaxJoin:
			nextList.append( 0 )
		"""
		
		return nextList
	
	def _getNextFailureList( self ):
		"""
		最下轮淘汰者名单
		"""
		nextList = []
		if self._currentMatchRound < 2:
			nextList = []
		else:
			match = self.getPreMatch()
			if match:
				nextList = match.getNextFailure()
				
		return nextList
	
	def _getEnterRoom( self, playerDBID ):
		return self.getCurrentMatch().getEnterRoom( playerDBID )
	
	def getCurrentMatch( self ):
		return self.dataMgr.infos[ self.__getMatchType() ]
	
	def getPreMatch( self ):
		matchType = AO_ZHAN_MAX_JOIN >> self._currentMatchRound - 1
		if self.dataMgr.infos.has_key( matchType ):
			return self.dataMgr.infos[ matchType ]
			
		return None
	
	def startNext( self, matchType ):
		self.currentState = MGR_STATE_ENTER
	
	def readyEnd( self ):
		"""
		准备时间结束
		"""
		self.currentState = MGR_STATE_UNDERWAY
		BigWorld.globalData[ "SpaceManager" ].remoteCallDomain( self._spaceType, "activityStart", [] )
		
	def roundMatchEnd( self ):
		"""
		一轮比赛结束
		"""
		self.currentState = MGR_STATE_HALF_TIME #状态切换成中场休息时间
		BigWorld.globalData[ "SpaceManager" ].remoteCallDomain( self._spaceType, "activityEnd", [] )
		curMatch = self.getCurrentMatch()
		failLists = curMatch.getCurRoundFailure()
		for playerDBID in failLists:
			self.rewarJoinWin( playerDBID )
			
		if not self.isLastMatch():
			self.addTimer( TIME_NEXT, 0, TIMER_ARG_NEXT )
		else:
			self.onEnd()
	
	def setResult( self, spaceNumber, winner, score, useTime, remainHP ):
		"""
		define method.
		设置结果
		remainHP:胜利者剩余血量
		"""
		matchType = GET_ATHLETICS_MATCH_TYPE( spaceNumber )
		roomNum = GET_ATHLETICS_ROOM_NUM( spaceNumber )
		if self.dataMgr.infos.has_key( matchType ):
			self.dataMgr.infos[ matchType ].setResult( self, roomNum, winner, score, useTime, remainHP )
	
	def requestEnterSpace( self, spaceDomain, position, direction, baseMailbox, params ):
		"""
		请求进入副本
		"""
		if self.currentState == MGR_STATE_FREE:
			baseMailbox.client.onStatusMessage( csstatus.AO_ZHAN_QUN_XIONG_ENTER_FREE, "" )
		elif self.currentState == MGR_STATE_SIGNUP:
			baseMailbox.client.onStatusMessage( csstatus.AO_ZHAN_QUN_XIONG_ENTER_SIGN, "" )
		elif self.currentState == MGR_STATE_ENTER:
			room = self._getEnterRoom( params[ "playerDBID" ] )
			if room:
				if room.isWin():
					baseMailbox.client.onStatusMessage( csstatus.AO_ZHAN_QUN_XIONG_WIN, "" )
					return
					
				params[ "spaceKey" ] = GET_ATHLETICS_SPACE_NUMBER( self.__getMatchType(), room.rIndex )
				params[ "matchType" ] = self.getCurrentMatch().getType()
				params[ "roundTime" ] = self.currentRoundStartTime
				params.update( room.pickDictToSpace() )
				if room.aPlayer == params[ "playerDBID" ]:
					position = ( -2.178, 9.063, 48.459 )
				else:
					position = ( -2.178, 9.063, -17.403 )
					
				spaceDomain.teleportEntityMgr( position, direction, baseMailbox, params )
			else:
				baseMailbox.client.onStatusMessage( csstatus.AO_ZHAN_QUN_XIONG_CANNOT_ENTER, "" )
		else:
			baseMailbox.client.onStatusMessage( csstatus.AO_ZHAN_QUN_XIONG_NOT_ENTER_TIME, "" )
	
	def playerInit( self, playerDBID, playerMailBox ):
		"""
		玩上线
		"""
		if self.dataMgr.joinDatas.has_key( playerDBID ):
			self.dataMgr.joinDatas[ playerDBID ].playerMailBox = playerMailBox
	
	def playerDestroy( self, playerDBID ):
		"""
		玩家下线
		"""
		if self.dataMgr.joinDatas.has_key( playerDBID ):
			self.dataMgr.joinDatas[ playerDBID ].playerMailBox = None
	
	def rewarJoinWin( self, databaseID ):
		"""
		奖励所有参与的玩家
		鏖战群雄（1vN）胜者组经验、金钱奖励公式为： 
		经验：(524 * Lv ^ 1.5 + 1381) * r ^ 0.613 
		金钱：18 * Lv * 1.5 ^ (0.1 * Lv - 1) * r ^ 0.613 
		其中，Lv为玩家当前等级，r为通过的轮次。
		"""
		if databaseID and self.dataMgr.joinDatas.has_key( databaseID ):
			playerMB = self.dataMgr.joinDatas[ databaseID ].playerMailBox
			playerLevel = self.dataMgr.joinDatas[ databaseID ].playerLevel
			r = self.dataMgr.getWinnerJoinRound( databaseID )
			rewarExp = int( ( 524 * pow( playerLevel, 1.5 ) + 1381 ) * pow( r, 0.613 ) )
			rewarMoney = int( 18 * playerLevel * pow( 1.5, (0.1 * playerLevel - 1) ) * pow( r, 0.613 ) )
			if playerMB:
				playerMB.cell.addExp( rewarExp, csdefine.CHANGE_EXP_AO_ZHAN_QUN_XIONG )
				playerMB.cell.addMoney( rewarMoney, csdefine.CHANGE_MONEY_AO_ZHAN_QUN_XIONG )
			else:
				playerName = self.dataMgr.joinDatas[ databaseID ].playerName
				mailMgr = BigWorld.globalData[ "MailMgr" ]
				itemDatas = []
				item = g_items.createDynamicItem( REWARD_EXP_ITEM_ID )
				if item:
					item.setExp( rewarExp )
					tempDict = item.addToDict()
					del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
					itemData = cPickle.dumps( tempDict, 2 )
					itemDatas.append( itemData )
					
				mailMgr.send( None, playerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC,"", cschannel_msgs.AO_ZHAN_MAIL_TITILE, cschannel_msgs.AO_ZHAN_MAIL_CONTENT, rewarMoney, itemDatas )
	
	def rewardJoinFailure( self, databaseID ):
		"""
		鏖战群雄（1vN）败者组经验、金钱奖励公式为： 
		经验：(175 * Lv ^ 1.5 + 460) * r ^ 0.613 
		金钱：6 * Lv * 1.5 ^ (0.1 * Lv - 1) * r ^ 0.613 
		其中，Lv为玩家当前等级，r为通过的轮次。
		"""
		if databaseID and self.dataMgr.joinDatas.has_key( databaseID ):
			playerMB = self.dataMgr.joinDatas[ databaseID ].playerMailBox
			playerLevel = self.dataMgr.joinDatas[ databaseID ].playerLevel
			r = self.dataMgr.getFaulureJoinRound( databaseID )
			rewarExp = int( (175 * pow( playerLevel, 1.5 ) + 460) * pow( r , 0.613 ) )
			rewarMoney = int( 6 * playerLevel * pow( 1.5, (0.1 * playerLevel - 1) ) * pow( r, 0.613 ) )
			if playerMB:
				playerMB.cell.addExp( rewarExp, csdefine.CHANGE_EXP_AO_ZHAN_QUN_XIONG )
				playerMB.cell.addMoney( rewarMoney, csdefine.CHANGE_MONEY_AO_ZHAN_QUN_XIONG )
			else:
				playerName = self.dataMgr.joinDatas[ databaseID ].playerName
				mailMgr = BigWorld.globalData[ "MailMgr" ]
				itemDatas = []
				item = g_items.createDynamicItem( REWARD_EXP_ITEM_ID )
				if item:
					item.setExp( rewarExp )
					tempDict = item.addToDict()
					del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
					itemData = cPickle.dumps( tempDict, 2 )
					itemDatas.append( itemData )
					
				mailMgr.send( None, playerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC,"", cschannel_msgs.AO_ZHAN_MAIL_TITILE, cschannel_msgs.AO_ZHAN_MAIL_CONTENT, rewarMoney, itemDatas )
	
	def getBattlefield( self, playerMB ):
		"""
		define method.
		获取战报
		"""
		doingMatch = 0
		if self.currentState in [ MGR_STATE_ENTER, MGR_STATE_UNDERWAY ]:
			doingMatch = self.__getMatchType()
			
		playerMB.client.aoZhan_showBattlefield( self.dataMgr, doingMatch )
	
	def getSignUpList( self, playerMB ):
		"""
		define method
		获取报名名单
		info:playerMB, playerName, playerLevel, playerClass
		"""
		playerMB.client.aoZhan_showSignUpWindows( self.dataMgr.joinDatas.values() )
	
	def getplayerMailBox( self, playerDBID ):
		return self.dataMgr.getplayerMailBox( playerDBID )
	
	def isLastMatch( self ):
		return self.__getMatchType() == 1
	
	def onTimer( self, timerID, timerArg ):
		if timerArg == TIMER_ARG_READY:
			self.readyEnd()#准备时间结束
		elif timerArg == TIMER_ARG_ROUND:
			self.roundMatchEnd()
		elif timerArg == TIMER_ARG_NEXT:
			self.startRoundMatch()
		elif timerArg == TIMER_ARG_CLEAR:
			self.timerClearDataID = 0
			self.clearData()