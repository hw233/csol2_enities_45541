# -*- coding: gb18030 -*-
import copy

from NPC import NPC
import BigWorld
import Language
import random
import ECBExtend
import csstatus

from Resource.ImperialExaminationsLoader import g_imperialExaminationsLoader
from Resource.ImperialExaminationsLoader import ANSWERS_OPTIONS

class ImperialExaminationsNPC( NPC ):
	"""
	NPC的基类
	"""
	def __init__( self ):
		"""
		初始化
		"""
		NPC.__init__( self )
		self.currAnswer = None #add by wuxo 2012-1-31

	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		NPC对话控制
		"""
		if dlgKey == "START EXAMINATION":
			questionID = playerEntity.queryTemp( "current_ie_question_id", -1 )
			questionsSec = None
			if questionID == -1:
				questionsSec = g_imperialExaminationsLoader.randomGet()
				questionID = questionsSec[ "questionID" ]
				playerEntity.setTemp( "current_ie_question_id", questionID )
			else:
				questionsSec = g_imperialExaminationsLoader[questionID]
				
			playerEntity.setGossipText( questionsSec["questionDes"] )
			#以下实现科举答题选项的随机 add by wuxo 2012-1-31
			
			questOptions = copy.deepcopy( questionsSec[ "questOptions" ] )
			
			random.shuffle( questOptions )
			
			self.currAnswer = ANSWERS_OPTIONS[ questOptions.index( questionsSec[ "answer" ] ) ] #新的映射答案
			for i in range(len(questOptions)):
				playerEntity.addGossipOption( ANSWERS_OPTIONS[i], ANSWERS_OPTIONS[i] + "." + questOptions[i] )
			
			BigWorld.globalData['ImperialExaminationsMgr'].addPlayerQuestion( playerEntity.playerName, questionID )
		elif dlgKey in ANSWERS_OPTIONS:
			BigWorld.globalData['ImperialExaminationsMgr'].requestPlayerQuestion(  selfEntity, playerEntity.base, playerEntity.playerName, dlgKey  )
			playerEntity.endGossip( selfEntity )
		else:
			return NPC.gossipWith( self, selfEntity, playerEntity, dlgKey )
		
		playerEntity.sendGossipComplete( selfEntity.id )

	def receivePlayerQuestionInfo( self, selfEntity, playerBaseMailbox, questionID, answerID ):
		"""
		define method
		得到玩家回答问题的信息
		"""
		player = BigWorld.entities.get( playerBaseMailbox.id, None )
		
		if player is None:
			return
			
		currAnswer = self.currAnswer #modify by wuxo 2012-1-31
		if currAnswer == answerID:
			#通知任务完成记数，回答正确记数
			player.statusMessage( csstatus.IE_ANSWER_TRUE )
			player.questTaskAddAnswerQuestion( True )
		else:
			#通知任务完成记数
			player.statusMessage( csstatus.IE_ANSWER_FALSE )
			player.questTaskAddAnswerQuestion( False )
		self.currAnswer = None
		if BigWorld.globalData.has_key( "AS_DianshiActivityStart" ):
			examCount = player.queryTemp( "current_dianshi_question", 1 )
			examCount += 1
			if examCount <= 20:
				self.startExamination( selfEntity, player, examCount )
				player.setTemp( "current_dianshi_question", examCount )
	
	def startExamination( self, selfEntity, player, exaCount ):
		"""
		"""
		selfEntity.setTemp( "exaCount", exaCount )
		player.setTemp( "talkID", "START EXAMINATION" )
		player.setTemp( "talkNPCID", selfEntity.id )
		player.addTimer( 0.5, 0, ECBExtend.AUTO_TALK_CBID )