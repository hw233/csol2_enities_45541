# -*- coding: gb18030 -*-

import math
import random
import copy
import time
import cPickle

import BigWorld

from bwdebug import *
import csstatus
import csdefine
import csconst
import cschannel_msgs
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from items.ItemDataList import ItemDataList
g_items = ItemDataList.instance()

import Love3

# 状态
TEAM_CHALLENGE_STAGE_FREE		= 0			# 空闲期
TEAM_CHALLENGE_STAGE_NOTICE		= 1			# 广播期
TEAM_CHALLENGE_STAGE_SIGNUP		= 2			# 报名期
TEAM_CHALLENGE_STAGE_ENTER		= 3			# 进场期
TEAM_CHALLENGE_STAGE_UNDERWAY	= 4			# 进行期
TEAM_CHALLENGE_STAGE_RESET		= 5			# 休息期

# 时间 ( 以分钟为单位 )
TEAM_CHALLENGE_TIME_DISTANCE_NOTICE 	= 15	# 下次广播时间
TEAM_CHALLENGE_TIME_DISTANCE_SIGNUP		= 5		# 下次报名广播时间

TEAM_CHALLENGE_TIME_NOTICE = TEAM_CHALLENGE_TIME_DISTANCE_NOTICE * 4	# 广播时间
TEAM_CHALLENGE_TIME_SIGNUP = TEAM_CHALLENGE_TIME_DISTANCE_SIGNUP * 3 	# 报名时间

# time userArg
TEAM_CHALLENGE_USER_ARG_NOTICE		= 1 # 广播准备报名
TEAM_CHALLENGE_USER_ARG_SIGNUP		= 2 # 广播报名
TEAM_CHALLENGE_USER_ARG_CLOSE_ENTER	= 3 # 关闭入场标志
TEAM_CHALLENGE_USER_ARG_OPEN_NEXT	= 4 # 开始下轮比赛
TEAM_CHALLENGE_USER_ARG_END			= 5 # 结束
TEAM_CHALLENGE_USER_ARG_Will_START  = 6	# 通知进入副本

CHALLENGE_CONDITION_COMMON 		= 0
CHALLENGE_CONDITION_ALL_FAIL	= 1
CHALLENGE_CONDITION_NONE_ENTER	= 2
CHALLENGE_CONDITION_CHAMPION	= 3

SPACE_KEY_FORMAT = lambda level, round, index : level * 10000 + round * 100 + index
g_teamChallengeIns = None
TEAM_CHALLENGE_JOIN_REWARD = 60101259


