# -*- coding: gb18030 -*-
#
# $Id: Exp $


"""
"""

from bwdebug import *
import cschannel_msgs
import ShareTexts as ST
from QuestFixedLoop import QuestFixedLoop
import csdefine
import ECBExtend
import Const
import time
import csstatus
import BigWorld


class QuestImperialExamination( QuestFixedLoop ):
	"""
	ÿ��ֻ�����ָ������������
	"""
	def __init__( self ):
		QuestFixedLoop.__init__( self )
		self._type =  csdefine.QUEST_TYPE_IMPERIAL_EXAMINATION


	def accept( self, player ):
		"""
		virtual method.
		���������������ʧ�����򷵻�False��������ұ������˷Ų���������ߣ���

		@param     player: instance of Role Entity
		@type      player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		QuestFixedLoop.accept( self, player )


	def beforeAccept( self, player ):
		"""
		virtual method.
		ִ�н�������ж�
		"""
		bukaoMoney = 0
		pLog = player.getLoopQuestLog( self.getID(), True )
		if not pLog.checkStartTime():
			# �����������뵱ǰʱ�䲻��ͬһ�죬Ҳ�ͱ�ʾ��Ҫ��������״̬
			pLog.reset()
		ieTime = pLog.getDegree()					# �ƾٿ��ԵĴ���
		if ieTime > 0:
			bukaoMoney = int( player.level ** 2 * 10 )	# ������Ǯ
			if player.money < bukaoMoney:
				# ������ǵ�һ���ˣ�˵���ǲ�����Ҫ��Ǯ
				return None

		return QuestFixedLoop.beforeAccept( self, player )


	def onAccept( self, player, tasks ):
		"""
		virtual method.
		ִ������ʵ�ʴ���
		"""
		questsLen = len( player.questsTable )

		if questsLen  < Const.QUEST_MAX_ASSIGNMENT:
			player.addTimer( 0.5, 0, ECBExtend.AUTO_TALK_CBID )
		for t in self.tasks_.itervalues():
			if t.getType() == csdefine.QUEST_OBJECTIVE_TIME:
				break
		player.setTemp( "imperial_exam_start_time", int( time.time() ) )
		pLog = player.getLoopQuestLog( self.getID(), True )
		ieTime = pLog.getDegree()					# �ƾٿ��ԵĴ���
		if ieTime > 0:
			bukaoMoney = int( player.level ** 2 * 10 )	# ������Ǯ
			# ������ǵ�һ���ˣ�˵���ǲ�����Ҫ��Ǯ
			player.payMoney( bukaoMoney, csdefine.CHANGE_MONEY_BUKAO )

		return QuestFixedLoop.onAccept( self, player, tasks )


	def gossipIncomplete( self, playerEntity, issuer ):
		"""
		����Ŀ��δ��ɶ԰ף�
		"""
		if issuer:	targetID = issuer.id
		else:		targetID = 0
		lpLog = playerEntity.getLoopQuestLog( self.getID(), False )
		if lpLog is None or not lpLog.checkStartTime():
			playerEntity.sendQuestIncomplete(  self._id, self._title, self.getLevel( playerEntity ), cschannel_msgs.KE_JU_VOICE_17, targetID )
		else:
			playerEntity.sendQuestIncomplete(  self._id, self._title, self.getLevel( playerEntity ), self._msg_incomplete, targetID )

	def abandoned( self, player, flags ):
		"""
		virtual method.
		@param player: instance of Role Entity
		@type  player: Entity
		@return: None
		"""
		pLog = player.getLoopQuestLog( self.getID(), True )
		ieTime = pLog.getDegree()					# �ƾٿ��ԵĴ���
		if ieTime <= 1:
			player.addFailedGroupQuest( self._id )
		player.cancel( player.queryTemp( "ie_huishi_timerID", 0 ) )
		return QuestFixedLoop.abandoned( self, player, flags )

	def complete( self, player, rewardIndex, codeStr = "" ):
		"""
		virtual method.
		������

		@param player: instance of Role Entity
		@type  player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		completed = QuestFixedLoop.complete( self, player, rewardIndex, codeStr )
		totalNum = player.queryTemp( "imperial_exam_total_num", 0 )
		rightNum = player.queryTemp( "imperial_exam_right_num", 0 )
		if totalNum != 0:
			startTime = player.queryTemp( "imperial_exam_start_time", 0 )
			finishTime = time.time()
			examTime = finishTime - startTime
			examTimeStr = cschannel_msgs.KE_JU_VOICE_18 % ( int( examTime / 60 ), int( examTime % 60 ) )
			correctRate = rightNum * 1.0 / totalNum
			correctRateStr = str( int( rightNum * 100 / totalNum ) ) + "%"
			player.statusMessage( csstatus.IE_OVER_RESULT_MSG, correctRateStr, examTimeStr )
			if BigWorld.globalData.has_key( "AS_HuishiActivityStart" ):
				player.statusMessage( csstatus.IE_OVER_STAT_MSG )
			BigWorld.globalData["ImperialExaminationsMgr"].submitResults( player.databaseID, correctRate, examTime, player.playerName )

		player.removeTemp( "imperial_exam_start_time" )
		player.removeTemp( "imperial_exam_total_num" )
		player.removeTemp( "imperial_exam_right_num" )
		player.removeTemp( "imperial_exam_finish_num" )
		player.removeTemp( "imperial_exam_start_time" )
		player.removeTemp( "current_dianshi_question" )
		dataQuestID = str(time.localtime()[2])+':' + str( self.getID() )
		if dataQuestID in player.failedGroupQuestList:
			player.failedGroupQuestList.remove( dataQuestID )
		return completed

	def checkRequirement( self, player ):
		"""
		virtual method.
		�ж���ҵ������Ƿ��㹻�ӵ�ǰ����
		@return: ����ﲻ���������Ҫ���򷵻�False��
		@rtype:  BOOL
		"""
		lpLog = player.getLoopQuestLog( self.getID(), False )
		if lpLog is not None and lpLog.getDegree() >= self._finish_count:
			# ���������������࣬�������ٽ�
			return False
		for requirement in self.requirements_:
			if not requirement.query( player ):
				return False
		return True