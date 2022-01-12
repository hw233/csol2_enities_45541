# -*- coding: gb18030 -*-
#
# $Id: Exp $


import time
import random
import math
import cPickle
import copy

import BigWorld
from bwdebug import *
from MsgLogger import g_logger
import csdefine
import csconst
import cschannel_msgs
import csstatus
import Love3
import RoleMatchRecorder
from Function import Functor
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from items import ItemDataList
g_items = ItemDataList.instance()

# 武道大会状态
WUDAO_STAGE_FREE		= 0			# 空闲期
WUDAO_STAGE_NOTICE		= 1			# 广播期
WUDAO_STAGE_SIGNUP		= 2			# 报名期
WUDAO_STAGE_UNDERWAY	= 3			# 进行期

# 时间 ( 以分钟为单位 )
WUDAO_TIME_DISTANCE_NOTICE 		= 15	# 下次广播时间
WUDAO_TIME_DISTANCE_SIGNUP		= 5		# 下次报名广播时间

WUDAO_TIME_NOTICE = WUDAO_TIME_DISTANCE_NOTICE * 4	# 广播时间
WUDAO_TIME_SIGNUP = WUDAO_TIME_DISTANCE_SIGNUP * 3 	# 报名时间

# time userArg
WUDAO_USER_ARG_NOTICE		= 1 # 广播准备报名
WUDAO_USER_ARG_SIGNUP		= 2 # 广播报名
WUDAO_USER_ARG_CLOSE_ENTER	= 3 # 关闭入场标志
WUDAO_USER_ARG_OPEN_NEXT		= 4 # 开始下轮比赛
WUDAO_USER_ARG_END			= 5 # 比武结束
WUDAO_USER_ARG_Will_START    = 6	# 间隔1min后通知进入武道大会

WU_DAO_LAST_ROUND = int( math.ceil( math.log( csconst.WUDAO_MAX_NUM, 2 ) ) ) # 武道大会的最后一轮

WU_DAO_JOIN_REWARD = 60101258