class RoundItem( object ):
	# 一轮的比赛
	def __init__( self ):
		self.teamList = []
		self.failList = []
		self.nextTeamList = []
		self.challengeInfo = []
		self.round = 0
		self.roundNums = 0
		self.minLevel = 0
		self.maxLevel = 0
	
	def initRound( self, tList, round, roundNums, minL, maxL ):
		# 初始化数据
		self.round = round
		self.roundNums = roundNums
		self.minLevel = minL
		self.maxLevel = maxL
		
		self.teamList = tList
		tempList = copy.deepcopy( tList )
		teamCount = len( self.teamList )
		if teamCount == 0: # 没人报名
			return
		
		if teamCount == 1:
			self.nextTeamList.append( random.choice( self.teamList ) )
			BigWorld.globalData[ "TeamManager" ].setMessage( self.nextTeamList[ -1 ], csstatus.TEAM_CHALLENGE_NOT_OPPONENT )
			return
		
		if teamCount % 2: # 如果队伍数量是单数的，则随机抽取一支队伍轮空
			teamID = random.choice( self.teamList ) 
			self.nextTeamList.append( teamID )
			tempList.remove( teamID )
			BigWorld.globalData[ "TeamManager" ].setMessage( teamID, csstatus.TEAM_CHALLENGE_NOT_OPPONENT )
			
		while( True ):
			cteamID1 = random.choice( tempList )
			tempList.remove( cteamID1 )
			cteamID2 = random.choice( tempList )
			tempList.remove( cteamID2 )
			self.challengeInfo.append( (cteamID1, cteamID2) )
			# 通知队伍集合
			BigWorld.globalData[ "TeamManager" ].teamChallengeGather( cteamID1, self.round + 1 )
			BigWorld.globalData[ "TeamManager" ].teamChallengeGather( cteamID2, self.round + 1 )
			if not len( tempList ):
				break
	
	def onCloseEnter( self ):
		BigWorld.globalData[ "TeamManager" ].teamChallengeCloseGather( self.teamList )
		for c in self.challengeInfo:
			if not g_teamChallengeIns.playerEnterInfos.has_key( c[0] ) and not g_teamChallengeIns.playerEnterInfos.has_key( c[1] ):
				# 当这场比赛没人进入
				self.setResultMessage( c[0], c[1], CHALLENGE_CONDITION_NONE_ENTER )
				self.failList.append( c[0] )
				self.failList.append( c[1] )
		
	def getNextTeamList( self ):
		# 获取下一轮比赛的名单
		return self.nextTeamList
	
	def teamWin( self, teamID ):
		# 胜出队伍
		self.nextTeamList.append( teamID )
		
		# 发放奖励
		for cInf in self.challengeInfo:
			if teamID in cInf:
				if cInf[ 0 ] == teamID:
					self.failList.append( cInf[ 1 ] )
					g_teamChallengeIns.rewardTeam( cInf[ 0 ], csconst.TEAM_CHALLENGE_REWARD_WIN )
					if self.round == self.roundNums-1:
						self.setResultMessage( cInf[ 0 ], cInf[ 1 ],  CHALLENGE_CONDITION_CHAMPION )
					else:
						self.setResultMessage( cInf[ 0 ], cInf[ 1 ],  CHALLENGE_CONDITION_COMMON )
				else:
					self.failList.append( cInf[ 0 ] )
					g_teamChallengeIns.rewardTeam( cInf[ 1 ], csconst.TEAM_CHALLENGE_REWARD_WIN )
					if self.round == self.roundNums - 1:
						self.setResultMessage( cInf[ 1 ], cInf[ 0 ], CHALLENGE_CONDITION_CHAMPION )
					else:
						self.setResultMessage( cInf[ 1 ], cInf[ 0 ], CHALLENGE_CONDITION_COMMON )
					
				break
				
		if len( self.teamList ) == 2: # 决出冠军
			g_teamChallengeIns.setChampion( teamID, self.minLevel, self.maxLevel )
	
	def teamDraw( self, teamID_1, teamID_2 ):
		if teamID_1 in self.teamList and teamID_2 in self.teamList:
			self.setResultMessage( teamID_1, teamID_2, CHALLENGE_CONDITION_ALL_FAIL )
			self.failList.append( teamID_1 )
			self.failList.append( teamID_2 )
		
	def setResultMessage( self, teamID_1, teamID_2, condition ):
		# 正常情况teamID_1为胜利队伍,teamID_2失败队伍，也有可能两队都失败了
		# 向队伍发送比赛结果
		if condition == CHALLENGE_CONDITION_COMMON:
			if g_teamChallengeIns.playerEnterInfos.has_key( teamID_2 ):
				BigWorld.globalData[ "TeamManager" ].setMessage( teamID_1, csstatus.TEAM_CHALLENGE_WIN )
				BigWorld.globalData[ "TeamManager" ].setMessage( teamID_2, csstatus.TEAM_CHALLENGE_FAIL )
				BigWorld.globalData[ "TeamManager" ].setMessage( teamID_2, csstatus.TEAM_CHALLENGE_JOIN_REWARD ) # 发送安慰奖通知
			else:
				BigWorld.globalData[ "TeamManager" ].setMessage( teamID_1, csstatus.TEAM_CHALLENGE_OPPONENT_NOT_ENTER )
				BigWorld.globalData[ "TeamManager" ].setMessage( teamID_2, csstatus.TEAM_CHALLENGE_NOT_ENTER )
				BigWorld.globalData[ "TeamManager" ].setMessage( teamID_2, csstatus.TEAM_CHALLENGE_JOIN_REWARD ) # 发送安慰奖通知
				
		elif condition == CHALLENGE_CONDITION_ALL_FAIL:
			if self.round == self.roundNums - 1:
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TEAM_CHALLENGE_ALL_FAIL_LAST%( self.minLevel , self.maxLevel, ), [] )
				BigWorld.globalData[ "TeamManager" ].setMessage( teamID_1, csstatus.TEAM_CHALLENGE_FAIL_LAST )
				BigWorld.globalData[ "TeamManager" ].setMessage( teamID_2, csstatus.TEAM_CHALLENGE_FAIL_LAST )
			else:
				BigWorld.globalData[ "TeamManager" ].setMessage( teamID_1, csstatus.TEAM_CHALLENGE_ALL_FAIL )
				BigWorld.globalData[ "TeamManager" ].setMessage( teamID_2, csstatus.TEAM_CHALLENGE_ALL_FAIL )
				BigWorld.globalData[ "TeamManager" ].setMessage( teamID_1, csstatus.TEAM_CHALLENGE_JOIN_REWARD ) # 发送安慰奖通知
				BigWorld.globalData[ "TeamManager" ].setMessage( teamID_2, csstatus.TEAM_CHALLENGE_JOIN_REWARD ) # 发送安慰奖通知
	
		elif condition == CHALLENGE_CONDITION_NONE_ENTER:
			BigWorld.globalData[ "TeamManager" ].setMessage( teamID_1, csstatus.TEAM_CHALLENGE_NOT_ENTER )
			BigWorld.globalData[ "TeamManager" ].setMessage( teamID_2, csstatus.TEAM_CHALLENGE_NOT_ENTER )
			BigWorld.globalData[ "TeamManager" ].setMessage( teamID_1, csstatus.TEAM_CHALLENGE_JOIN_REWARD ) # 发送安慰奖通知
			BigWorld.globalData[ "TeamManager" ].setMessage( teamID_2, csstatus.TEAM_CHALLENGE_JOIN_REWARD ) # 发送安慰奖通知
			
		elif condition == CHALLENGE_CONDITION_CHAMPION:
			BigWorld.globalData[ "TeamManager" ].setMessage( teamID_2, csstatus.TEAM_CHALLENGE_FAIL_LAST )
			BigWorld.globalData[ "TeamManager" ].setMessage( teamID_2, csstatus.TEAM_CHALLENGE_JOIN_REWARD ) # 发送安慰奖通知
	
	def teamDismiss( self, teamID ):
		if teamID in self.nextTeamList:
			self.nextTeamList.remove( teamID )
	
	def getSpaceKey( self, teamID ):
		index = -1
		for i, rdata in enumerate( self.challengeInfo ):
			if teamID in rdata:
				index = i
				break
				
		if index == -1:
			return None
		
		return SPACE_KEY_FORMAT( self.minLevel, self.round, index )

