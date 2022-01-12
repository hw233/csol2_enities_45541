# -*- coding: gb18030 -*-

import time
import csdefine
import csconst
import csstatus
from bwdebug import *
import event.EventCenter as ECenter


class RoleQuizGame:
	"""
	���֪ʶ�ʴ��ӿ�
	"""
	def __init__( self ):
		"""
		"""
		self.quiz_score = 0		# �������
		self.currentQuestionID = 0	# ���ڻش������
		self.quizGameStartTime = 0.0

	def quiz_start( self ):
		"""
		Define method.
		֪ʶ�ʴ�ʼ
		"""
		if self.level < csconst.QUIZ_MIN_LEVEL_LIMIT:
			return

		ECenter.fireEvent( "EVT_ON_QUIZ_INVITE_JOIN" )

	def quiz_enterInviteJoin( self, quizGameStartTime ):
		"""
		Define method.
		�����ߺ��Ƿ�μ�֪ʶ�ʴ�
		"""
		#ECenter.fireEvent( "EVT_ON_QUIZ_ON_ENTER_INVITE_JOIN" )
		self.quizGameStartTime = quizGameStartTime
		self.isReceiveEnterInviteJoin = True

	def receiveRightAnswer( self, questionID, questionAnswer ):
		"""
		Define method.
		������ȷ��

		@param questionID : ��Ŀid
		@type questionID : UINT16
		@param questionAnswer : ��
		@type questionAnswer : STRING
		"""
		ECenter.fireEvent( "EVT_ON_QUIZ_RECEIVE_ANSWER", questionID, questionAnswer )

	def quiz_request( self ):
		"""
		����μ�֪ʶ�ʴ�
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
		��Ҵ���

		@param scoreRate : �÷ֱ��ʣ����ʹ�������Ǵ�Ի��˫�����֡�
		@type scoreRate : UINT8
		"""
		if self.currentQuestionID != questionID:
			return
		self.currentQuestionID = 0
		self.cell.quiz_answer( questionID, answer, scoreRate )

	def quiz_hasJoined( self ):
		"""
		�Ƿ��Ѿ��μ�
		"""
		if self.state == csdefine.ENTITY_STATE_QUIZ_GAME:
			return True
		return False

	def quiz_canJoin( self ):
		"""
		�Ƿ��ܲμӴ���
		"""
		if self.state == csdefine.ENTITY_STATE_FREE or self.state == csdefine.ENTITY_STATE_PENDING:
			return csstatus.QUIZ_CAN_JOIN
		else:
			return csstatus.QUIZ_STATE_CANNOT_JOIN

	def quiz_enterGameState( self ):
		"""
		�����ʴ�״̬����һЩ��ʼ��
		"""
		pet = self.pcg_getActPet()
		if pet is not None:
			pet.setActionMode( csdefine.PET_ACTION_MODE_FOLLOW )
		ECenter.fireEvent( "EVT_ON_QUIZ_ENTER_STATE" )

	def quiz_receiveQuestion( self, questionID, commentString, optionalStringList ):
		"""
		Define method.
		���շ������ʴ���Ŀ

		@param commentString : ���������
		@type commentString : STRING
		@param optionalStringList : �����ѡ��
		@type optionalStringList : ARRAY OF STRING
		"""
		self.currentQuestionID = questionID
		ECenter.fireEvent( "EVT_ON_QUIZ_RECEIVE_QUESTIONS", questionID, commentString, optionalStringList )

	def quiz_receiveTopPlayer( self, playerNameList, scoreList, playerOrder ):
		"""
		Define method.
		���մ������а����������

		@param playerNameList : ��ҵ������б�
		@type playerNameList : ARRAY OF STRING
		@param scoreList : ��ҵ÷��б�
		@type scoreList : ARRAY OF UINT16
		@param playerOrder : ��ұ��δ�������
		@type playerOrder : INT32
		"""
		ECenter.fireEvent( "EVT_ON_QUIZ_RECEIVE_TOPS",playerNameList, scoreList, playerOrder )

	def quiz_quit( self ):
		"""
		�˳���Ϸ
		"""
		if not self.state == csdefine.ENTITY_STATE_QUIZ_GAME:
			return
		self.cell.quiz_quit()

	def quiz_reset( self ):
		"""
		��������
		"""
		self.quiz_score = 0		# �������
		self.currentQuestionID = 0	# ���ڻش������
		self.quizGameStartTime = 0.0

	def quiz_scoreChange( self, score ):
		"""
		Define method.
		��������ı�
		"""
		self.quiz_score = score
		ECenter.fireEvent( "EVT_ON_QUIZ_SCORE_CHANGE", score )

	def quiz_answerState( self, qusetID, answerState ):
		"""
		Define method.
		���ջش�����Ľ��
		"""
		ECenter.fireEvent( "EVT_ON_QUIZ_ANSWER_STATE", qusetID, answerState )

	def quiz_useGold( self, questionID, scoreRate ):
		"""
		ʹ�ý�Ԫ������

		@param scoreRate : �÷ֱ��ʣ����ʹ�������Ǵ�Ի��˫�����֡�
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
		������Ŀ����
		"""
		ECenter.fireEvent( "EVT_ON_QUIZ_TOTAL_NUMBER", totalNumber )

