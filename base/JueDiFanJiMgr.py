# -*- coding: gb18030 -*-


import BigWorld
from bwdebug import *
import csdefine
import cschannel_msgs
import Love3
import time
import csstatus
import csconst
import random
import items
import Function
import cPickle
import ECBExtend
import RoleMatchRecorder
from CrondDatas import CrondDatas
from operator import itemgetter, attrgetter
g_items = items.instance()
g_CrondDatas = CrondDatas.instance()


LEFT_SEAT = 0			#匹配的第一个元素
RIGHT_SEAT = 1			#匹配的第二个元素
CAN_MATCH_NUM = 2		#能够匹配的最小数量
MATCH_NUM = 2			#匹配的第三个元素（表示匹配的数字）


VICTORY_SCORE_NUM			= 2			#胜一场积分数
DRAW_SCORE_NUM				= 1			#平一场积分数

MAX_SCORE_NUM				= 10		#最大积分数

LENGTH_OF_PLAYER_1			= 2
LENGTH_OF_PLAYER_2			= 3


REWARD_EXP_ITEM_ID = 60101282	#经验物品ID
VICTORY_MONEY		= 3			#胜利金钱奖励
DRAW_MONEY			= 2			#平局金钱奖励
FAILED_MONEY		= 1			#失败金钱奖励
FIRST_THIRD_RANK_NUM = 3		#前三名

INTERFACE_CLOSE_TIME = 300.0	#界面关闭时间（5分钟）
INTERFACE_CLOSE_TIMER = 20003	#界面关闭timer
JUE_DI_FAN_JI_SPACENAME = "fu_ben_jue_di_fan_ji"

class JueDiFanJiMember:
	"""
	绝地反击活动成员
	"""
	def __init__( self, level, dbid ):
		self.level = level
		self.dbid = dbid

	def __repr__( self ):
		return repr( ( self.level, self.dbid ) )
		
	def getLevel( self ):
		return self.level
	
	def getDBID( self ):
		return self.dbid

class JueDiFanJiMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# 把自己注册为globalData全局实体
		self.jueDiFanJiQueue = []							#绝地反击排队队列
		self.jueDiFanJiScoreDict = {}						#绝地反击积分字典，形如{dbid1:[playerName1, score1, victoryNum1 ],dbid2:[playerName2, score2, victoryNum2 ],...}(其中victoryNum1为净胜数，score1为积分)
		self.jueDiFanJiDBIDToPlayerInfo = {}				#绝地反击DBID对应的player信息字典，形如{dbid1:[playerMB1,playerName1,level1,playerClass1],dbid2:[playerMB2,playerName2,level2,playerClass2]}
		self.jueDiFanJiVictoryCountDict = {}				#绝地反击连胜次数记录字典
		self.jueDiFanJiStateDict = {}						#绝地反击每个玩家状态字典
		self.jueDiFanJiMatchList = []						#绝地反击匹配列表，形如[(dbid1,dbid2,匹配数字),(dbid3,dbid4,匹配数字),...](其中dbid1和dbid2是对战双方，匹配数字指的是这是多少次匹配)
		self.jueDiFanJiMatchedDBIDToIndex = {}				#绝地反击已经匹配的DBID对应的Index字典，形如{dbid1:index1,dbid2:index1,dbid3:index2,dbid4:index2,...}
		self.jueDiFanJiEmptyIndexList = []					#绝地反击空的位置索引
		self.curMaxMatchCount = 0							#目前已经匹配成功的最大数量
		self.requestCount = 0								#请求的总数量
		self.operateCount = 0								#正在操作的数量
		self.jueDiFanJiDBIDToOnlineDict = {}				#绝地反击DBID对应玩家是否在线字典,形如{123:1,234:0,...}（其中在线用1表示，不在线用0表示）
		self.jueDiFanJiTimerID = 0							#绝地反击活动Timer
		self.jueDiFanJiFirstThirdRank = []					#绝地反击前三名信息，由于需要在鏖战群雄中报名的时候能够取到，所以需要保存到下一次活动开启前
		self.jueDiFanJiTempHPDict = {}						#绝地反击活动临时血量记录,形如{dbid1:HP1,dbid2:HP2,...}
		self.registerGlobally( "JueDiFanJiMgr", self._onRegisterManager )

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register JueDiFanJiMgr Fail!" )
			# again
			self.registerGlobally( "JueDiFanJiMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["JueDiFanJiMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("JueDiFanJiMgr Create Complete!")
			self.registerCrond()



	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"jueDiFanJi_Start_Notice" : "onStartNotice",
					  	"jueDiFanJi_Start" : "onStart",
						"jueDiFanJi_End" :	"onEnd",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )
		crond.addAutoStartScheme( "jueDiFanJi_Start", self, "onStart" )

	def onStart( self ):
		"""
		define method.
		活动报名开始
		"""
		if BigWorld.globalData.has_key( "AS_JueDiFanJiStart" ) and BigWorld.globalData[ "AS_JueDiFanJiStart" ] == True:
			curTime = time.localtime()
			ERROR_MSG( "绝地反击活动正在进行，%i点%i分试图再次开始绝地反击活动。"%(curTime[3],curTime[4] ) )
			return
		for playerInfo in self.jueDiFanJiDBIDToPlayerInfo.itervalues():
				playerMB = playerInfo[ 0 ]
				playerMB.cell.removeBulletin()
		if self.jueDiFanJiTimerID:
			self.delTimer( self.jueDiFanJiTimerID )
			self.jueDiFanJiTimerID = 0
		self.resetJueDiFanJiData()
		self.jueDiFanJiFirstThirdRank = []
		INFO_MSG( "jueDiFanJi onStart: resetJueDiFanJiData!!!" )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_JUE_DI_FAN_JI_BEGIN, [] )
		BigWorld.globalData[ "AS_JueDiFanJiStart" ] = True
		Love3.g_baseApp.globalRemoteCallClient( "jueDiFanJiStart" )

	def onStartNotice( self ):
		"""
		define method.
		活动开始通知
		"""
		pass

	def onEnd( self ):
		"""
		define method.
		活动报名结束
		"""
		if BigWorld.globalData.has_key( "AS_JueDiFanJiStart" ):
			del BigWorld.globalData[ "AS_JueDiFanJiStart" ]
		self.calJueDiFanJiRankAndNotice()
		self.jueDiFanJiTimerID = self.addTimer( INTERFACE_CLOSE_TIME, 0, INTERFACE_CLOSE_TIMER)
		
	def onTimer( self, id, userArg ):
		"""
		"""
		if userArg == INTERFACE_CLOSE_TIMER:
			Love3.g_baseApp.globalRemoteCallClient( "jueDiFanJiEnd" )
			for playerInfo in self.jueDiFanJiDBIDToPlayerInfo.itervalues():
				playerMB = playerInfo[ 0 ]
				playerMB.cell.removeBulletin()
			self.resetJueDiFanJiData()
			self.jueDiFanJiTimerID = 0
			INFO_MSG( "jueDiFanJi onTimer: resetJueDiFanJiData!!!" )
		
	def onJueDiFanJiSignUp( self, playerMB, dbid, playerName, level, playerClass ):
		"""
		绝地反击报名
		"""
		if BigWorld.globalData.has_key( "AS_JueDiFanJiStart" ) and BigWorld.globalData[ "AS_JueDiFanJiStart" ]:
			self.jueDiFanJiDBIDToPlayerInfo[ dbid ] = [ playerMB, playerName, level, playerClass ]
			self.jueDiFanJiDBIDToOnlineDict[ dbid ] = 1
			#改变状态，发送现在的状态到客户端
			self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_HAS_SIGN_UP )
			self.pushJueDiFanJiQueue( dbid, level )
			
	def assignJueDiFanJiMatcher( self ):
		"""
		分配绝地反击的匹配队列
		"""
		if len( self.jueDiFanJiQueue ) >= CAN_MATCH_NUM and BigWorld.globalData.has_key( "AS_JueDiFanJiStart" ) and BigWorld.globalData[ "AS_JueDiFanJiStart" ] == True:
			if self.operateCount != 0:
				return
			else:
				self.operateCount = 1
				self.sortJueDiFanJiQueue()			#对绝地反击活动队列进行排序
				playerA = self.jueDiFanJiQueue.pop( 0 ).getDBID()
				playerB = self.jueDiFanJiQueue.pop( 0 ).getDBID()
				self.clearJueDiFanJiMatcher( playerA )
				self.clearJueDiFanJiMatcher( playerB )
				self.curMaxMatchCount += 1
				if self.jueDiFanJiEmptyIndexList:
					indexOfMatch = self.jueDiFanJiEmptyIndexList[ 0 ]
					self.jueDiFanJiMatchList[ indexOfMatch ] = [ playerA, playerB, self.curMaxMatchCount ]
					self.jueDiFanJiMatchedDBIDToIndex[ playerA ] = ( indexOfMatch, LEFT_SEAT )
					self.jueDiFanJiMatchedDBIDToIndex[ playerB ] = ( indexOfMatch, RIGHT_SEAT )
					DEBUG_MSG( "jueDiFanJi : match success, playerA is %s, playerB is %s, indexOfMatch is %s"%( playerA, playerB, indexOfMatch ) )
				else:
					self.jueDiFanJiMatchList.append( [ playerA, playerB, self.curMaxMatchCount ] )
					indexOfMatch = len( self.jueDiFanJiMatchList ) - 1
					self.jueDiFanJiMatchedDBIDToIndex[ playerA ] = ( indexOfMatch, LEFT_SEAT )
					self.jueDiFanJiMatchedDBIDToIndex[ playerB ] = ( indexOfMatch, RIGHT_SEAT )
					DEBUG_MSG( "jueDiFanJi : new match success, playerA is %s, playerB is %s, indexOfMatch is %s"%( playerA, playerB, indexOfMatch ) )
				#改变状态，发送现在的状态到客户端
				self.changeStateDict( playerA, csdefine.JUE_DI_FAN_JI_HAS_MATCHED )
				self.changeStateDict( playerB, csdefine.JUE_DI_FAN_JI_HAS_MATCHED )
				self.requestCount -= 1
				self.operateCount = 0
				if self.requestCount > 0:
					#因为是异步处理相应的删除等待队列加入匹配队伍，所以需要等到上一次操作完成后再进行下一次操作
					self.assignJueDiFanJiMatcher()
			
			
	def clearJueDiFanJiMatcher( self, dbid ):
		"""
		清理掉线、没有确认进入等情况下的匹配队列数据
		"""
		if self.jueDiFanJiMatchedDBIDToIndex.has_key( dbid ):
			outerIndex,innerIndex = self.jueDiFanJiMatchedDBIDToIndex[ dbid ]
			self.jueDiFanJiMatchList[ outerIndex ][ innerIndex ] = 0
			if ( innerIndex == LEFT_SEAT and self.jueDiFanJiMatchList[ outerIndex ][ RIGHT_SEAT ] == 0 ) or ( innerIndex == RIGHT_SEAT and self.jueDiFanJiMatchList[ outerIndex ][ LEFT_SEAT ] == 0 ):
				self.jueDiFanJiEmptyIndexList.append( outerIndex )
			del self.jueDiFanJiMatchedDBIDToIndex[ dbid ]
			
	def sendStateInfo( self, dbid, state ):
		"""
		发送状态信息
		"""
		if self.jueDiFanJiDBIDToPlayerInfo.has_key( dbid ):
			playerMB = self.jueDiFanJiDBIDToPlayerInfo[ dbid ][ 0 ]
			if self.jueDiFanJiVictoryCountDict.has_key( dbid ):
				playerMB.cell.onReceiveStateInfo( state, self.jueDiFanJiVictoryCountDict[ dbid ][ 0 ] )
			else:
				playerMB.cell.onReceiveStateInfo( state, 0 )
			if state == csdefine.JUE_DI_FAN_JI_HAS_MATCHED:
				#同时给对应的玩家的cell加一个timer，25s以后回调
				playerMB.cell.noticeAddTimer( csconst.JUE_DI_FAN_JI_WAIT_TIME )
	
	def onJueDiFanJiEnterConfirm( self, playerMB, dbid ):
		"""
		绝地反击进入确认
		"""
		if BigWorld.globalData.has_key( "AS_JueDiFanJiStart" ) and BigWorld.globalData[ "AS_JueDiFanJiStart" ]:
			if self.jueDiFanJiMatchedDBIDToIndex.has_key( dbid ):
				outerIndex,innerIndex = self.jueDiFanJiMatchedDBIDToIndex[ dbid ]
				if innerIndex == LEFT_SEAT:
					matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ RIGHT_SEAT ]
				elif innerIndex == RIGHT_SEAT:
					matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ LEFT_SEAT ]
				DEBUG_MSG( "dbid is %s, matchDBID is %s"%( dbid, matchDBID ) )
				if not matchDBID:
					self.clearJueDiFanJiMatcher( dbid )		#如果为0，说明对方已经匹配，这时候自己也应该被清理出匹配列表
					self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_HAS_SIGN_UP )
					if self.jueDiFanJiDBIDToPlayerInfo.has_key( dbid ):
						self.pushJueDiFanJiQueue( dbid, self.jueDiFanJiDBIDToPlayerInfo[ dbid ][ 2 ] )
				else:
					if self.jueDiFanJiStateDict[ matchDBID ] == csdefine.JUE_DI_FAN_JI_HAS_CONFIRM_ENTER:
					#分配相应的副本，将玩家传送进去(如果这时候有一个玩家不在线了，那么就不传送)
					#考虑到异步的问题，先改变状态再传送
						if self.isOnlineOrNot( matchDBID ) and self.isOnlineOrNot( dbid ) and self.jueDiFanJiDBIDToPlayerInfo.has_key( matchDBID ):
							self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_HAS_ENTERED )
							self.changeStateDict( matchDBID, csdefine.JUE_DI_FAN_JI_HAS_ENTERED )
							matchPlayerMB = self.jueDiFanJiDBIDToPlayerInfo[ matchDBID ][ 0 ]
							playerMB.cell.gotoSpace( JUE_DI_FAN_JI_SPACENAME, ( 0, 0, 0 ), ( 0, 0, 0 ) )
							matchPlayerMB.cell.gotoSpace( JUE_DI_FAN_JI_SPACENAME, ( 0, 0, 0), ( 0, 0, 0 ) )
							#玩家进入之后取消玩家的timer
							playerMB.cell.jueDiFanJiCanCelTimer()
							matchPlayerMB.cell.jueDiFanJiCanCelTimer()
					else:
						self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_HAS_CONFIRM_ENTER )
	
	def onJueDiFanJiCancelEnter( self, playerMB, dbid ):
		"""
		绝地反击玩家主动取消进入
		"""
		#需要取消相应的匹配队列，将另外的玩家重新排队，将主动取消的玩家的状态变成需要重新报名的状态
		if self.jueDiFanJiMatchedDBIDToIndex.has_key( dbid ):
			outerIndex,innerIndex = self.jueDiFanJiMatchedDBIDToIndex[ dbid ]
			if innerIndex == LEFT_SEAT:
				matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ RIGHT_SEAT ]
			elif innerIndex == RIGHT_SEAT:
				matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ LEFT_SEAT ]
			self.clearJueDiFanJiMatcher( dbid )		#将自己清理出匹配队列
			self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_NOT_SIGN_UP )
			DEBUG_MSG( "CancelEnter: dbid is %s, matchDBID is %s"%( dbid, matchDBID ) )
			if matchDBID:				#如果匹配的dbid不为0（说明没有重新匹配）,那么就需要将对方玩家先清除匹配记录，如果在线就重新加入排队队列中
				self.clearJueDiFanJiMatcher( matchDBID )
				if self.isOnlineOrNot( matchDBID ) and self.jueDiFanJiDBIDToPlayerInfo.has_key( matchDBID ):
					self.changeStateDict( matchDBID, csdefine.JUE_DI_FAN_JI_HAS_SIGN_UP )
					self.pushJueDiFanJiQueue( matchDBID, self.jueDiFanJiDBIDToPlayerInfo[ matchDBID ][ 2 ] )
				else:
					self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_NOT_SIGN_UP )
	
	def pushJueDiFanJiQueue( self, dbid, level ):
		"""
		将一个玩家加入队列的同时判断是否人数可以匹配，可以则进行相应的匹配
		"""
		flag = False
		for member in self.jueDiFanJiQueue:
			if member.getDBID() == dbid:
				flag = True
				break
		if not flag:
			self.jueDiFanJiQueue.append( JueDiFanJiMember( level, dbid ) )
		#if dbid not in self.jueDiFanJiQueue:
			#self.jueDiFanJiQueue.append( dbid )
		if len( self.jueDiFanJiQueue ) >= CAN_MATCH_NUM and BigWorld.globalData.has_key( "AS_JueDiFanJiStart" ) and BigWorld.globalData[ "AS_JueDiFanJiStart" ] == True:
			self.requestJueDiFanJiMatch()
	
	def sortJueDiFanJiQueue( self ):
		"""
		绝地反击活动队列排序
		"""
		self.jueDiFanJiQueue = sorted( self.jueDiFanJiQueue, key = attrgetter('level'), reverse=True )
	
	def requestJueDiFanJiMatch( self ):
		"""
		请求绝地反击匹配
		"""
		self.requestCount += 1
		if self.operateCount == 0:
			self.assignJueDiFanJiMatcher()
	
	
	def changeStateDict( self, dbid, state ):
		"""
		改变状态列表，同时通知客户端状态改变
		"""
		DEBUG_MSG( "jueDiFanJi : player state change, dbid is %s, state is %s"%( dbid, state ) )
		if state == csdefine.JUE_DI_FAN_JI_NOT_SIGN_UP:
			if self.jueDiFanJiStateDict.has_key( dbid ):
				del self.jueDiFanJiStateDict[ dbid ]
		else:
			self.jueDiFanJiStateDict[ dbid ] = state
		if self.jueDiFanJiDBIDToPlayerInfo.has_key( dbid ):
			self.jueDiFanJiDBIDToPlayerInfo[ dbid ][ 0 ].setJueDiFanJiState( state )
			self.sendStateInfo( dbid, state )
	
	def isOnlineOrNot( self, dbid ):
		"""
		玩家是否在线的判断，在玩家报名后到销毁之前都认为玩家在线
		"""
		if self.jueDiFanJiDBIDToOnlineDict.has_key( dbid ) and self.jueDiFanJiDBIDToOnlineDict[ dbid ]:
			return True
		else:
			return False
	
	def onJueDiFanJiReachTimeConfirm( self, dbid ):
		"""
		绝地反击活动确认时间到达回调
		"""
		if self.jueDiFanJiStateDict.has_key( dbid ) and self.jueDiFanJiMatchedDBIDToIndex.has_key( dbid ) and self.jueDiFanJiStateDict[ dbid ] == csdefine.JUE_DI_FAN_JI_HAS_CONFIRM_ENTER:
			if self.jueDiFanJiMatchedDBIDToIndex.has_key( dbid ):
				outerIndex,innerIndex = self.jueDiFanJiMatchedDBIDToIndex[ dbid ]
				if innerIndex == LEFT_SEAT:
					matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ RIGHT_SEAT ]
				elif innerIndex == RIGHT_SEAT:
					matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ LEFT_SEAT ]
				DEBUG_MSG( "dbid is %s, state is %s, matchDBID is %s"%( dbid, self.jueDiFanJiStateDict[ dbid ], matchDBID ) )
				if  not matchDBID:
					self.clearJueDiFanJiMatcher( dbid )		#如果为0，说明对方已经匹配，这时候自己也应该被清理出匹配列表
					self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_HAS_SIGN_UP )
					if self.jueDiFanJiDBIDToPlayerInfo.has_key( dbid ):
						self.pushJueDiFanJiQueue( dbid, self.jueDiFanJiDBIDToPlayerInfo[ dbid ][ 2 ] )
				else:
					#不在线并且是已匹配的状态下（这就说明玩家不是上线后再次报名，如果是上线后再次报名，再进入匹配队列，那么matchDBID为0，如果上线后报名，没有进入匹配队列，那么状态就不会为匹配状态）
					#对于这种情况，策划的意思是还没有进入之前，如果玩家掉线就重新报名，如果进入副本之后，状态为已经进入，那么玩家可以在相应的时间内上线
					#（在线的情况下，玩家会首先调用onJueDiFanJiEnterConfirm，因为只有这里设置了进入确认状态，因此时间到达的时候如果双方状态都为进入确认状态，那么就应该各自处理自己的情况，否则会导致状态混乱）
					#对方在线的情况，没有进行处理对方的情况，因为对方玩家会自己有一个timer回调，自己处理自己的情况就行。
					if not self.isOnlineOrNot( matchDBID ) and self.jueDiFanJiStateDict[ matchDBID ] == csdefine.JUE_DI_FAN_JI_HAS_MATCHED:
						self.clearJueDiFanJiMatcher( matchDBID )					#要这一步，因为可能玩家掉线了，后面没有再次上线，那么这个匹配记录就一直不会清除，而且就算没掉线，正常情况下，也需要主动清除重新报名
						self.changeStateDict( matchDBID, csdefine.JUE_DI_FAN_JI_NOT_SIGN_UP )
						#del self.jueDiFanJiStateDict[ matchDBID ]
						#对方不在线，自己应该被清理出匹配列表,重新加入匹配队列
						self.clearJueDiFanJiMatcher( dbid )
						self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_HAS_SIGN_UP )
						if self.jueDiFanJiDBIDToPlayerInfo.has_key( dbid ):
							self.pushJueDiFanJiQueue( dbid, self.jueDiFanJiDBIDToPlayerInfo[ dbid ][ 2 ] )
		elif self.jueDiFanJiStateDict.has_key( dbid ) and self.jueDiFanJiMatchedDBIDToIndex.has_key( dbid ) and self.jueDiFanJiStateDict[ dbid ] != csdefine.JUE_DI_FAN_JI_HAS_CONFIRM_ENTER:
			if self.jueDiFanJiMatchedDBIDToIndex.has_key( dbid ):
				outerIndex,innerIndex = self.jueDiFanJiMatchedDBIDToIndex[ dbid ]
				if innerIndex == LEFT_SEAT:
					matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ RIGHT_SEAT ]
				elif innerIndex == RIGHT_SEAT:
					matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ LEFT_SEAT ]
				DEBUG_MSG( "dbid is %s, state is %s, matchDBID is %s"%( dbid, self.jueDiFanJiStateDict[ dbid ], matchDBID ) )
				self.clearJueDiFanJiMatcher( dbid )
				self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_NOT_SIGN_UP )
				if matchDBID:
					if not self.isOnlineOrNot( matchDBID ):							#对方不在线的情况下，将对方清除出匹配列表，玩家上线需要重新报名
						self.clearJueDiFanJiMatcher( matchDBID )
						self.changeStateDict( matchDBID, csdefine.JUE_DI_FAN_JI_NOT_SIGN_UP )
					elif self.isOnlineOrNot( matchDBID ) and self.jueDiFanJiMatchedDBIDToIndex.has_key( matchDBID ) and self.jueDiFanJiStateDict[ matchDBID ] == csdefine.JUE_DI_FAN_JI_HAS_CONFIRM_ENTER:
						#这里将已经匹配的玩家再次加入报名列表，是为了防止已经匹配并且确认进入的玩家1，先调用了onJueDiFanJiReachTimeConfirm方法，然而这时候，
						#跟他匹配的玩家2还是已匹配但是未确认进入状态，从而导致不会主动将玩家1的状态改变，以至于玩家1一直都是等待对方确认状态，需要主动取消
						#所以在玩家2调用onJueDiFanJiReachTimeConfirm方法的时候，除了将自己的状态清理以外，同时如果对方状态是已确认进入状态，则改为已报名的状态
						self.clearJueDiFanJiMatcher( matchDBID )
						self.changeStateDict( matchDBID, csdefine.JUE_DI_FAN_JI_HAS_SIGN_UP )
						if self.jueDiFanJiDBIDToPlayerInfo.has_key( matchDBID ):
							self.pushJueDiFanJiQueue( matchDBID, self.jueDiFanJiDBIDToPlayerInfo[ matchDBID ][ 2 ] )
		
	def onEnterJueDiFanJiSpace( self, domainBase, baseMailbox, params ):
		"""
		请求进入绝地反击活动副本
		"""
		isLogin = params.has_key( "login" )
		dbid = params[ "dbID" ]
		if not self.jueDiFanJiMatchedDBIDToIndex.has_key( dbid ):
			if isLogin:
				baseMailbox.logonSpaceInSpaceCopy()
			return
		outerIndex,innerIndex = self.jueDiFanJiMatchedDBIDToIndex[ dbid ]
		if innerIndex == LEFT_SEAT:
			params[ "left" ] = dbid
			params[ "right" ] = self.jueDiFanJiMatchList[ outerIndex ][ RIGHT_SEAT ]
		elif innerIndex == RIGHT_SEAT:
			params[ "left" ] = self.jueDiFanJiMatchList[ outerIndex ][ LEFT_SEAT ]
			params[ "right" ] = dbid
		params[ "spaceKey" ] = "JueDiFanJi_" + str( self.jueDiFanJiMatchList[ outerIndex ][ MATCH_NUM ] )
		if self.jueDiFanJiMatchedDBIDToIndex.has_key( dbid ):
			outerIndex,innerIndex = self.jueDiFanJiMatchedDBIDToIndex[ dbid ]
			if innerIndex == LEFT_SEAT:
				matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ RIGHT_SEAT ]
			elif innerIndex == RIGHT_SEAT:
				matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ LEFT_SEAT ]
		if self.jueDiFanJiVictoryCountDict.has_key( dbid ):
			params[ "playerHP" ] = self.jueDiFanJiVictoryCountDict[ dbid ][ 1 ]
			params[ "playerHPToDBID" ] = dbid
		elif self.jueDiFanJiVictoryCountDict.has_key( matchDBID ):
			params[ "playerHP" ] = self.jueDiFanJiVictoryCountDict[ matchDBID ][ 1 ]
			params[ "playerHPToDBID" ] = matchDBID
		domainBase.onEnterSpace( baseMailbox, params )
		if isLogin:
			self.jueDiFanJiDBIDToPlayerInfo[ dbid ][ 0 ] = baseMailbox
			#通知客户端玩家现在的状态
			self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_HAS_ENTERED )
		
	def onAddJueDiFanJiScore( self, victoryDBID, failedDBID, status, hp ):
		"""
		define method
		绝地反击活动增加积分
		"""
		victoryName = ""
		failedName = ""
		if self.jueDiFanJiDBIDToPlayerInfo.has_key( victoryDBID ):
			victoryName = self.jueDiFanJiDBIDToPlayerInfo[ victoryDBID ][ 1 ]
		if self.jueDiFanJiDBIDToPlayerInfo.has_key( failedDBID ):
			failedName = self.jueDiFanJiDBIDToPlayerInfo[ failedDBID ][ 1 ]
		if status == csdefine.JUE_DI_FAN_JI_VICTORY_STATUS:				#胜负局
			if self.jueDiFanJiVictoryCountDict.has_key( victoryDBID ):
				score = 2 * (self.jueDiFanJiVictoryCountDict[ victoryDBID ][ 0 ] + 1)				#如果有连胜，那么积分为2*（ 连胜数 + 1 ）
				if score > MAX_SCORE_NUM:
					score = MAX_SCORE_NUM
			else:
				score = VICTORY_SCORE_NUM
			if not self.jueDiFanJiScoreDict.has_key( victoryDBID ):
					self.jueDiFanJiScoreDict[ victoryDBID ] = [ victoryName, score, 1 ]
			else:
				victoryNum = self.jueDiFanJiScoreDict[ victoryDBID ][ 2 ] + 1
				newScore = self.jueDiFanJiScoreDict[ victoryDBID ][ 1 ] + score
				self.jueDiFanJiScoreDict[ victoryDBID ][ 1 ] = newScore
				self.jueDiFanJiScoreDict[ victoryDBID ][ 2 ] = victoryNum
			self.jueDiFanJiTempHPDict[ victoryDBID ] = hp
			if not self.jueDiFanJiScoreDict.has_key( failedDBID ):
				self.jueDiFanJiScoreDict[ failedDBID ] = [ failedName, 0, 0 ]
			#失败玩家的连胜数需要清零
			self.clearVictoryCountDict( failedDBID )
			#胜利的玩家连胜和不是连胜的积分不一样，需要发送到客户端进行显示
			if self.jueDiFanJiDBIDToPlayerInfo.has_key( victoryDBID ) and self.isOnlineOrNot( victoryDBID ):
				victoryPlayerMB = self.jueDiFanJiDBIDToPlayerInfo[ victoryDBID ][ 0 ]
				victoryPlayerMB.client.receiveScoreInfo( score )
				victoryPlayerMB.client.selectLeaveOrNot( csdefine.JUE_DI_FAN_JI_VICTORY_STATUS )
			if self.jueDiFanJiDBIDToPlayerInfo.has_key( failedDBID ) and self.isOnlineOrNot( failedDBID ):
				failedPlayerMB = self.jueDiFanJiDBIDToPlayerInfo[ failedDBID ][ 0 ]
				failedPlayerMB.client.selectLeaveOrNot( csdefine.JUE_DI_FAN_JI_FAILED_STATUS )
		elif status == csdefine.JUE_DI_FAN_JI_DRAW_STATUS:					#平局
			score = DRAW_SCORE_NUM
			if not self.jueDiFanJiScoreDict.has_key( victoryDBID ):
				self.jueDiFanJiScoreDict[ victoryDBID ] = [ victoryName, score, 0 ]
			else:
				newScore = self.jueDiFanJiScoreDict[ victoryDBID ][ 1 ] + score
				self.jueDiFanJiScoreDict[ victoryDBID ][ 1 ] = newScore
			if not self.jueDiFanJiScoreDict.has_key( failedDBID ):
				self.jueDiFanJiScoreDict[ failedDBID ] = [ failedName, score, 0 ]
			else:
				newScore = self.jueDiFanJiScoreDict[ failedDBID ][ 1 ] + score
				self.jueDiFanJiScoreDict[ failedDBID ][ 1 ] = newScore
			#由于是平局，双方的连胜数都需要清零
			self.clearVictoryCountDict( victoryDBID )
			self.clearVictoryCountDict( failedDBID )
			if self.jueDiFanJiDBIDToPlayerInfo.has_key( victoryDBID ) and self.isOnlineOrNot( victoryDBID ):
				victoryPlayerMB = self.jueDiFanJiDBIDToPlayerInfo[ victoryDBID ][ 0 ]
				victoryPlayerMB.client.selectLeaveOrNot( csdefine.JUE_DI_FAN_JI_DRAW_STATUS )
			if self.jueDiFanJiDBIDToPlayerInfo.has_key( failedDBID ) and self.isOnlineOrNot( failedDBID ):
				failedPlayerMB = self.jueDiFanJiDBIDToPlayerInfo[ failedDBID ][ 0 ]
				failedPlayerMB.client.selectLeaveOrNot( csdefine.JUE_DI_FAN_JI_DRAW_STATUS )
		self.clearJueDiFanJiMatcher( victoryDBID )		#将胜利的玩家清理出匹配队列
		self.changeStateDict( victoryDBID, csdefine.JUE_DI_FAN_JI_NOT_SIGN_UP )
		self.clearJueDiFanJiMatcher( failedDBID )		#将失败的玩家清理出匹配队列
		self.changeStateDict( failedDBID, csdefine.JUE_DI_FAN_JI_NOT_SIGN_UP )
		
	def onClearRecord( self, dbid ):
		"""
		玩家都掉线等情况，需要清除相应的匹配记录
		"""
		self.clearJueDiFanJiMatcher( dbid )
		self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_NOT_SIGN_UP )
		
	def sendOfflineReward( self, dbid, status ):
		"""
		玩家掉线，发送离线奖励
		"""
		if self.jueDiFanJiDBIDToPlayerInfo.has_key( dbid ):
			level = self.jueDiFanJiDBIDToPlayerInfo[ dbid ][ 2 ]
		else:
			level = 0
		if status == csdefine.JUE_DI_FAN_JI_VICTORY_STATUS:
			#绝地反击（1v1）胜者经验、金钱奖励公式为： (n指的是到目前为止连续胜利的总次数，第一场胜利，n为1 )
			#经验：(175 * Lv ^ 1.5 + 460) * (n ^ 2 / (n ^ 2 + n + 1)) 
			#金钱：18 * Lv * 1.5 ^ (0.1 * Lv - 1) * (n ^ 2 / (n ^ 2 + n + 1)) 
			n = 1
			if self.jueDiFanJiVictoryCountDict.has_key( dbid ):
				n = self.jueDiFanJiVictoryCountDict[ dbid ][ 0 ] + 1
			exp = int( ( 175 * level ** 1.5 + 460 ) * ( n ** 2 / ( n ** 2 + n + 1.0 ) ) )
			moneyNum = int( 18 * level * 1.5 ** ( 0.1 * level - 1 ) * ( n ** 2 / ( n ** 2 + n + 1.0 ) ) )
		elif status == csdefine.JUE_DI_FAN_JI_DRAW_STATUS:
			#绝地反击（1v1）平局经验、金钱奖励公式为： 
			#经验：(116 * Lv ^ 1.5 + 307) * (1 ^ 2 / (1 ^ 2 + 1 + 1)) 
			#金钱：12 * Lv * 1.5 ^ (0.1 * Lv - 1) * (1 ^ 2 / (1 ^ 2 + 1 + 1)) 
			exp = int( ( 116 * level ** 1.5 + 307 ) * ( 1/ 3.0 ) )
			moneyNum = int( 12 * level * 1.5 ** ( 0.1 * level - 1 ) * ( 1/3.0 ) )
		elif status == csdefine.JUE_DI_FAN_JI_FAILED_STATUS:
			#绝地反击（1v1）败者经验、金钱奖励公式为： 
			#经验：(58 * Lv ^ 1.5 + 153) * (1 ^ 2 / (1 ^ 2 + 1 + 1)) 
			#金钱：6 * Lv * 1.5 ^ (0.1 * Lv - 1) * (1 ^ 2 / (1 ^ 2 + 1 + 1)) 
			exp = int( ( 58 * level ** 1.5 + 153 ) * ( 1/ 3.0 ) )
			moneyNum = int( 6 * level * 1.5 ** ( 0.1 * level - 1 ) * ( 1/3.0 ) )
		itemDatas = []
		item = g_items.createDynamicItem( REWARD_EXP_ITEM_ID )
		if item:
			item.setExp( exp )
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
			itemData = cPickle.dumps( tempDict, 2 )
			itemDatas.append( itemData )
		if len( itemDatas ) != 0 and self.jueDiFanJiDBIDToPlayerInfo.has_key( dbid ):
			playerName = self.jueDiFanJiDBIDToPlayerInfo[ dbid ][ 1 ]
			title = cschannel_msgs.JUE_DI_FAN_JI_REWARD_TITLE
			content = cschannel_msgs.JUE_DI_FAN_JI_REWARD_CONTENT
			BigWorld.globalData["MailMgr"].send( None, playerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC,"", title, content, moneyNum, itemDatas )
			
	def sendOnlineReward( self, playerMB, dbid, status, level ):
		"""
		发送在线奖励
		"""
		if status == csdefine.JUE_DI_FAN_JI_VICTORY_STATUS:
			#绝地反击（1v1）胜者经验、金钱奖励公式为： (n指的是到目前为止连续胜利的总次数，第一场胜利，n为1 )
			#经验：(175 * Lv ^ 1.5 + 460) * (n ^ 2 / (n ^ 2 + n + 1)) 
			#金钱：18 * Lv * 1.5 ^ (0.1 * Lv - 1) * (n ^ 2 / (n ^ 2 + n + 1)) 
			n = 1
			if self.jueDiFanJiVictoryCountDict.has_key( dbid ):
				n = self.jueDiFanJiVictoryCountDict[ dbid ][ 0 ] + 1
			exp = int( ( 175 * level ** 1.5 + 460 ) * ( n ** 2 / ( n ** 2 + n + 1.0 ) ) )
			money = int( 18 * level * 1.5 ** ( 0.1 * level - 1 ) * ( n ** 2 / ( n ** 2 + n + 1.0 ) ) )
		elif status == csdefine.JUE_DI_FAN_JI_DRAW_STATUS:
			#绝地反击（1v1）平局经验、金钱奖励公式为： 
			#经验：(116 * Lv ^ 1.5 + 307) * (1 ^ 2 / (1 ^ 2 + 1 + 1)) 
			#金钱：12 * Lv * 1.5 ^ (0.1 * Lv - 1) * (1 ^ 2 / (1 ^ 2 + 1 + 1)) 
			exp = int( ( 116 * level ** 1.5 + 307 ) * ( 1/ 3.0 ) )
			money = int( 12 * level * 1.5 ** ( 0.1 * level - 1 ) * ( 1/3.0 ) )
		elif status == csdefine.JUE_DI_FAN_JI_FAILED_STATUS:
			#绝地反击（1v1）败者经验、金钱奖励公式为： 
			#经验：(58 * Lv ^ 1.5 + 153) * (1 ^ 2 / (1 ^ 2 + 1 + 1)) 
			#金钱：6 * Lv * 1.5 ^ (0.1 * Lv - 1) * (1 ^ 2 / (1 ^ 2 + 1 + 1)) 
			exp = int( ( 58 * level ** 1.5 + 153 ) * ( 1/ 3.0 ) )
			money = int( 6 * level * 1.5 ** ( 0.1 * level - 1 ) * ( 1/3.0 ) )
		playerMB.cell.addExp( exp, csdefine.CHANGE_EXP_JUE_DI_FAN_JI )
		playerMB.cell.activity_gainMoney( money, csdefine.CHANGE_MONEY_JUE_DI_FAN_JI )
			
			
	def onSelectRepeatedVictory( self, baseMailbox, dbid, hp, playerName, level, playerClass ):
		"""
		玩家选择连胜
		"""
		if self.jueDiFanJiTempHPDict.has_key( dbid ):
			playerHP = self.jueDiFanJiTempHPDict[ dbid ]
			del self.jueDiFanJiTempHPDict[ dbid ]
		else:
			playerHP = hp
		if playerHP == 0:		#按照策划的要求，如果最后玩家没有血了，给予1滴血，以保证下次进入副本的时候有1滴血
			playerHP = 1
		if not self.jueDiFanJiVictoryCountDict.has_key( dbid ):
			self.jueDiFanJiVictoryCountDict[ dbid ] = [ 1, playerHP ]
		else:
			victoryCount = self.jueDiFanJiVictoryCountDict[ dbid ][ 0 ] + 1
			self.jueDiFanJiVictoryCountDict[ dbid ] = [ victoryCount, playerHP ]
		self.jueDiFanJiDBIDToPlayerInfo[ dbid ] = [ baseMailbox, playerName, level, playerClass ]
		self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_HAS_SIGN_UP )
		self.pushJueDiFanJiQueue( dbid, level )
		
	def clearVictoryCountDict( self, dbid ):
		"""
		玩家掉线或者失败或者是平局，那么会将玩家的连胜记录删除
		"""
		if self.jueDiFanJiVictoryCountDict.has_key( dbid ):
			del self.jueDiFanJiVictoryCountDict[ dbid ]
		
	def onJueDiFanJiRoleDestroy( self, dbid ):
		"""
		绝地反击活动玩家销毁
		"""
		self.jueDiFanJiDBIDToOnlineDict[ dbid ] = 0
		
	def calJueDiFanJiRankAndNotice( self ):
		"""
		计算参赛玩家排名
		"""
		scoreList = self.jueDiFanJiScoreDict.values()
		scoreList = sorted( scoreList, compareScore )
		if len( scoreList ) <= FIRST_THIRD_RANK_NUM:
			firstThirdRankList = scoreList
		else:
			firstThirdRankList = scoreList[:FIRST_THIRD_RANK_NUM]
		playerDBIDList = []
		firstPlayerDBID = 0
		for i,record in self.jueDiFanJiScoreDict.iteritems():
			if record in firstThirdRankList:
				if record == firstThirdRankList[ 0 ]:
					firstPlayerDBID = i
				playerDBIDList.append( i )
		if firstPlayerDBID and self.jueDiFanJiDBIDToPlayerInfo.has_key( firstPlayerDBID ):
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.JUE_DI_FAN_JI_CHAMPION_BROADCAST % self.jueDiFanJiDBIDToPlayerInfo[ firstPlayerDBID ][ 1 ], [] )
		for playerInfo in self.jueDiFanJiDBIDToPlayerInfo.itervalues():
			playerMB = playerInfo[ 0 ]
			playerMB.cell.receiveBulletin( scoreList )
		self.sendFirstThirdRewardInfo( playerDBIDList )
		for playerDBID in playerDBIDList:
			if self.jueDiFanJiDBIDToPlayerInfo.has_key( playerDBID ):
				playerInfo = self.jueDiFanJiDBIDToPlayerInfo[ playerDBID ]
				self.jueDiFanJiFirstThirdRank.append( ( playerInfo[0], playerDBID, playerInfo[1], playerInfo[2], playerInfo[3] ) )
				
	def sendFirstThirdRewardInfo( self, playerDBIDList ):
		"""
		发送前三名玩家奖励信息
		"""
		msgList = []
		for playerDBID in playerDBIDList:
			if self.jueDiFanJiScoreDict.has_key( playerDBID ):
				scoreInfo = self.jueDiFanJiScoreDict[ playerDBID ]
				msgList.append( scoreInfo[0] )
				msgList.append( scoreInfo[1] )
		title = cschannel_msgs.JUE_DI_FAN_JI_FIRST_THIRD_REWARD_TITLE
		content = ""
		if len( msgList ) == LENGTH_OF_PLAYER_1 * 2:
			content = cschannel_msgs.JUE_DI_FAN_JI_FIRST_THIRD_CONTENT_2 %( msgList[0], msgList[1], msgList[2], msgList[3] )
		elif len( msgList ) == LENGTH_OF_PLAYER_2 * 2:
			content = cschannel_msgs.JUE_DI_FAN_JI_FIRST_THIRD_CONTENT_1 %( msgList[0], msgList[1], msgList[2], msgList[3], msgList[4], msgList[5] )
		for playerDBID in playerDBIDList:
			if self.jueDiFanJiDBIDToPlayerInfo.has_key( playerDBID ):
				playerInfo = self.jueDiFanJiDBIDToPlayerInfo[ playerDBID ]
				BigWorld.globalData["MailMgr"].send( None, playerInfo[1], csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC,"", title, content, 0, "" )

		
	def resetJueDiFanJiData( self ):
		"""
		重置绝地反击活动数据
		"""
		self.jueDiFanJiQueue = []							#绝地反击排队队列
		self.jueDiFanJiScoreDict = {}						#绝地反击积分字典，形如{dbid1:[playerName1, score1, victoryNum1 ],dbid2:[playerName2, score2, victoryNum2 ],...}(其中victoryNum1为净胜数，score1为积分)
		self.jueDiFanJiDBIDToPlayerInfo = {}				#绝地反击DBID对应的player信息字典，形如{dbid1:[playerMB1,playerName1,level1,playerClass1],dbid2:[playerMB2,playerName2,level2,playerClass2]}
		self.jueDiFanJiVictoryCountDict = {}				#绝地反击连胜次数记录字典
		self.jueDiFanJiStateDict = {}						#绝地反击每个玩家状态字典
		self.jueDiFanJiMatchList = []						#绝地反击匹配列表，形如[(dbid1,dbid2,匹配数字),(dbid3,dbid4,匹配数字),...](其中dbid1和dbid2是对战双方，匹配数字指的是这是多少次匹配)
		self.jueDiFanJiMatchedDBIDToIndex = {}				#绝地反击已经匹配的DBID对应的Index字典，形如{dbid1:index1,dbid2:index1,dbid3:index2,dbid4:index2,...}
		self.jueDiFanJiEmptyIndexList = []					#绝地反击空的位置索引
		self.curMaxMatchCount = 0							#目前已经匹配成功的最大数量
		self.requestCount = 0								#请求的总数量
		self.operateCount = 0								#正在操作的数量
		self.jueDiFanJiDBIDToOnlineDict = {}				#绝地反击DBID对应玩家是否在线字典,形如{123:1,234:0,...}（其中在线用1表示，不在线用0表示）

	def onAoZhanQunXiongRequest( self ):
		"""
		鏖战群雄比赛需要取得前三名的数据
		"""
		for info in self.jueDiFanJiFirstThirdRank:
			BigWorld.globalData["AoZhanQunXiongMgr"].onSignUp( info[0], info[1], info[2], info[3], info[4] )

		
		
def compareScore( a, b ):
	"""
	积分比较函数
	"""
	if a[1] < b[1]:
		return 1
	elif a[1] == b[1] and a[2] < b[2]:
		return 1
	elif a[1] == b[1] and a[2] == b[2]:
		return 0
	elif a[1] == b[1] and a[2] > b[2]:
		return -1
	elif a[1] > b[1]:
		return -1
	