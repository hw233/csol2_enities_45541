# -*- coding: gb18030 -*-
#

from bwdebug import *
import cschannel_msgs
import ShareTexts as ST

import BigWorld
import Love3
import csdefine
import csconst
import time
import copy

import random #add by wuxo 2012-1-30
import csstatus #add by wuxo 2012-5-3
from QuizGameLoader import quizGameLoader
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from MsgLogger import g_logger


NOTICE_INTERVAL1 = 60*9		# 第二次通知的时间间隔
NOTICE_INTERVAL2 = 30			# 第三次通知的时间间隔
READY_INTERVAL = 30		# 答题准备时间

TIMER_NOTICE_INTERVAL1		= 1
TIMER_QUESTION_INTERVAL	= 2
TIMER_READY_FOR_QUESTION	= 3
TIMER_NOTICE_INTERVAL2		= 4

ANSWER_MAP =  [ "a", "b", "c", "d", "e" ]

class ExamineeItem:
	"""
	考生
	"""
	def __init__( self, playerBase, playerDBID, playerName ):
		self.base = playerBase
		self.playerDBID = playerDBID
		self.playerName = playerName
		self.score = 0

	def getScore( self ):
		return self.score

	def addScore( self, value ):
		self.score += value
		self.base.client.quiz_scoreChange( self.score )

	def getName( self ):
		return self.playerName

	def gameOver( self, isEnd ):
		"""
		游戏结束
		"""
		if hasattr( self.base, "cell" ):
			self.base.cell.quiz_gameOver( self.score, isEnd )