class WuDaoMgr( BigWorld.Base ):
	"""
	武道大会管理模块
	"""

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )

		self.currentStage = WUDAO_STAGE_FREE	 # 当前武道大会状态
		self.currentRound = 0					 # 当前比赛第几轮
		
		self.noticeWillSignUpNum = WUDAO_TIME_NOTICE / WUDAO_TIME_DISTANCE_NOTICE
		self.noticeSignUpNum = WUDAO_TIME_SIGNUP / WUDAO_TIME_DISTANCE_SIGNUP
		
		self.noticeWillSignUpTimeID = 0
		self.noticeSignUpTimeID = 0
		
		self.isCanEnter = False
		self.activityStartTime = 0
		
		self.joinActivityPlayers = []

		self.wuDaoDBIDDict = {}       # 报名参加武道大会角色dbid字典(根据角色等级分类) such as { level/10 : [dbid,...],... }
		self.wuDaoWinnerDBIDDict = {} # 武道大会胜利一方 such as { level/10 : [dbid,...],... }
		self.playerToSpaceDict = {}   # 当前轮次参加比赛数据 such as { level/10 : {dbid : spaceKey,...},... }
		self.wuDaoNextRound = {}      # 武道大会下一轮次 such as { level/10 : step }
		self.currentRoundStartTime = 0	  # 当前轮次比赛开始时间
		self.DBIDToBaseMailbox = {}	  # 根据角色dbid找到武道大会角色的baseMailbox

		self.hasEnterDBIDs = []		  # 在一轮比赛中 ，已经进入过的玩家

		self.sendMessageEnterWuDaoDBIDList = []	# 需要通知进入武道大会角色的databaseID的list
		self.sendMessageEnterWuDaoTime = 0		# 通知进入武道大会的轮次
		
		self.currentEnterDict = {} # 当前轮可以进入的玩家，主要是为了关闭集合使用
		
		self.championList = []

		# 把自己注册为globalData全局实体
		self.registerGlobally( "WuDaoMgr", self._onRegisterManager )

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register WuDaoMgr Fail!" )
			# again
			self.registerGlobally( "WuDaoMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["WuDaoMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("WuDaoMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"WuDaoMgr_start_notice" : "onStartNotice",
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )

	def onStartNotice( self ):
		"""
		define method.
		活动开始通知
		"""
		if self.currentStage != WUDAO_STAGE_FREE:		# 如果武道大会在进行中，无法再次开启
			ERROR_MSG( "WuDaoMgr is progressing,cannot start again.GM Wait until last time end!" )
			return
		
		self.joinActivityPlayers = []
		self.currentStage = WUDAO_STAGE_NOTICE
		self.noticeWillStartSignUp()
		self.activityStartTime = time.time()
		INFO_MSG( "WuDaoMgr", "notice", "" )
	
	def onEndNotice( self ):
		"""
		define method.
		活动结束通知
		"""
		if self.currentStage == WUDAO_STAGE_FREE:
			return
		
		if self.currentStage == WUDAO_STAGE_UNDERWAY:
			self.end_wudao()
			return
		
		if self.currentStage == WUDAO_STAGE_NOTICE:
			self.delTimer( self.noticeWillSignUpTimeID )
			self.currentStage = WUDAO_STAGE_SIGNUP
			self.noticeSignUp()
			return
		
		if self.currentStage == WUDAO_STAGE_SIGNUP:
			self.delTimer( self.noticeSignUpTimeID )
		
		self.startNewRound()
		self.currentStage = WUDAO_STAGE_UNDERWAY
		INFO_MSG( "WuDaoMgr", "notice end", "" )
		
	def noticeWillStartSignUp( self ):
		# 广播多久可以开始报名
		if self.currentStage != WUDAO_STAGE_NOTICE:
			return
			
		if not self.noticeWillSignUpTimeID:
			self.noticeWillSignUpTimeID = self.addTimer( WUDAO_TIME_DISTANCE_NOTICE * 60, WUDAO_TIME_DISTANCE_NOTICE * 60, WUDAO_USER_ARG_NOTICE )
			
		if self.noticeWillSignUpNum > 0:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.WU_DAO_DA_HUI_WILL_SIGNUP_NOTIFY%( self.noticeWillSignUpNum * WUDAO_TIME_DISTANCE_NOTICE, ), [] )
			self.noticeWillSignUpNum -= 1
		else:
			self.delTimer( self.noticeWillSignUpTimeID )
			self.currentStage = WUDAO_STAGE_SIGNUP
			self.noticeSignUp()
	
	def noticeSignUp( self ):
		# 广播报名时间还有多久
		if self.currentStage != WUDAO_STAGE_SIGNUP:
			return
			
		if not self.noticeSignUpTimeID:
			self.noticeSignUpTimeID = self.addTimer( WUDAO_TIME_DISTANCE_SIGNUP * 60, WUDAO_TIME_DISTANCE_SIGNUP * 60, WUDAO_USER_ARG_SIGNUP )
			
		if self.noticeSignUpNum > 0: 
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.WU_DAO_DA_HUI_START_SIGNUP_NOTIFY, [] )
			if self.noticeSignUpNum == 1:
				self.addTimer( ( WUDAO_TIME_DISTANCE_SIGNUP - 1 ) * 60, 0, WUDAO_USER_ARG_SIGNUP )
				
			self.noticeSignUpNum -= 1
		elif self.noticeSignUpNum == 0:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.WU_DAO_DA_HUI_START_SIGNUP_NOTIFY, [] )
			self.noticeSignUpNum -= 1
			self.addTimer( 60, 0, WUDAO_USER_ARG_SIGNUP )
		else:
			self.delTimer( self.noticeSignUpTimeID )
			if self.currentStage == WUDAO_STAGE_UNDERWAY:
				return
				
			if self.currentStage != WUDAO_STAGE_UNDERWAY:
				self.startNewRound()

	def startNewRound( self ):
		# 开启新的一轮
		if self.currentStage < WUDAO_STAGE_SIGNUP:
			# 防止使用GM指令出错
			return
		
		if self.currentRound < 0:
			return
			
		if self.currentRound == 0:
			self.currentStage = WUDAO_STAGE_UNDERWAY
			self.initWuDaoWar( copy.deepcopy( self.wuDaoDBIDDict ), self.currentRound + 1 )
			self.currentEnterDict = copy.deepcopy( self.wuDaoDBIDDict )
		else:
			self.currentEnterDict = copy.deepcopy( self.wuDaoWinnerDBIDDict )
			self.initWuDaoWar( self.wuDaoWinnerDBIDDict, self.currentRound + 1 )
		
		if self.currentRound == 0:
			return
		
		INFO_MSG( "WuDaoMgr", "round", str( self.currentRound ) )
		
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.WU_DAO_DA_HUI_WILL_BEGIN_NOTIFY%( self.currentRound, csconst.WUDAO_TIME_PREPARE ), [] )
		self.currentRoundStartTime = time.time()
		self.addTimer( csconst.WUDAO_TIME_PREPARE * 60, 0, WUDAO_USER_ARG_CLOSE_ENTER ) # 添加准备定时器
		if self.currentRound < math.log( csconst.WUDAO_MAX_NUM, 2 ):
			self.addTimer( csconst.WUDAO_TIME_ROUND * 60, 0, WUDAO_USER_ARG_OPEN_NEXT ) # 每轮比赛的时间
		else:
			self.addTimer( csconst.WUDAO_TIME_ROUND * 60, 0, WUDAO_USER_ARG_END ) # 每轮比赛的时间

	def closeEnterFlags( self ):
		# 关闭进场标志
		self.isCanEnter = False
		for dbids in self.currentEnterDict.values():
			for dbid in dbids:
				baseMailbox = self.DBIDToBaseMailbox.get( dbid )
				if baseMailbox:
					baseMailbox.cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_WUDAO )
					
				winnerList = []
				for ids in self.wuDaoWinnerDBIDDict.values():
					winnerList.extend( ids )
					
				if dbid not in self.hasEnterDBIDs and dbid not in winnerList and dbid not in self.championList: # 如果不在已经进入的列表内，那就表示他没有进入场地
					baseMailbox.client.onStatusMessage( csstatus.WU_DAO_NOT_IN_SPACE, "" )
		
	
	def updateDBIDToBaseMailbox( self, databaseID, baseMailbox ):
		"""
		更新武道大会DBIDToBaseMailbox
		"""
		if self.DBIDToBaseMailbox.has_key( databaseID ):
			self.DBIDToBaseMailbox[databaseID] = baseMailbox

	def delDBIDToBaseMailbox( self, databaseID ):
		"""
		角色下线后，删除DBIDToBaseMailbox
		"""
		if self.DBIDToBaseMailbox.has_key( databaseID ):
			self.DBIDToBaseMailbox[databaseID] = 0

	def onTimer( self, timerID, userArg ):
		"""
		执行武道大会相关操作
		"""
		if userArg == WUDAO_USER_ARG_NOTICE:
			self.noticeWillStartSignUp()
		elif userArg == WUDAO_USER_ARG_SIGNUP:
			self.noticeSignUp()
		elif userArg == WUDAO_USER_ARG_CLOSE_ENTER:
			self.closeEnterFlags()
		elif userArg == WUDAO_USER_ARG_OPEN_NEXT:
			self.startNewRound()
		elif userArg == WUDAO_USER_ARG_END:
			self.end_wudao()
		elif userArg == WUDAO_USER_ARG_Will_START:
			# 通知进入武道大会
			for e in self.sendMessageEnterWuDaoDBIDList:
				self.sendMessageEnterWuDao( e )
					
	def isSingUpFull( self, step ):
		"""
		判断武道大会某个级别的赛场是否满员
		"""
		return self.wuDaoDBIDDict.has_key( step ) and len( self.wuDaoDBIDDict[step] ) >= csconst.WUDAO_MAX_NUM

	def requestSignUp( self, level, playerBaseMailBox, playerDBID ):
		"""
		define method
		请求报名
		"""
		step = level / 10 # 每10级为一个赛场

		if self.currentStage == WUDAO_STAGE_SIGNUP:
			if self.wuDaoDBIDDict.has_key( step ) and playerDBID in self.wuDaoDBIDDict[step]:	# 如果已经报名
				playerBaseMailBox.client.onStatusMessage( csstatus.WU_DAO_SIGN_UP_ALREADY, "" )
				return
				
			if self.addToWuDao( step, playerBaseMailBox, playerDBID):
				playerBaseMailBox.client.onStatusMessage( csstatus.WU_DAO_SIGN_UP_SUCCE, "" )
				
				minLevel = step * 10
				maxLevel = minLevel + 9
				playerBaseMailBox.client.wuDaoUpLevel( maxLevel, minLevel )
			else:
				playerBaseMailBox.client.onStatusMessage( csstatus.WU_DAO_SIGN_UP_FULL, "" )
		else:
			playerBaseMailBox.client.onStatusMessage( csstatus.WU_DAO_SIGN_UP_TIME_ERR, "" )

	def addToWuDao( self, step, playerBaseMailBox, dbid ):
		"""
		请求加入武道大会
		"""
		if self.isSingUpFull( step ):
			return False

		if self.wuDaoDBIDDict.has_key( step ):
			if not dbid in self.wuDaoDBIDDict[step]:
				index = random.randint( 0, len( self.wuDaoDBIDDict[step] ) )
				self.wuDaoDBIDDict[step].insert( index, dbid ) # 对报名选手进行随机排列
		else:
			self.wuDaoDBIDDict[step] = [dbid]

		self.DBIDToBaseMailbox[dbid] = playerBaseMailBox	# 根据角色dbid存放参加舞蹈大会角色baseMailbox
		return True

	def initWuDaoWar( self, dbidDict, time ):
		"""
		初始化武道大会比赛数据,time为轮次。
		"""
		self.isCanEnter  = True  # 允许进入武道大会比赛
		self.currentRound += 1 # 当前轮次加1
		self.playerToSpaceDict.clear() # 将当前轮次参加比赛数据清空
		self.sendMessageEnterWuDaoDBIDList = []	# 将要通知进入武道大会的DBIDList清空
		enterNextRound = {}		# 获胜直接进入下一轮的

		keys = dbidDict.keys()
		for key in keys:
			for dbid in dbidDict[key]:
				baseMailbox = self.DBIDToBaseMailbox.get( dbid )
				if baseMailbox:
					baseMailbox.client.wuDaoUpInfo( self.currentRound - 1 )
				
			length = len( dbidDict[key] )		# 一个级别，有多少个参赛的
			if length == 2 :		# 如果只有2名参赛
				self.wuDaoNextRound[key] = WU_DAO_LAST_ROUND 	# 设置下一轮为最后一轮

			if length > 1 and length % 2 == 1:	# 如果是奇数个，取最后一个，直接获得胜利
				dbid = dbidDict[key][-1]
				del dbidDict[key][-1]
				length -= 1
				baseMailbox = self.DBIDToBaseMailbox.get( dbid )
				if baseMailbox :
					self.addWuDaoAward( self.currentRound, key, baseMailbox, 1 )
					baseMailbox.client.onStatusMessage( csstatus.WU_DAO_WITHOUT_ENEMY, "" )
				enterNextRound[key] = [dbid]

			teamCount = int( length / 2.0 + 0.5 )
			self.playerToSpaceDict[key] = {}
			for x in xrange( teamCount ):
				self.playerToSpaceDict[key][dbidDict[key][x*2]] = "WUDAO" + str(key*10000 + x)
				try:
					self.playerToSpaceDict[key][dbidDict[key][x*2 + 1]] = "WUDAO" + str(key*10000 + x)
				except:
					if length == 1:	# 如果只有一名参赛，则直接获得冠军
						playerBaseMB = self.DBIDToBaseMailbox.get( dbidDict[key][0] )
						if playerBaseMB:
							playerBaseMB.cell.wuDaoNoticeChampion( key, self.activityStartTime + csconst.CHALLENGE_CHAMPION_REWARD_LIVING )
							self.championList.append( dbid )
						del dbidDict[key]

		# 获得需要通知进入武道大会的DBIDList
		for dbidList in dbidDict.itervalues():
			self.sendMessageEnterWuDaoDBIDList += dbidList

		# 通知进入武道大会
		if len( self.sendMessageEnterWuDaoDBIDList ) == 0:
			self.end_wudao()
			return
			
		for e in self.sendMessageEnterWuDaoDBIDList:
			self.sendMessageEnterWuDao( e, time )

		# 间隔1min后再次通知进入武道大会
		self.addTimer( 60, 0, WUDAO_USER_ARG_Will_START )

		dbidDict.clear() # 将参赛数据清空
		self.wuDaoWinnerDBIDDict = enterNextRound	# 直接获得胜利的

	def end_wudao( self ):
		"""
		结束武道大会
		"""
		for dbid in  self.wuDaoDBIDDict:
			if self.DBIDToBaseMailbox.has_key( dbid ):
				self.DBIDToBaseMailbox[ dbid ].client.wuDaoClose()
				
		self.wuDaoDBIDDict = {}
		self.wuDaoWinnerDBIDDict = {}
		self.playerToSpaceDict = {}
		self.hasEnterDBIDs = []
		self.wuDaoNextRound = {}
		self.currentRoundStartTime = 0
		self.DBIDToBaseMailbox = {}

		self.currentStage = WUDAO_STAGE_FREE	 # 当前武道大会状态
		self.currentRound = 0					 # 当前比赛第几轮
		self.isCanEnter = False
		
		self.noticeWillSignUpNum = WUDAO_TIME_NOTICE / WUDAO_TIME_DISTANCE_NOTICE
		self.noticeSignUpNum = WUDAO_TIME_SIGNUP / WUDAO_TIME_DISTANCE_SIGNUP
		
		self.noticeWillSignUpTimeID = 0
		self.noticeSignUpTimeID = 0
		self.championList = []
		self.rewardJoin()
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.WU_DAO_DA_HUI_CLOSE_NOTIFY, [] )
		INFO_MSG( "WuDaoMgr", "end", "" )
	
	def rewardJoin( self ):
		# 给所有参与玩家参与奖励
		mailMgr = BigWorld.globalData[ "MailMgr" ]
		item = g_items.createDynamicItem( WU_DAO_JOIN_REWARD )
		tempDict = item.addToDict()
		del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
		itemData = cPickle.dumps( tempDict, 0 )
		for inf in self.joinActivityPlayers:
			baseMailbox = inf[ 0 ]
			mailMgr.sendWithMailbox( 
				None, \
				baseMailbox, \
				inf[ 1 ], \
				csdefine.MAIL_TYPE_QUICK, \
				csdefine.MAIL_SENDER_TYPE_NPC, \
				cschannel_msgs.WU_DAO_DA_HUI_MAIL_SEND_NAME, \
				cschannel_msgs.WU_DAO_DA_HUI_MAIL_TITILE, \
				"", \
				0, \
				[ itemData,]\
			)

	def isWuDaoWinner( self, roleDBID ):
		"""
		是否已经是胜利者
		"""
		for iList in self.wuDaoWinnerDBIDDict.itervalues():
			if roleDBID in iList:
				return True
			
		return False

	def isJoinWuDao( self, roleDBID ):
		"""
		角色是否在当前轮次参赛列表中
		"""
		for iDict in self.playerToSpaceDict.itervalues():
			if roleDBID in iDict:
				return True
		return False

	def onEnterWuDaoSpace( self, domainBase, position, direction, playerBaseMB, params ):
		"""
		Define method.
		请求进入武道大会副本

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
		roleDBID = params[ "roleDBID" ]			# 请求进入副本玩家的dbid
		level = params['level']
		playerName = params['playerName']
		
		currentInList = self.currentEnterDict[ level/10 ] if self.currentEnterDict.has_key( level/10 ) else []
		if not self.isCanEnter or roleDBID not in currentInList:
			playerBaseMB.client.onStatusMessage( csstatus.WU_DAO_NOT_OPEN_ENTER, "" )
			return
		
		if roleDBID in self.championList: # 已经是冠军了
			playerBaseMB.client.onStatusMessage( csstatus.WU_DAO_ALREADY_CHAMPION, "" )
			return

		if self.isWuDaoWinner( roleDBID ):					# 如果已经是胜利的玩家
			playerBaseMB.client.onStatusMessage( csstatus.WU_DAO_ALREADY_WIN, "" )
			return

		if not self.isJoinWuDao( roleDBID ):
			playerBaseMB.client.onStatusMessage( csstatus.WU_DAO_NOT_JOIN, "" )
			return

		if roleDBID not in self.hasEnterDBIDs:
			self.hasEnterDBIDs.append( roleDBID ) # 加入到已经进入过玩家列表中

		if playerName not in [ inf[1] for inf in self.joinActivityPlayers ]:
			self.joinActivityPlayers.append( ( playerBaseMB, playerName ) )
			
		enterKeyDict = {'spaceKey': self.playerToSpaceDict[level/10][roleDBID] }
		domainBase.onEnterWuDaoSpace( position, direction, True, playerBaseMB, enterKeyDict )

	def onWuDaoOverFromSpace( self, playerBaseMB, databaseID, level, result ):
		"""
		Define method.
		副本通知一场比赛结束了

		@param databaseID : 角色的dbid
		@type databaseID : DATABASE_ID
		"""
		for key in self.playerToSpaceDict:
			if self.playerToSpaceDict[key].has_key( databaseID ):
				del self.playerToSpaceDict[key][databaseID]

		self.hasEnterDBIDs.remove( databaseID ) # 正常从副本中出来
		step = level/10
		if result: # 如果为获胜方
			round = self.currentRound
			if self.wuDaoNextRound.has_key(step):
				round = WU_DAO_LAST_ROUND

			if round < WU_DAO_LAST_ROUND:
				if self.wuDaoWinnerDBIDDict.has_key( step ):
					index = random.randint( 0, len( self.wuDaoWinnerDBIDDict[step] ) )
					self.wuDaoWinnerDBIDDict[step].insert( index, databaseID ) # 对选手进行随机排序
				else:
					self.wuDaoWinnerDBIDDict[step] = [databaseID]
				nextRoundTime = int( (csconst.WUDAO_TIME_ROUND * 60 + self.currentRoundStartTime - time.time())/60 )	# 通知获胜方参加下一轮比赛
				playerBaseMB.client.onStatusMessage( csstatus.WU_DAO_NEXT_ROUND_TIME, "(\'%s\',)" % nextRoundTime )
			
			self.addWuDaoAward( round, step, playerBaseMB, True )
			if round == WU_DAO_LAST_ROUND:
				playerBaseMB.cell.wuDaoNoticeChampion( step, self.activityStartTime + csconst.CHALLENGE_CHAMPION_REWARD_LIVING )
				self.championList.append( databaseID )
				RoleMatchRecorder.update( databaseID, csdefine.MATCH_TYPE_PERSON_ABA, 0, playerBaseMB ) #设置活动信息

		else: # 如果为失败方
			self.addWuDaoAward( self.currentRound, step, playerBaseMB, False )
			re = self.currentRound
			memNums = len( self.wuDaoDBIDDict[ step ] )
			re = int( math.ceil( math.log( memNums, 2 ) ) ) - self.currentRound
			RoleMatchRecorder.update( databaseID, csdefine.MATCH_TYPE_PERSON_ABA, re, playerBaseMB )#设置活动信息

	def addWuDaoAward( self, round, step, playerBaseMB, isWinner ):
		"""
		加上相应奖励

		@param round : 奖励轮次
		@param playerBaseMB : 获得奖励角色mail_box
		@param isWinner : 是否胜利者
		@type isWinner : BOOL
		"""
		playerBaseMB.cell.wuDaoReward( round, step, isWinner )

# 根据databaseID寻找相应的角色，通知其参加武道大会
	def sendMessageEnterWuDao( self, databaseID, time = 0 ):
		"""
		通知客户端，要进入武道大会了
		"""
		if time != 0:
			self.sendMessageEnterWuDaoTime = time

		playerBaseMB = self.DBIDToBaseMailbox.get( databaseID )
		if playerBaseMB:
			playerBaseMB.client.wuDaoGather( self.sendMessageEnterWuDaoTime )
			playerBaseMB.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_WUDAO )
		#BigWorld.lookUpBaseByDBID( "Role", databaseID, Functor( self.sendMessageEnterWuDaoCB, self.sendMessageEnterWuDaoTime ) )

#	def sendMessageEnterWuDaoCB( self, time, callResult ):
		"""
		查询回调函数
		"""
#		if callResult != True and callResult != False:
#			callResult.client.receiveMessageEnterWuDao( time )

	def selectEnterWuDao( self, databaseID ):
		"""
		角色选择进入武道大会，不需要再通知了
		"""
		if databaseID in self.sendMessageEnterWuDaoDBIDList:
			self.sendMessageEnterWuDaoDBIDList.remove( databaseID )

#$Log:$
#
