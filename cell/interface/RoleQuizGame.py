# -*- coding: gb18030 -*-

import cschannel_msgs
import ShareTexts as ST
import csdefine
import csconst
import BigWorld
from bwdebug import *
import items
import csstatus
from VehicleHelper import getCurrVehicleID
from Love3 import g_rewards
from VehicleHelper import isFlying

class RoleQuizGame:
	"""
	���֪ʶ�ʴ�
	"""
	def __init__( self ):
		"""
		"""
		pass

	def getQuizGameMgr( self ):
		"""
		���֪ʶ�ʴ������
		"""
		return BigWorld.globalData[ "QuizGameMgr" ]

	def quiz_request( self, srcEntityID ):
		"""
		Exposed method.
		�������֪ʶ�ʴ�
		"""
		if self.id != srcEntityID:
			HACK_MSG( "-->>>self.id != srcEntityID, client id:%i, playerName:%s." % ( srcEntityID, self.getName() ) )
			return

		if self.level < csconst.QUIZ_MIN_LEVEL_LIMIT:
			self.statusMessage( csstatus.QUIZ_JOIN_LEVEL_LACK )
			return
		if not self.isQuizGaming():
			self.statusMessage( csstatus.QUIZ_NOT_START )
			return

		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_NORMAL:
			self.getQuizGameMgr().signUp( self.base, self.databaseID, self.getName() )
		else:
			self.setTemp( "startQuizGame_teleport", True )
			self.gotoSpace( self.reviveSpace, self.revivePosition, self.reviveDirection )

	def quiz_join( self ):
		"""
		Define method.
		��Ҳμ��ʴ𣬳�ʼ��״̬
		"""
		if getCurrVehicleID( self ):
			if isFlying( self ):
				actPet = self.pcg_getActPet()
				if actPet: actPet.entity.withdraw( csdefine.PET_WITHDRAW_GMWATCHER )
				self.effectStateInc( csdefine.EFFECT_STATE_WATCHER )
				self.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
				self.setTemp( "watch_state", True )
			else:
				self.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )
			
		# ������������ļ���
		if self.attrIntonateSkill:
			self.interruptSpell( csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1 )
			
		self.changeState( csdefine.ENTITY_STATE_QUIZ_GAME )
		self.setTemp( "lucky_star", csconst.QUIZ_LUCKY_STAR_COUNT )	# ������ʱ���ݣ������csconst.QUIZ_LUCKY_STAR_COUNT�λ���ϵͳ���������ȷ��
		actPet = self.pcg_getActPet()
		if actPet :
			actPet.entity.changeState( csdefine.ENTITY_STATE_QUIZ_GAME )

	def onEnterSpace_( self ):
		"""
		��ҽ���ռ�
		"""
		startQuizTeleport = self.queryTemp( "startQuizGame_teleport", False )
		if startQuizTeleport:
			self.removeTemp( "startQuizGame_teleport" )
			self.getQuizGameMgr().signUp( self.base, self.databaseID, self.getName() )

	def quiz_answer( self, srcEntityID, questionID, answer, scoreRate ):
		"""
		Exposed method.
		��Ҵ���

		@param questionID : ������Ӧ����Ŀ
		@type questionID : UNT16
		@param answer : ��
		@type answer : STRING
		@param scoreRate : �÷ֱ��ʣ����ʹ�������Ǵ�Ի��˫�����֡�
		@type scoreRate : UINT8
		"""
		if self.id != srcEntityID:
			HACK_MSG( "-->>>self.id != srcEntityID, client id:%i, playerName:%s." % ( srcEntityID, self.getName() ) )
			return

		if not self.isState( csdefine.ENTITY_STATE_QUIZ_GAME ):
			HACK_MSG( "-->>>player( %s ) is not in ENTITY_STATE_QUIZ_GAME state." % self.getName() )
			return

		if not self.isQuizGaming():
			return

		if scoreRate == 2:
			luckyStarCount = self.queryTemp( "lucky_star", 0 )
			if luckyStarCount <= 0:
				HACK_MSG( "-->>>There's no lucky star!" )
				return
			else:
				luckyStarCount -= 1
				self.setTemp( "lucky_star", luckyStarCount )
		elif scoreRate != 1:
			HACK_MSG( "player( %s ) scoreRate( %i ) is wrong." % ( self.getName(), scoreRate ) )
			return

		self.getQuizGameMgr().playerAnswer( self.databaseID, questionID, answer, scoreRate )


	def quiz_useGold( self, srcEntityID, questionID, scoreRate ):
		"""
		Exposed method.
		ʹ��Ԫ������

		@param questionID : ������Ӧ����Ŀ
		@type questionID : UNT16
		@param scoreRate : �÷ֱ��ʣ����ʹ�������Ǵ�Ի��˫�����֡�
		@type scoreRate : UINT8
		"""
		if self.id != srcEntityID:
			HACK_MSG( "-->>>self.id != srcEntityID, client id:%i, playerName:%s." % ( srcEntityID, self.getName() ) )
			return

		if not self.isState( csdefine.ENTITY_STATE_QUIZ_GAME ):
			HACK_MSG( "-->>>player( %s ) is not in ENTITY_STATE_QUIZ_GAME state." % self.getName() )
			return

		if not self.isQuizGaming():
			return

		if scoreRate == 2:
			luckyStarCount = self.queryTemp( "lucky_star", 0 )
			if luckyStarCount <= 0:
				HACK_MSG( "-->>>There's no lucky star!" )
				return
			else:
				luckyStarCount -= 1
				self.setTemp( "lucky_star", luckyStarCount )
		elif scoreRate != 1:
			HACK_MSG( "player( %s ) scoreRate( %i ) is wrong." % ( self.getName(), scoreRate ) )
			return

		self.base.quiz_useGold( questionID, scoreRate )

	def isQuizGaming( self ):
		"""
		��Ƿ�ʼ
		"""
		return BigWorld.globalData.has_key( "QuizGame_start" )
		
	def quiz_gameOver( self, score, isEnd ):
		"""
		Define method.
		���ջ���

		@param score : �������
		@type score : UINT16
		@param isEnd : �Ƿ��Ѿ�������е�֪ʶ�ʴ���Ŀ
		@type isEnd : BOOL
		"""
		self.changeState( csdefine.ENTITY_STATE_FREE )
		if getCurrVehicleID( self ):
			if isFlying( self ) and self.queryTemp( "watch_state", False ):
				self.effectStateDec( csdefine.EFFECT_STATE_WATCHER )
				self.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
				self.setTemp( "watch_state", False )
		self.removeTemp( "lucky_star" )
		if score > 0:
			level = self.level
			exp = score * csconst.ACTIVITY_GET_EXP( csdefine.ACTIVITY_ZHI_SHI_WEN_DA, level )
			potential = 0.3 * level * 1.6 * score
			self.addExp( exp, csdefine.CHANGE_EXP_QUIZ_GAMEOVER )
			self.addPotential( potential )
		actPet = self.pcg_getActPet()
		if actPet :
			actPet.entity.changeState( csdefine.ENTITY_STATE_FREE )
		if isEnd:	# ����Ǽ�ֵ��������
			awarder = g_rewards.fetch( csdefine.RCG_QUIZ_GAME_FESTIVAL, self )
			if self.checkItemsPlaceIntoNK_( awarder.items ) != csdefine.KITBAG_CAN_HOLD:
				self.statusMessage( csstatus.QUIZ_CANT_GET_ITEM_BAG_FULL )
				return
			awarder.award( self, csdefine.CHANGE_EXP_QUIZ_GAMEOVER )
			
	def quiz_quit( self, srcEntityID ):
		"""
		Exposed method.
		����˳��ʴ�
		"""
		if self.id != srcEntityID:
			HACK_MSG( "-->>>self.id != srcEntityID, client id:%i, playerName:%s." % ( srcEntityID, self.getName() ) )
			return
		if not self.isState( csdefine.ENTITY_STATE_QUIZ_GAME ):
			HACK_MSG( "player( %s ) is not in ENTITY_STATE_QUIZ_GAME state." % self.getName() )
			return
		if not self.isQuizGaming():
			HACK_MSG( "quiz game do not start now!" )
			return

		self.getQuizGameMgr().playerQuit( self.databaseID )

	def onDie( self ):
		"""
		�������ʴ��Ӱ��
		"""
		if not self.isState( csdefine.ENTITY_STATE_QUIZ_GAME ):
			return
		self.getQuizGameMgr().playerQuit( self.databaseID )
		
	def noticeJoinQuiz( self, quitExamineeList, quizGameStartTime ):
		if self.databaseID not in quitExamineeList:
			self.client.quiz_enterInviteJoin( quizGameStartTime )