class LevelItem( object ):
	# 一个等级段的比赛
	def __init__( self, minL, maxL):
		self.minLevel = minL
		self.maxLevel = maxL
		self.signUpList = []		 # 报名列表
		self.substituteList = [] 	 # 替补列表
		self.onSubstituteInfos = {}	 # 系统正在分配候补的列表
		self.recruitInfos = {}		 # 招募队伍列表
		self.recruitTeamMaiBox = {}
		self.onRecruitInfos = {}	 # 系统正在分配队伍的列表
		self.roundItemList = [] 	 # 轮数控制对象列表
		self.currentRound = 0
		self.roundNums = 0			 # 本阶段一共进行多少轮比赛
		self.isFinal = False		 # 是否决赛
	
	def signUp( self, teamID, cLevel, captianMailBox  ):
		# 报名
		if teamID in self.signUpList:
			# 防止队伍人员全改变了，一个队伍报了好几个等级段
			self.signUpList.remove( teamID )
			
		if self.checkLevel( cLevel ):
			if len( self.signUpList ) > csconst.TEAM_CHALLENGE_MAX_NUM - 1:
				captianMailBox.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_FULL, "" )
				return False
				
			self.signUpList.append( teamID )
			BigWorld.globalData[ "TeamManager" ].teamChallengeUpLevel( teamID, self.maxLevel, self.minLevel )
			return True
	
	def substitutePlayer( self, playerMailBox, playerLevel ):
		# 玩家申请加入修补列表
		if self.checkLevel( playerLevel ):
			if self.isFinal:
				playerMailBox.client.onStatusMessage( csstatus.TEAM_CHALLENGE_LEVEL_FINAL, "" )
				return True
			elif playerMailBox.id in [ mb.id for mb in self.substituteList ]:
				playerMailBox.client.onStatusMessage( csstatus.TEAM_CHALLENGE_TIBU_ALREADY, "" )
				return True
				
			self.substituteList.append( playerMailBox )
			playerMailBox.client.onStatusMessage( csstatus.TEAM_CHALLENGE_TIBU_SUCCEED, "" )
			
			# 判断当前是否已经有队伍报名了，开启分配
			if len( self.recruitInfos ):
				self.recruitTeamStart()
			return True
	
	def calcelSubstitute( self, playerMailBox ):
		# 玩家退出替补名单
		if playerMailBox.id in [ mb.id for mb in self.substituteList ]:
			for index, pMB in enumerate( self.substituteList ):
				if pMB.id == playerMailBox.id:
					del self.substituteList[ index ]
					playerMailBox.client.challengeTeamOnCancelSub()
					break
			
	def onSubstitutePlayer( self, playerMailBox, playerLevel ):
		# 玩家已经完成招募
		if self.checkLevel( playerLevel ):
			for index, mailbox in enumerate( self.substituteList ):
				if mailbox.id == playerMailBox.id:
					del self.substituteList[ index ]
					break
	
	def recruitTeam( self, teamMailBox, captainMailBox, tLevel, rNum ):
		# 队伍申请招募成员
		teamID = teamMailBox.id
		if self.checkLevel( tLevel ):
			if self.isFinal:
				captainMailBox.client.onStatusMessage( csstatus.TEAM_CHALLENGE_CANNOT_ZHAOMU, "" )
				return False
			elif teamID not in self.signUpList:
				# 没报名
				captainMailBox.client.onStatusMessage( csstatus.TEAM_CHALLENGE_ZHAOMU_TEAM_NOT_SIGNUP, "" )
				return False
			elif teamID in self.recruitInfos:
				# 已经在列表中
				captainMailBox.client.onStatusMessage( csstatus.TEAM_CHALLENGE_ZHAOMU_SUCCEED, "" )
				return False
			elif len( self.roundItemList ) and (\
					teamID not in self.roundItemList[ self.currentRound ].teamList or \
					teamID in self.roundItemList[ self.currentRound ].failList \
				):
				# 队伍已经被淘汰
				captainMailBox.client.onStatusMessage( csstatus.TEAM_CHALLENGE_CANNOT_ZHAOMU, "" )
				return False
				
			self.recruitInfos[ teamID ] = rNum if rNum > 1 else 1
			self.recruitTeamMaiBox[ teamID ] = teamMailBox
			teamMailBox.teamChallengeOnRecruit()
			#captainMailBox.client.onStatusMessage( csstatus.TEAM_CHALLENGE_ZHAOMU_SUCCEED, "" )
			BigWorld.globalData[ "TeamManager" ].setMessage( teamID, csstatus.TEAM_CHALLENGE_ZHAOMU_SUCCEED )
			
			# 判断当前是否已经有玩家报名替补了，开启分配
			if len( self.substituteList ):
				self.recruitTeamStart()
			return True
	
	def cancelRecruitTeam( self, teamMailBox ):
		# 队伍取消招募
		if self.recruitInfos.has_key( teamMailBox.id ):
			self.recruitInfos.pop( teamMailBox.id )
			self.recruitTeamMaiBox.pop( teamMailBox.id )
			teamMailBox.teamChallengeCancelRecruit()				
	
	def recruitTeamStart( self ):
		# 开始分配
		for k, v in copy.deepcopy( self.onRecruitInfos ).iteritems():
			# 清理分配队伍名单
			if time.time() - v > csconst.TEAM_CHALLENGE_RECRUIT_DIALOG_TIME:
				self.onRecruitInfos.pop( k )
		
		for k, v in copy.deepcopy( self.onSubstituteInfos ).iteritems():
			# 清理分配替补名单
			if time.time() - v > csconst.TEAM_CHALLENGE_RECRUIT_DIALOG_TIME:
				self.onSubstituteInfos.pop( k )
		
		if len( self.recruitInfos ) == 0 or len( self.onRecruitInfos ) == len( self.recruitInfos ):
			# 没队伍报名/队伍已经分配完毕
			return
			
		if len( self.substituteList ) == 0 or len( self.substituteList ) == len( self.onSubstituteInfos ):
			# 没人报名替补/替补人员已经分配完毕
			return
		
		tempInfos = copy.deepcopy( self.recruitInfos )
		for teamID, recruitNum in tempInfos.iteritems():
			if teamID not in self.roundItemList[ self.currentRound ].teamList:
				self.recruitInfos.pop( teamID )
				continue
				
			if teamID in self.onRecruitInfos:
				continue
			
			currentTime = time.time()
			self.onRecruitInfos[ teamID ] = currentTime
			for i in xrange( recruitNum ):
				pMB = self.randomGetPlayer()
				if pMB == None:
					return
					
				pMB.client.challengeTeamBeRecruit( teamID )
				self.onSubstituteInfos[ pMB.id ] = currentTime
	
	def randomGetPlayer( self ):
		# 随机从替补名单出取出一个
		if len( self.substituteList ) == len( self.onSubstituteInfos ):
			return None
		
		canDistribute = []
		for player in self.substituteList:
			if player.id in self.onSubstituteInfos:
				continue
			
			canDistribute.append( player )
		
		return random.choice( canDistribute ) 

	def recruitTeamSucceed( self, teamID, playerMailBox ):
		# 招募成功
		recruitNum = self.recruitInfos[ teamID ]
		if recruitNum <= 1:
			self.recruitInfos.pop( teamID )
			self.recruitTeamMaiBox[ teamID ].teamChallengeRecruitComplete()
			self.recruitTeamMaiBox.pop( teamID )
		else:
			self.recruitInfos[ teamID ] = recruitNum - 1
			
		self.onRecruitInfos.pop( teamID )
			
	def recruitTeamFailed( self, teamID, playerMailBox ):
		# 招募失败
		if self.onRecruitInfos.has_key( teamID ):
			self.onRecruitInfos.pop( teamID )
			
		if self.onSubstituteInfos.has_key( playerMailBox.id ):
			self.onSubstituteInfos.pop( playerMailBox.id )
		
	def initChallengeData( self ):
		# 准备开始比赛，初始化数据
		teamNums = len( self.signUpList )
		round = 0
		if teamNums == 0:
			return
		elif teamNums == 1:
			self.roundItemList.append( RoundItem() )
		else:
			lengList = len( self.signUpList )
			if lengList <= 2:
				round = 1
			else:
				round = int( math.ceil( math.log( lengList, 2 ) ) )
				
		for i in xrange( round ):
			self.roundItemList.append( RoundItem() )
		
		self.roundNums = len( self.roundItemList )
	
	def startRound( self, rnum ):
		# result 比赛是否已经结束 否：已经结束，是：还在继续
		# 开始一轮比赛
		if rnum == 1:
			self.initChallengeData()
		if rnum > self.roundNums:
			# 当前级别的所有比赛已经完毕
			return False
		
		nextList = []
		self.currentRound = rnum - 1
		try:
			startItem = self.roundItemList[ self.currentRound ]
		except IndexError:
			ERROR_MSG( "roundItemList is index %d Error!!"%( self.currentRound ) )
			return False
		
		challengeResult = len( self.roundItemList ) - self.currentRound # 计算当前属于第几强
		if rnum == 1:
			nextList = copy.deepcopy( self.signUpList )
		else:
			nextList = self.roundItemList[ self.currentRound - 1 ].getNextTeamList()
			roundTeam = self.roundItemList[ self.currentRound - 1 ].teamList
			votedOffList = list( set( roundTeam ) ^ set( nextList ) ) # 取出被淘汰的队伍
			if len( votedOffList ):
				BigWorld.globalData[ "TeamManager" ].teamChallengeSetResult( votedOffList, challengeResult )
		
		if len( nextList ) <= 2:
			self.clearRecruitInfos()
			BigWorld.globalData[ "TeamManager" ].teamChallengeSetResult( nextList, csdefine.MATCH_LEVEL_FINAL ) 
			self.isFinal = True
			
		if len( nextList ) == 1:
			#冠军已经决出
			championTeamID = nextList[ 0 ]
			g_teamChallengeIns.setChampion( championTeamID, self.minLevel, self.maxLevel )
			return False
			
		startItem.initRound( nextList, self.currentRound, self.roundNums, self.minLevel, self.maxLevel )
		BigWorld.globalData[ "TeamManager" ].teamChallengeUpInfo( nextList, challengeResult ) # 更新队伍的当前比赛排行
		return True
	
	def onCloseEnter( self ):
		# 当关闭进入副本的时候触发
		for item in self.roundItemList:
			item.onCloseEnter()
	
	def teamWin( self, teamID ):
		if teamID in self.signUpList:
			roundItem  = self.roundItemList[ self.currentRound ]
			roundItem.teamWin( teamID )
			return True
		
		return False
	
	def teamDraw( self, teamID_1, teamID_2 ):
		if teamID_1 in self.signUpList and teamID_2 in self.signUpList:
			roundItem  = self.roundItemList[ self.currentRound ]
			roundItem.teamDraw( teamID_1, teamID_2 )
			return True
		
		return False
	
	def endChallenge( self ):
		# 活动结束,通过本阶段的所有队伍
		for tMB in self.recruitTeamMaiBox.values():
			tMB.teamChallengeCancelRecruit()
			
		BigWorld.globalData[ "TeamManager" ].teamChallengeClose( self.signUpList )
	
	def clearRecruitInfos( self ):
		# 清空掉招募信息
		for tMB in self.recruitTeamMaiBox.values():
			tMB.teamChallengeCancelRecruit()
		
		for pMB in self.substituteList:
			pMB.client.challengeTeamOnCancelSub()
			
		self.substituteList = [] 	 # 替补列表
		self.onSubstituteInfos = {}	 # 系统正在分配候补的列表
		self.recruitInfos = {}		 # 招募队伍列表
		self.recruitTeamMaiBox = {}
		self.onRecruitInfos = {}	 # 系统正在分配队伍的列表
		
	def hasGame( self, teamID ):
		if teamID in self.signUpList:
			if len( self.roundItemList ) <= self.currentRound:
				return True
				
		return False
	
	def isWin( self, teamID ):
		if teamID in self.signUpList:
			roundItem  = self.roundItemList[ self.currentRound ]
			if teamID in roundItem.getNextTeamList():
				return True
			
		return False
	
	def isJoin( self, teamID ):
		if teamID in self.signUpList:
			roundItem  = self.roundItemList[ self.currentRound ]
			if teamID in roundItem.teamList:
				return True
			
		return False
		
	def teamDismiss( self, teamID ):
		if teamID in self.signUpList:
			self.signUpList.remove( teamID )
			roundItem  = self.roundItemList[ self.currentRound ]
			roundItem.teamDismiss( teamID )
			if teamID in self.recruitInfos:
				self.recruitInfos.pop( teamID )
			
			if teamID in self.recruitTeamMaiBox:
				self.recruitTeamMaiBox.pop( teamID )
			return True
		
		return False
	
	def playerDestroy( self, playerBaseMB ):
		if playerBaseMB.id in [ mb.id for mb in self.substituteList ]:
			for index, pMB in enumerate( self.substituteList ):
				if pMB.id == playerBaseMB.id:
					del self.substituteList[ index ]
					return True
	
	def getSpaceKey( self, teamID ):
		if teamID in self.signUpList:
			roundItem  = self.roundItemList[ self.currentRound ]
			spaceKey = roundItem.getSpaceKey( teamID )
			return spaceKey
		
		return None
			
	def checkLevel( self , cLevel ):
		return cLevel >= self.minLevel and  cLevel <= self.maxLevel

