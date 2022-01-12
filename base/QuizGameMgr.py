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


NOTICE_INTERVAL1 = 60*9		# �ڶ���֪ͨ��ʱ����
NOTICE_INTERVAL2 = 30			# ������֪ͨ��ʱ����
READY_INTERVAL = 30		# ����׼��ʱ��

TIMER_NOTICE_INTERVAL1		= 1
TIMER_QUESTION_INTERVAL	= 2
TIMER_READY_FOR_QUESTION	= 3
TIMER_NOTICE_INTERVAL2		= 4

ANSWER_MAP =  [ "a", "b", "c", "d", "e" ]

class ExamineeItem:
	"""
	����
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
		��Ϸ����
		"""
		if hasattr( self.base, "cell" ):
			self.base.cell.quiz_gameOver( self.score, isEnd )

class QuizGameMgr( BigWorld.Base ):
	"""
	ȫ��֪ʶ�ʴ������
	"""
	def __init__( self ):
		"""
		"""
		BigWorld.Base.__init__( self )

		# ���ڲμ��ʴ�����������Ӵ���Ҫ���ܶ�αȽϣ�����Ч�ʿ��ǣ������жϴ��Ƿ���ȷ��װ��KnowledgeLoader
		self.currentQustionStartTime = 0	# ��ǰ��Ŀ�ĳ���ʱ��		
		
		self.quizGameInfos = {}				#��¼ÿ����ҵĴ�����Ϣ�ֵ� {playerDBID:{questionList:,....}}���������ֵ��add by wuxo 2012-1-30
		self.questCount    = 0				#��¼��������		
		
		self.questionList = []					# ���λ��Ŀ�б�
		self.examineeDict = {}				# �����ֵ䣺{ databaseID:ExamineeItem, ... }
		self.quitExamineeList = []			# �˳�����������б�[ databaseID, ... ]�����α����ڼ���Ҳ����ٴμ���
		self.intializeFlag = False				# �Ƿ��ʼ��
		self.quizGameStartTime = 0			# ���⿪ʼʱ��

		self.onStartNoticeTimerID = 0
		self.onStartTimerID = 0
		self.onEndTimerID = 0
		self.intializeQuestionTimerID = 0

		self.registerGlobally( "QuizGameMgr", self._registerCallback )

	def _registerCallback( self, success ):
		"""
		ע��ȫ��ʵ���Ļص�
		"""
		if success:
			BigWorld.globalData[ "QuizGameMgr" ] = self
			self.registerCrond()
		else:
			self.registerGlobally( "QuizGameMgr", self._registerCallback )

	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
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
		���ʼ��ȫ��֪ͨ
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_DTHD_WILL_OPEN_3, [] )
		self.onStartNoticeTimerID = self.addTimer( NOTICE_INTERVAL1, 0, TIMER_NOTICE_INTERVAL1 )
		INFO_MSG( "QuizGameMgr", "notice", "" )

	def onStart( self ):
		"""
		Define method.
		���ʼ
		"""
		if BigWorld.globalData.has_key( "QuizGame_start" ) and BigWorld.globalData[ "QuizGame_start" ] == True:
			curTime = time.localtime()
			ERROR_MSG( "֪ʶ�ʴ����ڽ��У�%i��%i����ͼ�ٴο�ʼ֪ʶ�ʴ���" % ( curTime[3], curTime[4] ) )
			return
		BigWorld.globalData["QuizGame_start"] = True
		Love3.g_baseApp.globalRemoteCallClient( "quiz_start" )
		self.quizGameStartTime = time.time()
		self.questionList = quizGameLoader.getQuestionList()
		self.questCount = len(self.questionList) #��Ŀ���� add by wuxo 2012-1-30
		
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
		�����
		"""
		if not BigWorld.globalData.has_key( "QuizGame_start" ):
			curTime = time.localtime()
			ERROR_MSG( "֪ʶ�ʴ��Ѿ�������%i��%i����ͼ�ٴν������" % ( curTime[3], curTime[4] ) )
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
			# ����ǰ20����֪ͨ���
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
		��ұ���

		@param playerBase : ���base mailbox
		@type playerBase : MAILBOX
		@param playerName : �������
		@type playerName : STRING
		"""
		if playerDBID in self.quitExamineeList:
			return
		#��ӵ���Ҵ�����Ϣ�ֵ��� add by wuxo 2012-1-30
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
		����˳�����

		@param playerName : �������
		@type playerName : STRING
		"""
		if not self.examineeDict.has_key( playerDBID ):
			return
		self.quitExamineeList.append( playerDBID )
		
		isEnd = self.questCount == 0 and True or False # �������һ����
		self.examineeDict[playerDBID].gameOver( isEnd )
		del self.examineeDict[playerDBID]
		
	def playerAnswer( self, playerDBID, questionID, answer, scoreRate ):
		"""
		Define method.
		��Ҵ���

		@param scoreRate : �÷ֱ��ʣ����ʹ�������Ǵ�Ի��˫�����֡�
		@type scoreRate : UINT8
		"""
		if questionID != self.quizGameInfos[playerDBID]["currentQuestionID"]:
			return
		
		if answer != self.quizGameInfos[playerDBID]["currentAnswer"]:
			# ....�𰸲��ԡ�
			self.examineeDict[playerDBID].base.client.quiz_answerState( questionID, False )
			try:
				g_logger.actAnswerLog( csdefine.ACTIVITY_ZHI_SHI_WEN_DA, playerDBID, self.examineeDict[ playerDBID ].playerName ,False, self.questCount )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			return
		startTime = BigWorld.time() - self.currentQustionStartTime	# ��ʼ�˶೤ʱ��
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
		���ʹ�õ��ߴ��⣬��ɱ��

		@param playerDBID : ���databaseID
		@type playerDBID : DATABASE_ID
		@param questionID : ��Ŀid
		@type questionID : UINT16
		"""
		playerItem = self.examineeDict[playerDBID]
		if questionID != self.quizGameInfos[playerDBID]["currentQuestionID"]:	# ����ʴ�ʱ���ѹ����������������Ԫ������ô��һ��ǵ÷���
			playerItem.addScore( quizGameLoader.getScore( 0 ) )
			return
		playerItem.addScore( scoreRate * quizGameLoader.getScore( min( csconst.QUIZ_QUESTION_TIME - 1 - ( BigWorld.time() - self.currentQustionStartTime ), 9.0 ) ) )
		playerItem.base.client.receiveRightAnswer( questionID, self.quizGameInfos[playerDBID]["currentAnswer"] )
		
	def intializeQuestion( self ):
		"""
		��ʼ���
		"""
		#���������Ŀ�������Ŀ�𰸵�ѡ����� by wuxo 2012-1-31
		if self.questCount == 0:	# ����Ѿ�������ϣ�������
			self.onEnd()
			return
		
		self.currentQustionStartTime = BigWorld.time()#modify by wuxo 2012-1-30
		for playerDBID in self.examineeDict.iterkeys():
			playerItem = self.examineeDict[playerDBID]
			questionList = self.quizGameInfos[playerDBID]["questionList"]
			if len(questionList) == 0:
				continue
			currentQuestionID = random.choice(questionList)  #ʵ�����ȡ��
			questionList.remove(currentQuestionID)
			
			currentAnswer = quizGameLoader.getAnswer( currentQuestionID ) # ��ǰ�����
			currentDescription = quizGameLoader.getDescription( currentQuestionID ) # ��ǰ���������
			currentOption = copy.deepcopy( quizGameLoader.getOption( currentQuestionID ) )
			
			answer_str = currentOption[ANSWER_MAP.index(currentAnswer)]
			random.shuffle(currentOption)#ʵ�ִ�ѡ������
			currentAnswer0 = ANSWER_MAP[currentOption.index(answer_str)]

			self.quizGameInfos[playerDBID]["currentQuestionID"] = currentQuestionID #���浽���������Ϣ�ֵ���
			self.quizGameInfos[playerDBID]["currentDescription"]= currentDescription
			self.quizGameInfos[playerDBID]["currentOption"]     = currentOption
			self.quizGameInfos[playerDBID]["questionList"]      = questionList
			self.quizGameInfos[playerDBID]["currentAnswer"]     = currentAnswer0 #ʵ�ִ𰸵������ӳ��
			
			playerItem.base.client.quiz_receiveQuestion( currentQuestionID, currentDescription, currentOption )
			
		self.questCount -= 1
		self.intializeQuestionTimerID = self.addTimer( csconst.QUIZ_QUESTION_TIME, 0, TIMER_QUESTION_INTERVAL )

	def reset( self ):
		"""
		�������������
		"""
		
		self.quitExamineeList = []
		self.questionList = []
		self.questCount = 0
		
		self.examineeDict.clear()
		self.quizGameInfos.clear()

		# ����ص�//
		self.delTimer( self.onStartNoticeTimerID )
		self.delTimer( self.onStartTimerID )
		self.delTimer( self.onEndTimerID )
		self.delTimer( self.intializeQuestionTimerID )

	def onRoleGetCell( self, baseMailbox ):
		"""
		��ɫ�ڻ�ڼ��¼
		"""
		baseMailbox.cell.noticeJoinQuiz( self.quitExamineeList, self.quizGameStartTime )
		