class QuizGameMgr( BigWorld.Base ):
	"""
	全民知识问答管理器
	"""
	def __init__( self ):
		"""
		"""
		BigWorld.Base.__init__( self )

		# 由于参加问答的人数可能庞大，需要做很多次比较，基于效率考虑，不把判断答案是否正确封装于KnowledgeLoader
		self.currentQustionStartTime = 0	# 当前题目的出题时间		
		
		self.quizGameInfos = {}				#记录每个玩家的答题信息字典 {playerDBID:{questionList:,....}}包括答题字典等add by wuxo 2012-1-30
		self.questCount    = 0				#记录答题数量		
		
		self.questionList = []					# 本次活动题目列表
		self.examineeDict = {}				# 考生字典：{ databaseID:ExamineeItem, ... }
		self.quitExamineeList = []			# 退出比赛的玩家列表，[ databaseID, ... ]，本次比赛期间玩家不能再次加入
		self.intializeFlag = False				# 是否初始化
		self.quizGameStartTime = 0			# 答题开始时间

		self.onStartNoticeTimerID = 0
		self.onStartTimerID = 0
		self.onEndTimerID = 0
		self.intializeQuestionTimerID = 0

		self.registerGlobally( "QuizGameMgr", self._registerCallback )

	def _registerCallback( self, success ):
		"""
		注册全局实例的回调
		"""
		if success:
			BigWorld.globalData[ "QuizGameMgr" ] = self
			self.registerCrond()
		else:
			self.registerGlobally( "QuizGameMgr", self._registerCallback )

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"QuizGameMgr_notice" : "onStartNotice",
					  	"QuizGameMgr_start" : "onStart",
					  	"QuizGameMgr_end" : "onEnd",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )


	def onStartNotice( self ):
		"""
		Define method.
		活动开始的全服通知
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_DTHD_WILL_OPEN_3, [] )
		self.onStartNoticeTimerID = self.addTimer( NOTICE_INTERVAL1, 0, TIMER_NOTICE_INTERVAL1 )
		INFO_MSG( "QuizGameMgr", "notice", "" )

	def onStart( self ):
		"""
		Define method.
		活动开始
		"""
		if BigWorld.globalData.has_key( "QuizGame_start" ) and BigWorld.globalData[ "QuizGame_start" ] == True:
			curTime = time.localtime()
			ERROR_MSG( "知识问答活动正在进行，%i点%i分试图再次开始知识问答活动。" % ( curTime[3], curTime[4] ) )
			return
		BigWorld.globalData["QuizGame_start"] = True
		Love3.g_baseApp.globalRemoteCallClient( "quiz_start" )
		self.quizGameStartTime = time.time()
		self.questionList = quizGameLoader.getQuestionList()
		self.questCount = len(self.questionList) #题目数量 add by wuxo 2012-1-30
		
		self.onStartTimerID = self.addTimer( READY_INTERVAL, 0, TIMER_READY_FOR_QUESTION )
		pType = csdefine.ACTIVITY_PARENT_TYPE_OTHER
		aType = csdefine.ACTIVITY_ZHI_SHI_WEN_DA
		action = csdefine.ACTIVITY_ACTION_CURRENT_PLAYER_COUNT
		
		t = time.localtime()
		quizUid = str( t[0:4] )
		Love3.g_baseApp.addAllBasePlayerCountLogs( pType, aType, action, quizUid, "", "", "", "" )
		INFO_MSG( "QuizGameMgr", "start", "" )

	def onEnd( self ):
		"""
		Define method.
		活动结束
		"""
		if not BigWorld.globalData.has_key( "QuizGame_start" ):
			curTime = time.localtime()
			ERROR_MSG( "知识问答活动已经结束，%i点%i分试图再次结束活动。" % ( curTime[3], curTime[4] ) )
			return
		for playerItem in self.examineeDict.itervalues():
			playerItem.gameOver( True )
		del BigWorld.globalData["QuizGame_start"]
		self.reset()
		INFO_MSG( "QuizGameMgr", "end", "" )

	def onTimer( self, controllerID, useArg ):
		"""
		"""
		if TIMER_NOTICE_INTERVAL1 == useArg:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_DTHD_WILL_OPEN_1, [] )
			self.onEndTimerID = self.addTimer( NOTICE_INTERVAL2, 0, TIMER_NOTICE_INTERVAL2 )
		elif TIMER_NOTICE_INTERVAL2 == useArg:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_DTHD_WILL_OPEN_2, [] )
		elif TIMER_QUESTION_INTERVAL == useArg:
			# 排名前20名单通知玩家
			playerList = self.examineeDict.values()
			playerList.sort( key = lambda n: n.getScore(), reverse = True )
			topPlayerList = playerList[ 0:20 ]
			nameList = [ playerItem.getName() for playerItem in topPlayerList ]
			scoreList = [ playerItem.getScore() for playerItem in topPlayerList ]
			for order, playerItem in enumerate( playerList ):
				playerItem.base.client.quiz_receiveTopPlayer( nameList, scoreList, order )
			self.intializeQuestion()
		elif TIMER_READY_FOR_QUESTION == useArg:
			self.intializeQuestion()

	def signUp( self, playerBase, playerDBID, playerName ):
		"""
		Define method.
		玩家报名

		@param playerBase : 玩家base mailbox
		@type playerBase : MAILBOX
		@param playerName : 玩家名字
		@type playerName : STRING
		"""
		if playerDBID in self.quitExamineeList:
			return
		#添加到玩家答题信息字典中 add by wuxo 2012-1-30
		if self.questCount == 0:
			playerBase.client.onStatusMessage( csstatus.QUIZ_NO_QUESTION, "" )
			return
		self.quizGameInfos[playerDBID] = {}
		questionList = random.sample(self.questionList, self.questCount)
		self.quizGameInfos[playerDBID]["questionList"] = questionList
		
		self.examineeDict[playerDBID] = ExamineeItem( playerBase, playerDBID, playerName )
		playerBase.cell.quiz_join()
		playerBase.client.quiz_receiveTotalNumber( self.questCount )
		try:
			g_logger.actJoinLog( csdefine.ACTIVITY_ZHI_SHI_WEN_DA, csdefine.ACTIVITY_JOIN_ROLE, playerDBID, playerName )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
			
		INFO_MSG( "QuizGameMgr", "signup", "" )

	def playerQuit( self, playerDBID ):
		"""
		Define method.
		玩家退出考试

		@param playerName : 玩家名字
		@type playerName : STRING
		"""
		if not self.examineeDict.has_key( playerDBID ):
			return
		self.quitExamineeList.append( playerDBID )
		
		isEnd = self.questCount == 0 and True or False # 答完最后一道题
		self.examineeDict[playerDBID].gameOver( isEnd )
		del self.examineeDict[playerDBID]
		
	def playerAnswer( self, playerDBID, questionID, answer, scoreRate ):
		"""
		Define method.
		玩家答题

		@param scoreRate : 得分倍率，如果使用幸运星答对会得双倍积分。
		@type scoreRate : UINT8
		"""
		if questionID != self.quizGameInfos[playerDBID]["currentQuestionID"]:
			return
		
		if answer != self.quizGameInfos[playerDBID]["currentAnswer"]:
			# ....答案不对。
			self.examineeDict[playerDBID].base.client.quiz_answerState( questionID, False )
			try:
				g_logger.actAnswerLog( csdefine.ACTIVITY_ZHI_SHI_WEN_DA, playerDBID, self.examineeDict[ playerDBID ].playerName ,False, self.questCount )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			return
		startTime = BigWorld.time() - self.currentQustionStartTime	# 开始了多长时间
		if startTime < csconst.QUIZ_READING_QUESTION_TIME:
			HACK_MSG( "--->>>it's reading question time.playerDBID( %i )." % playerDBID )
			return
		self.examineeDict[playerDBID].base.client.quiz_answerState( questionID, True )
		try:
			g_logger.actAnswerLog( csdefine.ACTIVITY_ZHI_SHI_WEN_DA, playerDBID, self.examineeDict[ playerDBID ].playerName, True, self.questCount )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		self.examineeDict[playerDBID].addScore( scoreRate * quizGameLoader.getScore( min( csconst.QUIZ_QUESTION_TIME - 1 - startTime, 9.0 ) ) )

	def useYourHead( self, playerDBID, questionID, scoreRate ):
		"""
		Define method.
		玩家使用道具答题，秒杀。

		@param playerDBID : 玩家databaseID
		@type playerDBID : DATABASE_ID
		@param questionID : 题目id
		@type questionID : UINT16
		"""
		playerItem = self.examineeDict[playerDBID]
		if questionID != self.quizGameInfos[playerDBID]["currentQuestionID"]:	# 如果问答时间已过，但是玩家消耗了元宝，那么玩家还是得分了
			playerItem.addScore( quizGameLoader.getScore( 0 ) )
			return
		playerItem.addScore( scoreRate * quizGameLoader.getScore( min( csconst.QUIZ_QUESTION_TIME - 1 - ( BigWorld.time() - self.currentQustionStartTime ), 9.0 ) ) )
		playerItem.base.client.receiveRightAnswer( questionID, self.quizGameInfos[playerDBID]["currentAnswer"] )
		
	def intializeQuestion( self ):
		"""
		初始化活动
		"""
		#增加玩家题目随机和题目答案的选项随机 by wuxo 2012-1-31
		if self.questCount == 0:	# 如果已经出题完毕，则结束活动
			self.onEnd()
			return
		
		self.currentQustionStartTime = BigWorld.time()#modify by wuxo 2012-1-30
		for playerDBID in self.examineeDict.iterkeys():
			playerItem = self.examineeDict[playerDBID]
			questionList = self.quizGameInfos[playerDBID]["questionList"]
			if len(questionList) == 0:
				continue
			currentQuestionID = random.choice(questionList)  #实现随机取题
			questionList.remove(currentQuestionID)
			
			currentAnswer = quizGameLoader.getAnswer( currentQuestionID ) # 当前考题答案
			currentDescription = quizGameLoader.getDescription( currentQuestionID ) # 当前问题的描述
			currentOption = copy.deepcopy( quizGameLoader.getOption( currentQuestionID ) )
			
			answer_str = currentOption[ANSWER_MAP.index(currentAnswer)]
			random.shuffle(currentOption)#实现答案选项的随机
			currentAnswer0 = ANSWER_MAP[currentOption.index(answer_str)]

			self.quizGameInfos[playerDBID]["currentQuestionID"] = currentQuestionID #保存到答题玩家信息字典中
			self.quizGameInfos[playerDBID]["currentDescription"]= currentDescription
			self.quizGameInfos[playerDBID]["currentOption"]     = currentOption
			self.quizGameInfos[playerDBID]["questionList"]      = questionList
			self.quizGameInfos[playerDBID]["currentAnswer"]     = currentAnswer0 #实现答案调整后的映射
			
			playerItem.base.client.quiz_receiveQuestion( currentQuestionID, currentDescription, currentOption )
			
		self.questCount -= 1
		self.intializeQuestionTimerID = self.addTimer( csconst.QUIZ_QUESTION_TIME, 0, TIMER_QUESTION_INTERVAL )

	def reset( self ):
		"""
		活动结束的清理工作
		"""
		
		self.quitExamineeList = []
		self.questionList = []
		self.questCount = 0
		
		self.examineeDict.clear()
		self.quizGameInfos.clear()

		# 清除回调//
		self.delTimer( self.onStartNoticeTimerID )
		self.delTimer( self.onStartTimerID )
		self.delTimer( self.onEndTimerID )
		self.delTimer( self.intializeQuestionTimerID )

	def onRoleGetCell( self, baseMailbox ):
		"""
		角色在活动期间登录
		"""
		baseMailbox.cell.noticeJoinQuiz( self.quitExamineeList, self.quizGameStartTime )
		