class TeamChallengeMgr( BigWorld.Base ):
	# 组队擂台管理器
	def __init__( self ):
		BigWorld.Base.__init__( self )
		self.teamChallengeNum = 0 # 记录当前组队擂台开启的次数
		self.teamChallengeDestroyNum = 0 # 记录当前清空哪一次开启的数据
		self.registerGlobally( "TeamChallengeMgr", self._onRegisterManager )
		self._CList = []
		self.currentStage = TEAM_CHALLENGE_STAGE_FREE
		self.noticeWillSignUpTimeID = 0
		self.noticeSignUpTimeID = 0
		self.noticeWillSignUpNum = TEAM_CHALLENGE_TIME_NOTICE / TEAM_CHALLENGE_TIME_DISTANCE_NOTICE
		self.noticeSignUpNum = TEAM_CHALLENGE_TIME_SIGNUP / TEAM_CHALLENGE_TIME_DISTANCE_SIGNUP
		
		self.currentRound = 0					 # 当前比赛第几轮
		self.currentRoundStartTime = 0
		self.joinActivityPlayers = []
		
		self.hasEnterDBIDs = []
		self.playerEnterInfos = {}			# 进入人员列表，奖励用，mailbox
		self.playerEnterDBIDInfos = {}		# 进入人员列表，奖励用，dbid
		self.championInfos = {}				# 冠军的DBID，奖励冠军专用
		self.timerIDLists = [] 				# 记录当前所有添加的定时器列表
		
		global g_teamChallengeIns
		g_teamChallengeIns = self
	
	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register TeamChallengeMgr Fail!" )
			self.registerGlobally( "TeamChallengeMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["TeamChallengeMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("TeamChallengeMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"TeamChallenge_start" : "onStart",
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )

	def initChallenge( self ):
		self.teamChallengeNum += 1
		self.startTime = time.time()
		self.championInfos = {} # 重置冠军信息
		self.joinActivityPlayers = [] # 重置参与玩家信息
		clevel = csconst.TEAM_CHALLENGE_JOIN_LEVEL_MIN
		while( True ):
			minL = clevel
			maxL = clevel + csconst.TEAM_CHALLENGE_JOIN_LEVEL_INCREASE
			clevel = maxL + 1
			if clevel >= csconst.TEAM_CHALLENGE_JOIN_LEVEL_MAX:
				maxL = csconst.TEAM_CHALLENGE_JOIN_LEVEL_MAX
				self._CList.append( LevelItem( minL, maxL ) )
				break
				
			self._CList.append( LevelItem( minL, maxL ) )
	
	def endChallenge( self ):
		# 结束本次活动
		self.cleanCurrentAllTimer()
		for lItem in self._CList: # 通过各阶段的比赛结束
			lItem.endChallenge()
			
		self._CList = []
		if self.currentStage != TEAM_CHALLENGE_STAGE_FREE:
			self.rewardJoin()
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TEAM_CHALLENGE_CLOSE_NOTIFY, [] )
		
		self.currentStage = TEAM_CHALLENGE_STAGE_FREE
		self.noticeWillSignUpTimeID = 0
		self.noticeSignUpTimeID = 0
		self.noticeWillSignUpNum = TEAM_CHALLENGE_TIME_NOTICE / TEAM_CHALLENGE_TIME_DISTANCE_NOTICE
		self.noticeSignUpNum = TEAM_CHALLENGE_TIME_SIGNUP / TEAM_CHALLENGE_TIME_DISTANCE_SIGNUP
		
		self.currentRound = 0					 # 当前比赛第几轮
		self.currentRoundStartTime = 0
		self.hasEnterDBIDs = []
		self.playerEnterInfos = {}
		self.playerEnterDBIDInfos = {}
	
	def rewardJoin( self ):
		# 给所有参与玩家参与奖励
		mailMgr = BigWorld.globalData[ "MailMgr" ]
		item = g_items.createDynamicItem( TEAM_CHALLENGE_JOIN_REWARD )
		tempDict = item.addToDict()
		del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
		itemData = cPickle.dumps( tempDict, 0 )
		for inf in self.joinActivityPlayers:
			mailMgr.sendWithMailbox( 
				None, \
				inf[ 0 ], \
				inf[ 1 ], \
				csdefine.MAIL_TYPE_QUICK, \
				csdefine.MAIL_SENDER_TYPE_NPC, \
				cschannel_msgs.TEAM_CHALLENGE_MAIL_SEND_NAME, \
				cschannel_msgs.TEAM_CHALLENGE_MAIL_TITILE, \
				"", \
				0, \
				[ itemData,]\
			)
	
	def signUp( self, teamID, tLevel, captianMailBox ):
		# define method
		# 报名
		if self.currentStage != TEAM_CHALLENGE_STAGE_SIGNUP:
			captianMailBox.client.onStatusMessage( csstatus.TEAM_CHALLENGE_NOT_SIGN_UP_TIME, "" )
			return
		
		isSucceed = False
		for lItem in self._CList:
			if lItem.signUp( teamID, tLevel, captianMailBox ):
				captianMailBox.client.onStatusMessage( csstatus.TEAM_CHALLENGE_SIGN_UP_SUCCEED, "" )
				isSucceed = True
		
		INFO_MSG( "TeamChallengeMgr", "signup", "" )
		assert isSucceed, "team challenge sign up is failed teamID %d, team level %d, captian %s" % ( teamID, tLevel, captianMailBox )
	
	def substitutePlayer( self, playerMailBox, playerLevel ):
		# define method
		# 玩家申请加入修补列表
		if self.currentStage < TEAM_CHALLENGE_STAGE_SIGNUP:
			playerMailBox.client.onStatusMessage( csstatus.TEAM_CHALLENGE_TIBU_FAILED, "" )
			return 
			
		isSucceed  = False
		for lItem in self._CList:
			if lItem.substitutePlayer( playerMailBox, playerLevel ):
				isSucceed = True
				break
				
		if not isSucceed:
			DEBUG_MSG( "player %s ( level %d ) add substitute list failed"%( playerMailBox, playerLevel ) )
	
	def calcelSubstitute( self, playerMailBox ):
		# define method
		# 玩家退出替补名单
		for lItem in self._CList:
			lItem.calcelSubstitute( playerMailBox )
	
	def recruitTeam( self, teamMailBox, captainMailBox, tLevel, rNum ):
		# define method
		# 队伍申请招募成员
		if self.currentStage <= TEAM_CHALLENGE_STAGE_SIGNUP:
			captainMailBox.client.onStatusMessage( csstatus.TEAM_CHALLENGE_ZHAOMU_FAILED, "" )
			return 
			
		for lItem in self._CList:
			lItem.recruitTeam( teamMailBox, captainMailBox, tLevel, rNum  )
	
	def cancelRecruitTeam( self, teamMailBox ):
		# define method
		# 队伍取消招募
		for lItem in self._CList:
			lItem.cancelRecruitTeam( teamMailBox )
	
	def recruitRresult( self, playerMailBox, playerLevel, teamID, result ):
		# define method
		# 招募结果
		item = None
		for lItem in self._CList:
			if lItem.checkLevel( playerLevel ):
				item = lItem
				break
		
		if item == None:
			ERROR_MSG( "playerLevel %d is error!"%playerLevel )
			return 
		
		if result:
			item.recruitTeamSucceed( teamID, playerMailBox )
		else:
			item.recruitTeamFailed( teamID, playerMailBox )
		
	def teamDismiss( self, teamID ):
		# define method
		# 某队伍解散
		for lItem in self._CList:
			if lItem.teamDismiss( teamID ):
				break
				
	def playerDestroy( self, playerBaseMB ):
		# define method
		# 某玩家下线
		for lItem in self._CList:
			if lItem.playerDestroy( playerBaseMB ):
				break
	
	def teamWin( self, teamID ):
		# define method
		# 某队伍胜利了
		for lItem in self._CList:
			if lItem.teamWin( teamID ):
				break
	
	def teamDraw( self, teamID_1, teamID_2 ):
		# define method
		# 某场比赛打平了
		for lItem in self._CList:
			if lItem.teamDraw( teamID_1, teamID_2 ):
				break
	
	def rewardTeam( self, teamID, type ):
		# 奖励队伍
		if self.playerEnterInfos.has_key( teamID ):
			rewardList = self.playerEnterInfos[ teamID ]
			for pMB in rewardList:
				pMB.cell.challengeTeamReward( type, self.currentRound )
		else:
			ERROR_MSG( "team %d is no member in space !!!"%teamID )
	
	def setChampion( self, teamID, minLevel, maxLevel ):
		# 决出冠军
		rewardList = []
		if self.playerEnterDBIDInfos.has_key( teamID ):
			rewardList = self.playerEnterDBIDInfos[ teamID ]
		
		rewardTime = self.startTime + csconst.CHALLENGE_CHAMPION_REWARD_LIVING
		BigWorld.globalData[ "TeamManager" ].teamChallengeChampion( teamID, rewardList, minLevel, maxLevel, rewardTime )
	
	def getChampionReward( self, dbid, playerMailBox ):
		# define method
		# 领取冠军奖励
		if self.championInfos.has_key( dbid ):
			if self.championInfos[ dbid ]:
				# 已经领过奖励
				playerMailBox.client.onStatusMessage( csstatus.TEAM_CHALLENGE_REWARD_ALREADY, "" )
			else:
				self.championInfos[ dbid ] = True
				playerMailBox.cell.getTeamChallengeReward( csconst.TEAM_CHALLENGE_REWARD_CHAMPION, 0 )
		else:
			playerMailBox.client.onStatusMessage( csstatus.TEAM_CHALLENGE_REWARD_UN_CHAMPION, "" )
	
	def onStart( self ):
		# define method
		# 活动开启
		self.initChallenge() # 初始化数据
		self.noticeWillStartSignUp()
		INFO_MSG( "TeamChallengeMgr", "start", "" )
		
	
	def onEnd( self ):
		# define method
		# 结束活动
		if self.currentStage == TEAM_CHALLENGE_STAGE_FREE:
			return
		
		if self.currentStage == TEAM_CHALLENGE_STAGE_NOTICE:
			self.delTimer( self.noticeWillSignUpTimeID )
			self.noticeSignUp()
			return
		
		if self.currentStage == TEAM_CHALLENGE_STAGE_SIGNUP:
			self.delTimer( self.noticeSignUpTimeID )
			self.startNewRound()
			return
		if BigWorld.globalData.has_key( "TeamChallengeStart" ):
			del BigWorld.globalData[ "TeamChallengeStart" ]
		self.endChallenge()
		INFO_MSG( "TeamChallengeMgr", "end", "" )
		
	def noticeWillStartSignUp( self ):
		# 广播多久可以开始报名
		if self.currentStage > TEAM_CHALLENGE_STAGE_NOTICE:
			return
			
		if not self.noticeWillSignUpTimeID:
			self.currentStage = TEAM_CHALLENGE_STAGE_NOTICE
			self.noticeWillSignUpTimeID = self.addTimer( TEAM_CHALLENGE_TIME_DISTANCE_NOTICE * 60, TEAM_CHALLENGE_TIME_DISTANCE_NOTICE * 60, TEAM_CHALLENGE_USER_ARG_NOTICE )
			self.timerIDLists.append( self.noticeWillSignUpTimeID )
			
		if self.noticeWillSignUpNum > 0:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TEAM_CHALLENGE_WILL_SIGNUP_NOTIFY%( self.noticeWillSignUpNum * TEAM_CHALLENGE_TIME_DISTANCE_NOTICE, ), [] )
			self.noticeWillSignUpNum -= 1
		else:
			self.delTimer( self.noticeWillSignUpTimeID )
			self.noticeSignUp()
	
	def noticeSignUp( self ):
		# 广播报名时间还有多久
		if self.currentStage > TEAM_CHALLENGE_STAGE_SIGNUP:
			return
			
		if not self.noticeSignUpTimeID:
			self.currentStage = TEAM_CHALLENGE_STAGE_SIGNUP
			self.noticeSignUpTimeID = self.addTimer( TEAM_CHALLENGE_TIME_DISTANCE_SIGNUP * 60, TEAM_CHALLENGE_TIME_DISTANCE_SIGNUP * 60, TEAM_CHALLENGE_USER_ARG_SIGNUP )
			self.timerIDLists.append( self.noticeSignUpTimeID )
			
		if self.noticeSignUpNum > 0: 
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TEAM_CHALLENGE_START_SIGNUP_NOTIFY % ( self.noticeSignUpNum * TEAM_CHALLENGE_TIME_DISTANCE_SIGNUP, ), [] )
			if self.noticeSignUpNum == 1:
				self.timerIDLists.append( self.addTimer( ( TEAM_CHALLENGE_TIME_DISTANCE_SIGNUP - 1 ) * 60, 0, TEAM_CHALLENGE_USER_ARG_SIGNUP ) )
				
			self.noticeSignUpNum -= 1
		elif self.noticeSignUpNum == 0:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TEAM_CHALLENGE_START_SIGNUP_NOTIFY % 1, [] )
			self.noticeSignUpNum -= 1
			self.timerIDLists.append( self.addTimer( 60, 0, TEAM_CHALLENGE_USER_ARG_SIGNUP ) )
		else:
			self.delTimer( self.noticeSignUpTimeID )
			self.startNewRound()

	def startNewRound( self ):
		# 开启新的一轮
		if self.currentStage < TEAM_CHALLENGE_STAGE_SIGNUP:
			# 防止使用GM命令出错
			return
		if BigWorld.globalData.has_key( "TeamChallengeCloseEnter" ):
			del BigWorld.globalData["TeamChallengeCloseEnter"]
		self.cleanPreData()
		self.currentRound += 1
		INFO_MSG( "TeamChallengeMgr", "round", str( self.currentRound ) )
		if not BigWorld.globalData.has_key( "TeamChallengeStart" ):
			BigWorld.globalData[ "TeamChallengeStart" ] = True
		
		isAllComplete = True
		for lItem in self._CList:
			if lItem.startRound( self.currentRound ):
				isAllComplete = False
		
		if isAllComplete:
			#判断是否所有比赛结束
			self.endChallenge()
			return
		
		self.hasEnterDBIDs = []
		self.playerEnterInfos = {}
		self.playerEnterDBIDInfos = {}
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TEAM_CHALLENGE_WILL_BEGIN_NOTIFY, [] )
		self.currentRoundStartTime = time.time()
		self.currentStage = TEAM_CHALLENGE_STAGE_ENTER # 把当前状态设置为入场状态
		BigWorld.globalData[ "TeamChallengeCurrentRoundTime" ] = self.currentRoundStartTime
		if self.currentRound < math.log( csconst.TEAM_CHALLENGE_MAX_NUM, 2 ) + 1:
			self.timerIDLists.append( self.addTimer( csconst.TEAM_CHALLENGE_TIME_PREPARE * 60, 0, TEAM_CHALLENGE_USER_ARG_CLOSE_ENTER ) )# 添加准备定时器
			self.timerIDLists.append( self.addTimer( csconst.TEAM_CHALLENGE_TIME_ROUND * 60, 0, TEAM_CHALLENGE_USER_ARG_OPEN_NEXT ) ) # 每轮比赛的时间
		else:
			self.timerIDLists.append( self.addTimer( csconst.TEAM_CHALLENGE_TIME_PREPARE * 60, 0, TEAM_CHALLENGE_USER_ARG_CLOSE_ENTER ) ) # 添加准备定时器
			self.teamChallengeDestroyNum = self.teamChallengeNum
			self.timerIDLists.append( self.addTimer( csconst.TEAM_CHALLENGE_TIME_ROUND * 60, 0, TEAM_CHALLENGE_USER_ARG_END ) ) # 每轮比赛的时间
	
	def cleanPreData( self ):
		# 清理上一轮的临时数据
		if BigWorld.globalData.has_key( "TeamChallengeCurrentRoundTime" ):
			del BigWorld.globalData[ "TeamChallengeCurrentRoundTime" ]
			
		for i in BigWorld.globalData.keys():
			if "TeamChallengeTempID_" in i:
				del BigWorld.globalData[i]
	
	def onTimer( self, timerID, userArg ):
		# 定时器触发
		if userArg == TEAM_CHALLENGE_USER_ARG_NOTICE:
			self.noticeWillStartSignUp()
		elif userArg == TEAM_CHALLENGE_USER_ARG_SIGNUP:
			self.noticeSignUp()
		elif userArg == TEAM_CHALLENGE_USER_ARG_CLOSE_ENTER: #准备时间结束，关闭进入
			self.closeEnter()
		elif userArg == TEAM_CHALLENGE_USER_ARG_OPEN_NEXT:
			self.startNewRound()
		elif userArg == TEAM_CHALLENGE_USER_ARG_END:
			if self.teamChallengeDestroyNum == self.teamChallengeNum:
				self.endChallenge()
			
	def onEnterSpace( self, domainBase, position, direction, playerBaseMB, params ):
		"""
		Define method.
		请求进入组队擂台副本

		@param domainBase : 空间对应的domain的base mailbox
		@type domainBase : MAILBOX
		@param position : 进入空间的初始位置
		@type position : VECTOR3
		@param direction : 进入空间的初始面向
		@type direction : VECTOR3
		@param playerBaseMB : 玩家base mailbox
		@type playerBaseMB : MAILBOX
		@param params: 一些关于该entity进入space的额外参数；(domain条件)
		@type params : PY_DICT
		"""
		teamID = params[ "teamID" ]
		roleDBID = params[ "roleDBID" ]
		level = params['level']
		playerName = params['playerName']
		
		if self.currentStage == TEAM_CHALLENGE_STAGE_UNDERWAY:
			playerBaseMB.client.onStatusMessage( csstatus.TEAM_CHALLENGE_STAGE_UNDERWAY, "" )
			return
			
		if self.currentStage != TEAM_CHALLENGE_STAGE_ENTER:
			playerBaseMB.client.onStatusMessage( csstatus.TEAM_CHALLENGE_NOT_OPEN_ENTER, "" )
			return
		
		if not self.isJoin( teamID ):
			playerBaseMB.client.onStatusMessage( csstatus.TEAM_CHALLENGE_NOT_JOIN, "" )
			return
		
		if self.hasGame( teamID ):
			# 检测队伍是否还有后续的比赛
			playerBaseMB.client.onStatusMessage( csstatus.TEAM_CHALLENGE_IS_COMPLETED, "" )
			return

		if self.isWin( teamID ):					# 如果已经是胜利的玩家
			playerBaseMB.client.onStatusMessage( csstatus.TEAM_CHALLENGE_ALREADY_WIN, "" )
			return
		
		if not self.checkLevel( teamID, level ):
			playerBaseMB.client.onStatusMessage( csstatus.TEAM_CHALLENGE_TEAM_LEVEL_ERR, "" )
			return
			
		#if roleDBID in self.hasEnterDBIDs:
			#playerBaseMB.client.onStatusMessage( csstatus.TEAM_CHALLENGE_HAS_ENTER_BEFORE, "" )
			#return
			
		spaceKey = self.getSpaceKey( teamID )
		if spaceKey == None:
			return
			
		self.recordEnter( teamID, roleDBID, playerBaseMB, playerName, level )
		domainBase.onEnterTeamChallenge( position, direction, True, playerBaseMB, spaceKey )
	
	def recordEnter( self, teamID, roleDBID, playerBaseMB, playerName, playerLevel ):
		# 记录玩家进入信息
		if roleDBID not in self.hasEnterDBIDs:
			self.hasEnterDBIDs.append( roleDBID ) # 加入到已经进入过玩家列表中
		
		if self.playerEnterInfos.has_key( teamID ):
			if playerBaseMB.id not in [ mb.id for mb in self.playerEnterInfos[ teamID ] ]:
				self.playerEnterInfos[ teamID ].append( playerBaseMB )
		else:
			self.playerEnterInfos[ teamID ] = [ playerBaseMB, ]
		
		if self.playerEnterDBIDInfos.has_key( teamID ):
			if roleDBID not in self.playerEnterDBIDInfos[ teamID ]:
				self.playerEnterDBIDInfos[ teamID ].append( roleDBID )
		else:
			self.playerEnterDBIDInfos[ teamID ] = [ roleDBID, ]
		
		if playerName not in [ inf[1] for inf in self.joinActivityPlayers ]:
			self.joinActivityPlayers.append( ( playerBaseMB, playerName ) )
	
	def closeEnter( self ):
		for lItem in self._CList:
			lItem.onCloseEnter()
		self.currentStage = TEAM_CHALLENGE_STAGE_UNDERWAY
		BigWorld.globalData["TeamChallengeCloseEnter"] = True
	
	def hasGame( self, teamID ):
		# 判断当前的比赛是否完毕
		for lItem in self._CList:
			if lItem.hasGame( teamID ):
				return True
		
		return False
	
	def isWin( self, teamID ):
		# 判断队伍是否已经晋级下一轮
		for lItem in self._CList:
			if lItem.isWin( teamID ):
				return True
		
		return False
	
	def isJoin( self, teamID ):
		# 判断当前队伍是否参加本轮比赛
		for lItem in self._CList:
			if lItem.isJoin( teamID ):
				return True
		
		return False
	
	def checkLevel( self, teamID, level ):
		# 判断等级是否符合
		for lItem in self._CList:
			if teamID in lItem.signUpList:
				return lItem.checkLevel( level )
		
		return False
	
	def getSpaceKey( self, teamID ):
		# 获取地图的KEY
		for lItem in self._CList:
			spaceKey = lItem.getSpaceKey( teamID )
			if spaceKey != None:
				return spaceKey
		
		ERROR_MSG( "teamID %d get space key is error!"%teamID )
		return None
	
	def cleanCurrentAllTimer( self ):
		for tid in self.timerIDLists:
			self.delTimer( tid )
		
		self.timerIDLists = []