# -*- coding: gb18030 -*-

import time
import csdefine
import csconst
import csstatus
from bwdebug import *
import event.EventCenter as ECenter


class RoleQuizGame:
	"""
	玩家知识问答活动接口
	"""
	def __init__( self ):
		"""
		"""
		self.quiz_score = 0		# 答题积分
		self.currentQuestionID = 0	# 正在回答的问题
		self.quizGameStartTime = 0.0

	def quiz_start( self ):
		"""
		Define method.
		知识问答开始
		"""
		if self.level < csconst.QUIZ_MIN_LEVEL_LIMIT:
			return

		ECenter.fireEvent( "EVT_ON_QUIZ_INVITE_JOIN" )

	def quiz_enterInviteJoin( self, quizGameStartTime ):
		"""
		Define method.
		新上线后，是否参加知识问答
		"""
		#ECenter.fireEvent( "EVT_ON_QUIZ_ON_ENTER_INVITE_JOIN" )
		self.quizGameStartTime = quizGameStartTime
		self.isReceiveEnterInviteJoin = True

	def receiveRightAnswer( self, questionID, questionAnswer ):
		"""
		Define method.
		接收正确答案

		@param questionID : 题目id
		@type questionID : UINT16
		@param questionAnswer : 答案
		@type questionAnswer : STRING
		"""
		ECenter.fireEvent( "EVT_ON_QUIZ_RECEIVE_ANSWER", questionID, questionAnswer )

	def quiz_request( self ):
		"""
		请求参加知识问答
		"""
		if self.quiz_hasJoined():
			return
		if self.hasFlag( csdefine.ROLE_FLAG_XL_DARTING ) or self.hasFlag( csdefine.ROLE_FLAG_CP_DARTING ):
			self.statusMessage( csstatus.QUIZ_DARK_CANNOT_JOIN )
		status = self.quiz_canJoin()
		if status != csstatus.QUIZ_CAN_JOIN:
			self.statusMessage( status )
			return
		self.cell.quiz_request()

	def quiz_answer( self, questionID, answer, scoreRate ):
		"""
		玩家答题

		@param scoreRate : 得分倍率，如果使用幸运星答对会得双倍积分。
		@type scoreRate : UINT8
		"""
		if self.currentQuestionID != questionID:
			return
		self.currentQuestionID = 0
		self.cell.quiz_answer( questionID, answer, scoreRate )

	def quiz_hasJoined( self ):
		"""
		是否已经参加
		"""
		if self.state == csdefine.ENTITY_STATE_QUIZ_GAME:
			return True
		return False

	def quiz_canJoin( self ):
		"""
		是否能参加答题
		"""
		if self.state == csdefine.ENTITY_STATE_FREE or self.state == csdefine.ENTITY_STATE_PENDING:
			return csstatus.QUIZ_CAN_JOIN
		else:
			return csstatus.QUIZ_STATE_CANNOT_JOIN

	def quiz_enterGameState( self ):
		"""
		进入问答状态后，做一些初始化
		"""
		pet = self.pcg_getActPet()
		if pet is not None:
			pet.setActionMode( csdefine.PET_ACTION_MODE_FOLLOW )
		ECenter.fireEvent( "EVT_ON_QUIZ_ENTER_STATE" )

	def quiz_receiveQuestion( self, questionID, commentString, optionalStringList ):
		"""
		Define method.
		接收服务器问答题目

		@param commentString : 问题的内容
		@type commentString : STRING
		@param optionalStringList : 问题的选项
		@type optionalStringList : ARRAY OF STRING
		"""
		self.currentQuestionID = questionID
		ECenter.fireEvent( "EVT_ON_QUIZ_RECEIVE_QUESTIONS", questionID, commentString, optionalStringList )

	def quiz_receiveTopPlayer( self, playerNameList, scoreList, playerOrder ):
		"""
		Define method.
		接收答题排行榜和自身排名

		@param playerNameList : 玩家的名字列表
		@type playerNameList : ARRAY OF STRING
		@param scoreList : 玩家得分列表
		@type scoreList : ARRAY OF UINT16
		@param playerOrder : 玩家本次答题排名
		@type playerOrder : INT32
		"""
		ECenter.fireEvent( "EVT_ON_QUIZ_RECEIVE_TOPS",playerNameList, scoreList, playerOrder )

	def quiz_quit( self ):
		"""
		退出游戏
		"""
		if not self.state == csdefine.ENTITY_STATE_QUIZ_GAME:
			return
		self.cell.quiz_quit()

	def quiz_reset( self ):
		"""
		重置数据
		"""
		self.quiz_score = 0		# 答题积分
		self.currentQuestionID = 0	# 正在回答的问题
		self.quizGameStartTime = 0.0

	def quiz_scoreChange( self, score ):
		"""
		Define method.
		答题分数改变
		"""
		self.quiz_score = score
		ECenter.fireEvent( "EVT_ON_QUIZ_SCORE_CHANGE", score )

	def quiz_answerState( self, qusetID, answerState ):
		"""
		Define method.
		接收回答问题的结果
		"""
		ECenter.fireEvent( "EVT_ON_QUIZ_ANSWER_STATE", qusetID, answerState )

	def quiz_useGold( self, questionID, scoreRate ):
		"""
		使用金元宝答题

		@param scoreRate : 得分倍率，如果使用幸运星答对会得双倍积分。
		@type scoreRate : UINT8
		"""
		if self.state != csdefine.ENTITY_STATE_QUIZ_GAME:
			HACK_MSG( "-->>>player( %s ) is not in ENTITY_STATE_QUIZ_GAME state." % self.getName() )
			return
		if self.currentQuestionID != questionID:
			return
		if self.gold < csconst.QUIZ_GOLD_CONSUME:
			self.statusMessage( csstatus.GOLD_NO_ENOUGH )
			return
		self.currentQuestionID = 0
		self.cell.quiz_useGold( questionID, scoreRate )

	def quiz_receiveTotalNumber( self, totalNumber ):
		"""
		Define method.
		接收题目总数
		"""
		ECenter.fireEvent( "EVT_ON_QUIZ_TOTAL_NUMBER", totalNumber )

