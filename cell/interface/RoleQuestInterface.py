# -*- coding: gb18030 -*-
#
# $Id: RoleQuestInterface.py,v 1.93 2008-09-05 01:40:40 zhangyuxing Exp $

"""
����ϵͳ for Role ����
"""
import sys
import cPickle
import copy
import time
import BigWorld
import random

from config.server.RoleSecondExp import Datas as SecondExpDatas

import csdefine
import csconst
import csstatus
from bwdebug import *
from MsgLogger import g_logger

import Const
import ECBExtend
import Love3
from Resource.QuestModule import QTTask
from LoopQuestTypeImpl import LoopQuestTypeImpl
from RewardQuestTypeImpl import RewardQuestTypeImpl
from Resource.QuestLoader import QuestsFlyweight
from QuestDataType import QuestDataType
from QuestRandomRecordType import QuestRandomRecordType
import cschannel_msgs
from Resource.RewardQuestLoader import RewardQuestLoader		# ������������
g_rewardQuestLoader = RewardQuestLoader.instance()

DISTANCE_FOR_PLAYER_TAKE_SLAVE	= 20						#�ڶ������ڣ����Я���ڳ�һ���������

class RoleRandomQuestInterface:
	"""
	�������ӿ�
	"""
	def __init__( self ):
		pass


	def addSubQuestCount( self, questID, count):
		"""
		�����������д���
		@type	questID: QUESTID
		@param  count:	�������������
		@type	count:	INT
		"""
		self.questsRandomLog.addCount( questID, count )

	def setSubQuestCount( self, questID, count):
		"""
		�����������д���
		@type	questID: QUESTID
		@param  count:	�������������
		@type	count:	INT
		"""
		if self.questsRandomLog.has_randomQuestGroup( questID ):
			self.questsRandomLog._questsRandomLog[questID].count = count

	def getSubQuestCount( self, questID ):
		"""
		��õ������������
		@type	questID: QUESTID
		@rtype : INT
		"""
		return self.questsRandomLog.getCount( questID )

	def setSubQTCountRewardRate( self, questID, count, rate ):
		"""
		���û��������������
		"""
		self.questsRandomLog.setSubQTCountRewardRate( questID, count, rate )

	def getSubQTCountRewardRate( self, questID, count ):
		"""
		��ȡ���������������
		"""
		return self.questsRandomLog.getSubQTCountRewardRate( questID, count )

	def resetSubQTCountRewardRate( self, questID ):
		"""
		���û��������������
		"""
		self.questsRandomLog.resetSubQTCountRewardRate( questID )

	def payQuestDeposit( self, questID, deposit ):
		"""
		֧���������Ѻ��
		@type	questID: QUESTID
		@param 	deposit: Ѻ������ֵ
		@type	deposint:int
		"""
		if deposit == 0:return
		self.payMoney( deposit, csdefine.CHANGE_MONEY_PAYQUESTDEPOSIT )
		self.questsRandomLog.addDeposit( questID, deposit )

	def returnDeposit( self, questID ):
		"""
		����һ���������Ѻ��
		@type questID: QUESTID
		@rtype : INT
		"""
		deposit = self.questsRandomLog.returnDeposit( questID )
		return self.gainMoney( deposit, csdefine.CHANGE_MONEY_RETURNDEPOSIT )
		#self.statusMessage( csstatus.ROLE_QUEST_DEPOSIT_RETURN )

	def addGroupPoint( self, questID, point ):
		"""
		����ѭ������
		@type questID: QUESTID
		@param point: ��������ֵ
		@type  point: INT
		"""
		#--------- ����Ϊ������ϵͳ���ж� --------#
		gameYield = self.wallow_getLucreRate()
		if point >=0:
			point = point * gameYield
		#--------- ����Ϊ������ϵͳ���ж� --------#
		self.questsRandomLog.addPoint( questID, point )

	def takeGroupPoint( self, questID):
		"""
		ȡ��һ���������Ļ���
		@type questID: QUESTID
		@rtype : INT
		"""
		return self.questsRandomLog.takePoint( questID )

	def addRandomLogs( self, questID, record ):
		"""
		����һ����������¼
		@type questID: QUESTID
		"""
		self.questsRandomLog[questID] = record


	def checkStartGroupTime( self, questID ):
		"""
		�ж��������ʼʱ���ǲ��ǽ���
		@type questID: QUESTID
		"""
		return self.questsRandomLog.checkStartGroupTime( questID )

	def resetGroupQuest( self, questID ):
		"""
		�������������
		@type questID: QUESTID
		"""
		self.questsRandomLog.resetGroupQuest( questID )

	def addGroupQuestCount( self, questID ):
		"""
		������������
		@type questID: QUESTID
		"""
		self.questsRandomLog.addGroupQuestCount( questID )

	def setGroupQuestCount( self, questID, num):
		"""
		������������ for GM
		@type questID: QUESTID
		@type num: INT
		"""
		if self.questsRandomLog.has_randomQuestGroup( questID ):
			self.questsRandomLog._questsRandomLog[questID].degree = num

	def resetSingleGroupQuest( self, questID ):
		"""
		���������������
		@type questID: QUESTID
		"""
		self.questsRandomLog.resetSingleGroupQuest( questID )

	def getGroupQuestCount( self, questID ):
		"""
		�����������ɴ���
		@type questID: QUESTID
		@rtype : INT
		"""
		return self.questsRandomLog.getGroupQuestCount( questID )

	def setGroupCurID( self, questID, subQuestID ):
		"""
		�������������������ID
		@type questID: QUESTID
		@type subQuestID: QUESTID
		"""
		self.questsRandomLog.setGroupCurID( questID, subQuestID )

	def queryGroupCurID( self, questID ):
		"""
		��ѯ��ǰ���������������ID
		@type questID: INT
		@rtype : QUESTID
		"""
		return self.questsRandomLog.queryGroupCurID( questID )

	def isGroupQuestRecorded( self, questID ):
		"""
		�Ƿ��Ǽ�¼����������
		"""
		return self.questsRandomLog.isGroupQuestRecorded( questID )

	def setGroupQuestRecorded( self, questID, isRecorded ):
		"""
		���ü�¼����������
		"""
		self.questsRandomLog.setGroupQuestRecorded( questID, isRecorded )

	def recordRandomQuest( self, questID):
		"""
		��¼����������Ϣ
		"""
		#����ҽ�ɫ�������ߵ���

		if not self.has_randomQuestGroup( questID ):
			self.statusMessage( csstatus.ROLE_QUEST_RANDON_NOT_HAVE )
			return
		self.recordQuestsRandomLog.add( questID, self.questsRandomLog[questID].copy() )
		#self.recordQuestsRandomLog.setGroupQuestRecorded( questID, True )
		self.statusMessage( csstatus.ROLE_QUEST_RANDON_RECORD_SUCCESSED )

	def readRandomQuestRecord( self, srcEntityID, questID ):
		"""
		Exposed method.
		��ȡ����������Ϣ
		"""
		if self.id != srcEntityID:
			srcEntity = BigWorld.entities[srcEntityID]
			WARNING_MSG( "%s(%i): other entity caller my method, entityID = %i, caller name = %s" % ( self.playerName, self.id, srcEntityID, srcEntity.playerName ) )
			return
		if not self.recordQuestsRandomLog.has_randomQuestGroup( questID ):
			return
		questID = self.recordQuestsRandomLog[questID].questGroupID
		subQuestID = self.recordQuestsRandomLog[questID].curID
		self.addRandomLogs( questID, self.recordQuestsRandomLog[questID].copy() )
		self.setGroupQuestRecorded( questID, True )
		self.statusMessage( csstatus.ROLE_QUEST_RANDON_TAKE_SUCCESSED )
		self.delRandomQuestRecord( questID )
		self.loadGroupQuest( questID, subQuestID )

		# ��ȡ��������ɾ��failedGroupQuestList�м�¼(�洢����ʱ�򣬰���������Ϊʧ��)
		dataQuestID = str(time.localtime()[2])+':'+str(questID)
		if dataQuestID in self.failedGroupQuestList:
			self.failedGroupQuestList.remove( dataQuestID )

	def loadGroupQuest( self, questID, subQuestID ):
		"""
		����������ID��������ID������һ����֪����
		"""
		if self.getQuest( questID ) is None:
			return
		self.getQuest( questID ).loadQuest( self, subQuestID )


	def delRandomQuestRecord( self, questID ):
		"""
		ɾ��һ����������¼
		"""
		self.recordQuestsRandomLog.delete( questID )


	def addFailedGroupQuest( self, questID ):
		"""
		����һ��������ʧ�ܼ�¼
		"""
		dataQuestID = str(time.localtime()[2])+':'+str(questID)
		if not (dataQuestID in self.failedGroupQuestList ):
			self.failedGroupQuestList.append( dataQuestID )


	def addSaveQuestRecord( self, questID ):
		"""
		����һ���洢���������¼
		ע�ͣ�
			�洢����������Ҹ���ָ������¼�����굱ǰ�����ǣ�������������Ļ���
		"""
		dataQuestID = str(time.localtime()[2])+':'+str(questID)
		if not (dataQuestID in self.savedGroupQuestList ):
			self.savedGroupQuestList.append( dataQuestID )


	def newDataGroupQuest( self, questID ):
		"""
		��һ��Ļ�����
		ע�ͣ�
			�洢���Ļ�������֮���ĳ������󣬻�����������Ļ�����
		"""
		for i in self.savedGroupQuestList:
			if i.split(':')[1] == str( questID ):
				self.resetGroupQuest( questID )
				self.savedGroupQuestList.remove( questID )
			return True
		return False


	def groupQuestSavedAndFailedProcess( self, questID ):
		"""
		������浵�����ʧ�ܹ���
		ע�ͣ�
			�浵��������洢����������������浵����Ĵ���
		"""
		if not self.recordQuestsRandomLog.has_randomQuestGroup( questID ):
			"""
			������û��ʹ�õ��߼�¼������浵����ִ�������Ļ������������
			"""
			outDateList = []
			tempQuestID = 0
			for i in self.failedGroupQuestList:
				if i.split(':')[0] != str(time.localtime()[2]):
					outDateList.append(i)

			for i in outDateList:
				self.failedGroupQuestList.remove( i )
				self.resetSingleGroupQuest( int(i.split(':')[1]) )

			for i in self.failedGroupQuestList:
				if str(questID) == i.split(':')[1]:
					if not self.groupQuestReAccept( questID ):
						return False
					tempQuestID = i
			if tempQuestID != 0:
				self.failedGroupQuestList.remove( tempQuestID )

		outDateSaveList = []
		for i in self.savedGroupQuestList:
			if i.split(':')[0] != str(time.localtime()[2]):
				outDateSaveList.append(i)

		for i in outDateSaveList:
			self.savedGroupQuestList.remove( i )

		return True


	def getRandomLogsTaskType( self, questID ):
		"""
		"""
		return self.questsRandomLog[questID].getTaskType()


	def setRandomLogsTaskType( self, questID,taskType ):
		"""
		"""
		self.questsRandomLog[questID].setTaskType( taskType )


class RoleDartQuestInterface:
	"""
	��������ӿ�
	"""
	def __init__( self ):
		"""
		"""
		self.addDartActivity()
		#self.resetDartPrestige()
		self.queryAboutDart()

	def isDarting( self ):
		"""
		����Ƿ���������������
		"""
		return self.hasFlag( csdefine.ROLE_FLAG_XL_DARTING ) or self.hasFlag( csdefine.ROLE_FLAG_CP_DARTING )

	def isRobbing( self ):
		"""
		����Ƿ��н�����������
		"""
		return self.hasFlag( csdefine.ROLE_FLAG_XL_ROBBING ) or self.hasFlag( csdefine.ROLE_FLAG_CP_ROBBING )

	def isRobbingOppose( self, prestige ):
		"""
		����Ƿ��ж����ھֽ�����������
		"""
		if prestige == csconst.FACTION_CP:
			return self.hasFlag( csdefine.ROLE_FLAG_XL_ROBBING )
		else:
			return self.hasFlag( csdefine.ROLE_FLAG_CP_ROBBING )


	def hasQuestMerchant( self ):
		"""
		����Ƿ���������������
		"""
		return self.hasFlag( csdefine.ROLE_FLAG_MERCHANT )



	def isRobbingComplete( self ):
		"""
		���������Ƿ����
		������������ͬ��������һ�������ݲ߻���Ҫ��ֻҪ�ڹ涨ʱ���ھ�ɱ���ڳ��������
		��ɱ�ڳ���ʱ�涨ʱ���ڲ�������Ҳ����ʧ��
		"""
		for qID in self.questsTable._quests:
			if self.getQuest( qID ).getType() == csdefine.QUEST_TYPE_ROB:
				return self.getQuest( qID ).isCompleted(  self )
		return False

	def isDartingComplete( self ):
		"""
		���������Ƿ����
		������������ͬ��������һ�������ݲ߻���Ҫ��ֻҪ�ڹ涨ʱ�������ھ������
		���ں�ʱ�涨ʱ���ڲ�������Ҳ����ʧ��
		"""
		for qID in self.questsTable._quests:
			if self.getQuest( qID ).getType() == csdefine.QUEST_TYPE_DART or self.getQuest( qID ).getType() == csdefine.QUEST_TYPE_MEMBER_DART:
				return self.getQuest( qID ).isCompleted(  self )
		return False

	def onDartActivityStart( self, controllerID, userData ):
		"""
		��ʼ���ڻ
		"""
		self.statusMessage( csstatus.ROLE_QUEST_DART_ACTIVITY_START )
		self.setTemp('dart_activety', True )

	def onDartActivityEnd( self, controllerID, userData ):
		"""
		�������ڻ
		"""
		self.statusMessage( csstatus.ROLE_QUEST_DART_ACTIVITY_END)
		self.setTemp('dart_activety', False )

	def addDartActivity( self ):
		"""
		"""
		startTime = self.weekTimeMinus( 6, 21 )
		endTime = self.weekTimeMinus( 6, 23 )

		if startTime < 0 and startTime > -7100:
			self.setTemp('dart_activety', True )

		else:
			self.addTimer( startTime, 0, ECBExtend.QUEST_DART_ACTIVITY_START_CBID )			#���˻��ʼ

		if endTime > 0:
			self.addTimer( endTime, 0, ECBExtend.QUEST_DART_ACTIVITY_END_CBID )				#���˻����


	def weekTimeMinus( self, w, h, m = 0):
		"""
		���ص��ﵱǰ�ܵ�ĳһ���ĳ��ʱ�仹��Ҫ������
		0 ����һ
		���磺 ��������9��
		weekTimeMinus�� 6, 21 )
		"""
		date = time.localtime()
		return (w-date[6])*24*3600+(h-date[3])*3600+(m-date[4])*60   #gmtime ��������8Сʱ



	def resetDartPrestige( self ):
		"""
		"""
		BigWorld.globalData['DartManager'].requestPlayerDartPrestige( self.getName(), self.base )

	def updateDartPrestige( self, xValue, cValue ):
		"""
		define method

		@param xValue	:��¡�ھ�����ֵ
		@param cValue	:��ƽ�ھ�����ֵ
		"""
		self.setPrestige( csconst.FACTION_XL, xValue )			#��¡�ھ�����
		self.setPrestige( csconst.FACTION_CP, cValue )			#��ƽ�ھ�����

	def handleDartFailed( self ):
		"""
		define method
		������������ʧ�ܱ���
		"""
		resultList = self.questsTable.handleDartFailed( self )

		for r in resultList:
			self.onTaskStateChange( r[0], self.questsTable[r[0]]._tasks[r[1]], r[1] )
			self.client.onTaskStateUpdate( r[0], self.questsTable[r[0]]._tasks[r[1]] )


	def queryAboutDart( self ):
		"""
		����ȡ���ڳ���Ϣ
		"""
		if not hasattr( self, "base" ):
			WARNING_MSG("Role entity not has base!!")
			return
		BigWorld.globalData['DartManager'].queryAboutDart( self.getName(), self.base )


	def handleDartMsg( self, msg ):
		"""
		"""
		self.statusMessage( msg )

	def isDartRelation( self, killer ):
		"""
		�ж�ɱ���ߺͱ�ɱ���Ƿ�������ں����ڹ�ϵ
		"""
		
		# ɱ��������������
		if killer.isDarting():
			return True
		
		# ɱ�����н�������
		if killer.isRobbing():
			if killer.hasFlag( csdefine.ROLE_FLAG_XL_ROBBING ):
				if self.hasFlag( csdefine.ROLE_FLAG_CP_DARTING ) and killer.level - self.queryTemp( "Dart_level" , self.level ) < csconst.DART_ROB_MIN_LEVEL:		# ɱ������
					return True
				elif len(self.queryTemp("attackDartRoleID",[])) != 0 and killer.id in self.queryTemp("attackDartRoleID"):		# ɱ�����߰��İ���
					return True
					
			if killer.hasFlag( csdefine.ROLE_FLAG_CP_ROBBING ):
				if self.hasFlag( csdefine.ROLE_FLAG_XL_DARTING ) and killer.level - self.queryTemp( "Dart_level" , self.level ) < csconst.DART_ROB_MIN_LEVEL:
					return True
				elif len(self.queryTemp("attackDartRoleID",[])) != 0 and killer.id in self.queryTemp("attackDartRoleID"):
					return True
		
		# ɱ����û�н�������
		else:
			if self.isDarting():	# ��Ұ�ڵ����
				if killer.level - self.level < csconst.DART_ROB_MIN_LEVEL:
					return True
			if self.isRobbing():
				if len(killer.findBuffsByBuffID( 99029 )) != 0:			# ����Աɱ������
					if ( self.hasFlag( csdefine.ROLE_FLAG_CP_ROBBING ) and killer.queryTemp( "TongDart_factionID",0 ) == csdefine.FACTION_XINGLONG )\
						or ( self.hasFlag( csdefine.ROLE_FLAG_XL_ROBBING ) and killer.queryTemp( "TongDart_factionID",0 ) == csdefine.FACTION_CHANGPING ):
							if self.level - killer.queryTemp( "TongDart_level",0 ) < csconst.DART_ROB_MIN_LEVEL:
								return True
			else:
				if len(self.queryTemp("attackDartRoleID",[])) != 0 and killer.id in self.queryTemp("attackDartRoleID"):		# ����Ա������ɱ��
					DEBUG_MSG( "Tong member %s(%i) is killed by player %s(%i)" %( self.getName, self.id, killer.getName(), killer.id ) )
					return True
				if len(killer.queryTemp("attackDartRoleID",[])) != 0 and self.id in killer.queryTemp("attackDartRoleID"):		# ���˱�����Աɱ��
					DEBUG_MSG( "Player %s(%i) is killed by tong member %s(%i)" %( self.getName, self.id, killer.getName(), killer.id ) )
					return True
		
		return False

	def requestTakeToMaster( self, baseMailBox ):
		"""
		define method
		���󵽴���������λ��
		"""
		baseMailBox.cell.onReceiveMasterInfo( self, self.position )

	def dart_spaceDartCountResult( self, count ):
		"""
		Define method.
		��ǰ��ͼ�����ڳ������Ľ���ص�

		@param count : �ڳ�����
		@type count : INT16
		"""
		self.setGossipText( self.popTemp( "DartSpaceInfoQuery_talkString", "%s" ) % count )
		self.sendGossipComplete( self.popTemp( "DartSpaceInfoQuery_talkNPCID", self.id ) )

class RoleActivityInterface:
	"""
	��ӿ�
	"""
	def __init__( self ):
		"""
		"""
		pass

	def moneyToYinpiao( self, money ):
		"""
		"""
		if self.getAllYinpiaoValue() < 0:			# С�����ʾ����û����Ʊ
			self.statusMessage( csstatus.ROLE_YIN_PIAO_NOT_FOUND )
			return
		if self.money < money:
			self.statusMessage( csstatus.ROLE_QUEST_NOT_ENOUGH_MONEY_FOR_CHAGRE_YINPIAO )
			return
		yinpiaoMoney = money * 80 / 100  #��ֵ������Ϊ1��0.8 by����
		self.gainYinpiao( yinpiaoMoney )
		self.payMoney( money, csdefine.CHANGE_MONEY_MONEYTOYINPIAO )

	def getCurrentExaID( self ):
		"""
		"""
		for questID in self.questsTable.keys():
			if self.getQuest( questID ).getType() == csdefine.QUEST_TYPE_IMPERIAL_EXAMINATION:
				for task in self.questsTable[questID]._tasks.itervalues():
					if task.getType() == csdefine.QUEST_OBJECTIVE_IMPERIAL_EXAMINATION:
						return task.val1


		return -1

	def isInMerchantQuest( self ):
		"""
		��û����������
		"""
		for i in self.questsTable._quests:
			if self.getQuest( i ).getType() == csdefine.QUEST_TYPE_RUN_MERCHANT:
				return True
		return False

	def getMerchantQuest( self ):
		"""
		��ȡ��������
		"""
		for id in self.questsTable._quests:
			if self.getQuest( id ).getType() == csdefine.QUEST_TYPE_RUN_MERCHANT:
				return self.getQuest( id )
		return None

	def addIETitle( self, titleID ):
		"""
		define method
		"""
		self.addTitle( titleID )


	def onAddIEExpReward( self, exp ):
		"""
		define method
		�õ��ƾٻش���Ŀ�ľ��齱��
		"""
		self.addExp( exp, csdefine.CHANGE_EXP_KEJUREWARD )

	def addWuDaoAward( self, round, step, isWinner ):
		"""
		���������ά�����߻��ƶ�����CSOL-2656
		"""
		rank = pow( 2, 5 - round )

		if isWinner:
			self.addExp( int( 5 * self.level * pow( 40 - rank, 2.3 ) ), csdefine.CHANGE_EXP_WUDAOAWARD )
			money = int( 0.5 * self.level * pow( 38 - rank, 2.3 ) )
			self.gainMoney( money, csdefine.CHANGE_MONEY_WUDAOAWARD )

			if round == 5: # �����ֻ�ʤ��Ϊ��һ��
				self.sysBroadcast( cschannel_msgs.CELL_ROLEQUESTINTERFACE_1 %( self.getName(), step*10, step*10+9 ) )
				self.addTitle( 36 )
				awarder = Love3.g_rewards.fetch( csdefine.RCG_WD_FORE_LEVEL, self )
				awarder.award( self, csdefine.ADD_ITEM_ADDWUDAOAWARD )

		else:
			self.addExp( int( 2.5 * self.level * pow( 40 - rank, 2.3 ) ), csdefine.CHANGE_EXP_WUDAOAWARD )
			money = int( 0.25 * self.level * pow( 38 - rank, 2.3 ) )
			self.gainMoney( money,csdefine.CHANGE_MONEY_WUDAOAWARD )

			if round == 5: # ������ʧ����Ϊ�ڶ���
				self.addTitle( 37 )
				awarder = Love3.g_rewards.fetch( csdefine.RCG_WD_THREE_LEVEL , self )
				awarder.award( self, csdefine.ADD_ITEM_ADDWUDAOAWARD )

	def showMerchantQuestFlag( self ):
		"""
		���ͷ����ʾ���̱��
		"""
		if not self.hasFlag( csdefine.ROLE_FLAG_MERCHANT ) :
			self.addFlag( csdefine.ROLE_FLAG_MERCHANT )

	def removeMerchantQuestFlag( self ):
		"""
		���ͷ����ʾ���̱��
		"""
		if self.hasFlag( csdefine.ROLE_FLAG_MERCHANT ) :
			self.removeFlag( csdefine.ROLE_FLAG_MERCHANT )

	def showBloodItemFlag( self ):
		"""
		���ͷ����ʾ��Ѫ��ұ��
		"""
		if not self.hasFlag( csdefine.ROLE_FLAG_BLOODY_ITEM ) :
			self.addFlag( csdefine.ROLE_FLAG_BLOODY_ITEM )

	def removeBloodItemFlag( self ):
		"""
		���ͷ����ʾ��Ѫ��ұ��
		"""
		if self.hasFlag( csdefine.ROLE_FLAG_BLOODY_ITEM ) :
			self.removeFlag( csdefine.ROLE_FLAG_BLOODY_ITEM )


	def checkTeamInCopySpace( self, mailbox ):
		"""
		�����븱����ʱ���Ƿ��ж���
		"""
		if not self.isInTeam():
			self.statusMessage( csstatus.TEAM_NOT_IN_LEAVE_COPY )
			self.leaveTeamTimer = self.addTimer( 120, 0, ECBExtend.LEAVE_TEAM_TIMER )


class TasksNotify:
	"""
	����֪ͨ�ӿ�
	"""
	def __init__( self ):
		"""
		"""
		pass

	def updataQuestState( self, resultList ):
		"""
		��������������Ϣ
		"""
		if resultList != []:
			for r in resultList:
				task = self.questsTable[r[0]]._tasks[r[1]]
				self.onTaskStateChange( r[0], task, r[1] )
				self.client.onTaskStateUpdate( r[0], task )
				self.onQuestBoxStateUpdate()

	def questItemAmountChanged( self, item, quantity ):
		"""
		��֪ͨ��ұ�������Ʒ���ı�

		@param   item: ��Ʒʵ��
		@type    item: instance
		@param quantity: ����,��Ϊ����,��Ϊ����
		@type  quantity: INT32
		"""
		r = self.questsTable.addDeliverAmount( self, item, quantity )
		self.updataQuestState( r )
		if cschannel_msgs.CELL_ROLEQUESTINTERFACE_2 in item.name():
			if quantity > 0:
				self.showBloodItemFlag()
			else:
				for item in self.getAllItems() :		# Ŀǰû�ҵ����õı�������
					if cschannel_msgs.CELL_ROLEQUESTINTERFACE_2 in item.name() :
						return
				self.removeBloodItemFlag()

	def onEnterSpace_( self ):
		"""
		�������µĿռ�
		"""
		sapceLabel = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		self.updataQuestState( self.questsTable.enterNewSpaceTrigger( self, sapceLabel ) )
	
	def onEnterSpaceAutoNextQuest( self, exposed ):
		"""
		exposed method
		�����ͼ���Զ��򿪽��������
		"""
		if exposed != self.id:
			return
			
		autoOpenNextQuestID = self.popTemp( Const.QUEST_AUTO_OPEN_NEXT_KEY, 0 )
		if autoOpenNextQuestID:
			autoOpenNextQuest = self.getQuest( autoOpenNextQuestID )
			nextQuestID = autoOpenNextQuest.getNextQuest( self )
			if nextQuestID:
				nextQuest = self.getQuest( nextQuestID )
				startByObjectIDs = nextQuest.getObjectIdsOfStart()
				for e in self.entitiesInRangeExt( Const.ENTER_SPACE_AUTO_ACCEPT_QUEST_DISTANCE, "NPC", self.position ):
					if e.className in startByObjectIDs:
						if e.getScript().questQuery( e, self, nextQuestID ) == csdefine.QUEST_STATE_NOT_HAVE:		# ��û�нӸ�����
							self.getQuest( nextQuestID ).gossipDetail( self, e )
						break
		
	def questYinpiaoValueChange( self, item ):
		"""
		��Ʊ��ֵ�����仯
		"""
		r = self.questsTable.addYinpiaoDeliverAmount( self, item )
		self.updataQuestState( r )


	def questPetEvent( self, eventType ):
		"""
		��������¼�

		@param   item: ��Ʒʵ��
		@type    item: instance
		@param quantity: ����,��Ϊ����,��Ϊ����
		@type  quantity: INT32
		"""
		r = self.questsTable.addPetEvent( self, eventType )
		self.updataQuestState( r )


	def questPetAmountAdd( self, petClassName, petDBID ):
		"""
		֪ͨ��ҳ����1

		@param   item: ��Ʒʵ��
		@type    item: instance
		@param quantity: ����,��Ϊ����,��Ϊ����
		@type  quantity: INT32
		"""
		r = self.questsTable.addDeliverPetAmount( self, petClassName, petDBID )
		self.updataQuestState( r )

	def questPetAmountSub( self, petClassName, petDBID ):
		"""
		֪ͨ��ҳ����м���1

		@param   item: ��Ʒʵ��
		@type    item: instance
		@param quantity: ����,��Ϊ����,��Ϊ����
		@type  quantity: INT32
		"""
		r = self.questsTable.subDeliverPetAmount( self, petClassName, petDBID )
		self.updataQuestState( r )


	def questTaskIncreaseState( self, questID, taskIndex ):
		"""
		Define Method.
		��ָ֪ͨ��������һ�������¼������
		"""
		if not self.has_quest( questID ):
			DEBUG_MSG( "player %i no has quest %i." % ( self.id, questID ) )
			return

		tasks = self.getQuestTasks( questID ).getTasks()
		try:
			task = tasks[ taskIndex ]
		except IndexError:
			ERROR_MSG( "%d:list index %d out of range" % ( questID, taskIndex ) )
			return

		task.increaseState()
		self.onTaskStateChange( questID, task, taskIndex )
		self.client.onTaskStateUpdate( questID, task )
		self.onQuestBoxStateUpdate()

		#Ѻ������ɹ�ʱ��Ҫɾ�����������Ӧ�ı�� add by chenweilan
		quest = self.getQuest( questID )
		if quest:
			if quest.getType() == csdefine.QUEST_TYPE_DART or quest.getType() == csdefine.QUEST_TYPE_MEMBER_DART:
				if self.hasFlag( csdefine.ROLE_FLAG_XL_DARTING ):
					self.removeFlag( csdefine.ROLE_FLAG_XL_DARTING )
				else:
					self.removeFlag( csdefine.ROLE_FLAG_CP_DARTING )

	def questTaskAddAnswerQuestion( self, isRight ):
		"""
		Define Method.
		֪ͨ���һ���ƾ�����
		"""
		self.removeTemp( "current_ie_question_id" )
		r = self.questsTable.addAnswerQuestion( self, isRight )
		if len(r) == 0:
			return
		self.updataQuestState( r )

		BigWorld.globalData['ImperialExaminationsMgr'].requestIEExpReward( self.base, self.playerName, self.level, isRight, r[0][2], self.wallow_getLucreRate() )


	def questTaskAddNormalAnswerQuestion( self,  questionType, isRight ):
		"""
		Define Method.
		֪ͨ�ش�����
		"""
		self.remove( "current_question_id" )
		r = self.questsTable.addNormalAnswerQuestion( self, questionType, isRight )
		self.updataQuestState( r )


	def questTaskFailed( self, questID, taskIndex ):
		"""
		Define Method.
		֪ͨһ���¼�����ʧ��
		"""
		if not self.has_quest( questID ):
			DEBUG_MSG( "player %i no has quest %i." % ( self.id, questID ) )
			return

		tasks = self.getQuestTasks( questID ).getTasks()
		try:
			task = tasks[ taskIndex ]
		except IndexError:
			ERROR_MSG( "%d:list index %d out of range" % ( questID, taskIndex ) )
			return

		task.collapsedState()
		self.onTaskStateChange( questID, task, taskIndex )
		self.client.onTaskStateUpdate( questID, task )

	def questTaskDecreaseState( self, questID, taskIndex ):
		"""
		��ָ֪ͨ��������һ�������¼�ʧ��
		"""
		if not self.has_quest( questID ):
			DEBUG_MSG( "player %i no has quest %i." % ( self.id, questID ) )
			return

		tasks = self.getQuestTasks( questID ).getTasks()
		try:
			task = tasks[ taskIndex ]
		except IndexError:
			ERROR_MSG( "%d:list index %d out of range" % ( questID, taskIndex ) )
			return

		task.decreaseState()
		self.onTaskStateChange( questID, task, taskIndex )
		self.client.onTaskStateUpdate( questID, task )

	def questMonsterKilled( self, monsterEntity ):
		"""
		Define Method.
		��֪ͨ�й��ﱻ���ɱ��
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		monsterEntity = BigWorld.entities.get( monsterEntity.id, None )
		if monsterEntity is None:
			WARNING_MSG( "entity is None." )
			return

		if monsterEntity.isDestroyed:
			WARNING_MSG( "entity is destroyed." )
			return

		r = self.questsTable.increaseKilled( self, monsterEntity )
		self.updataQuestState( r )

	def questDartKilled( self, dartQuestID, factionID ):
		"""
		Define Method.
		��֪ͨ���ڳ������ɱ��
		"""
		r = self.questsTable.increaseDartKilled( self, dartQuestID, factionID )
		self.updataQuestState( r )

	def questPetActChanged( self ):
		"""
		Define Method.
		��֪ͨ����ļ���״̬�����ı�
		"""
		r = self.questsTable.updatePetActState( self, self.pcg_hasActPet() )
		self.updataQuestState( r )

	def questMonsterEvoluted( self, className ):
		"""
		Define Method
		��֪ͨ�й��ﱻ��ҽ���
		"""
		r = self.questsTable.increaseEvolution( self, className )
		self.updataQuestState( r )

	def questSkillLearned( self, skillID ):
		"""
		��֪ͨ�м��ܱ����ѧϰ�ɹ�
		"""
		r = self.questsTable.increaseSkillLearned( self, skillID )

		self.updataQuestState( r )

	def questLivingSkillLearned(self, skillID):
		r = self.questsTable.increaseLivingSkillLearned(self, skillID)
		self.updataQuestState( r )

	def questFinishQuest( self, questID ):
		"""
		֪ͨ���������
		"""
		r = self.questsTable.questFinish( questID )
		self.updataQuestState( r )

	def questRoleLevelUp( self, level ):
		"""
		�ȼ��б仯
		"""
		r = self.questsTable.increaseLevel( level )
		self.updataQuestState( r )

	def questIncreaseItemUsed( self, itemID ):
		"""
		ʹ����Ʒ�������,����Ʒ���á�
		"""
		r = self.questsTable.increaseItemUsed( self, itemID )
		self.updataQuestState( r )



	def questPetAmountChange( self, quantity ):
		"""
		����һ����������
		"""
		r = self.questsTable.addPetAmount( self, quantity )
		self.updataQuestState( r )


	def questTalk( self, targetClassName ):
		"""
		�Ի������ͨ�����һ������Ŀ��
		"""
		r = self.questsTable.addTalk( self, targetClassName )
		self.updataQuestState( r )


	def questBuffAddOrRemoved( self, buffID, val ):
		"""
		Define Method
		��֪ͨ��buff�����ӻ��Ƴ�
		"""
		r = self.questsTable.updateBuffState( buffID, val )
		self.updataQuestState( r )


	def questPotentialFinish( self ):
		"""
		���Ǳ������

		@param   item: ��Ʒʵ��
		@type    item: instance
		@param quantity: ����,��Ϊ����,��Ϊ����
		@type  quantity: INT32
		"""
		r = self.questsTable.addPotentialFinish( self )
		self.updataQuestState( r )


	def questIncreaseSkillUsed( self, skillID, className ):
		"""
		ʹ����Ʒ�������,����Ʒ���á�
		"""
		r = self.questsTable.increaseSkillUsed( self, skillID, className )
		self.updataQuestState( r )


	def questSetRevivePos( self, spaceName ):
		"""
		ʹ����Ʒ�������,����Ʒ���á�
		"""
		r = self.questsTable.updateSetRevivePos( self, spaceName )
		self.updataQuestState( r )
		
	def questCampMoraleChange( self, camp, amount ):
		"""
		���ӻ������Ӫʿ��
		"""
		r = self.questsTable.onChangeCampMorale( self, camp, amount )
		self.updataQuestState( r )

	def questVehicleActived( self, VehicleID ):
		"""
		�����������
		"""
		r = self.questsTable.increaseVehicleActived( self, VehicleID )
		self.updataQuestState( r )

g_quests = QuestsFlyweight.instance()
class RoleQuestInterface( TasksNotify, RoleRandomQuestInterface, RoleDartQuestInterface, RoleActivityInterface ):
	"""
	�������ӿ�
	"""
	def __init__( self ):

		RoleRandomQuestInterface.__init__( self )
		RoleDartQuestInterface.__init__( self )
		RoleActivityInterface.__init__( self )

	def onDestroy( self ):
		"""
		����ʱ����
		"""
		self.questClearTeamMember()				# ���������Ϣ
		self.questClearFollowNPC()				# ������NPC�����NPC
		self.handleOffLineQuestEvent()			# ����ҵ����������ߴ���

	def getQuest( self, questID ):
		"""
		��������ID��ȡ��ȫ�ֵ�����ʵ��������������ѽӵ�����ʵ����

		@param questID: ����Ψһ��ʶ
		@type  questID: INT
		"""
		global g_quests
		try:
			return g_quests._quests[questID]
		except KeyError:
			ERROR_MSG( "%s(%i): global quest data not found. %i" % (self.playerName, self.id, questID) )
			return None

	def getLoopQuestLog( self, questID, createIfNotExist = False ):
		"""
		��ȡĳ������Ļ������б�
		@param questID: QUESTID; ��Ҫ��ȡ��������
		@param createIfNotExist: BOOL; ��ʾ����Ҳ����Ƿ񴴽�һ���µĲ����뵽�б���
		return: LOOP_QUEST
		"""
		for e in self.loopQuestLogs:
			if e.getQuestID() == questID:
				return e
		if createIfNotExist:
			e = LoopQuestTypeImpl()
			e.setQuestID( questID )
			e.reset()
			self.loopQuestLogs.append( e )
			return e
		return None

	def getQuestTasks( self, questID ):
		"""
		��ȡ�����ѽӵ�ĳ�����������Ŀ��

		@return: instance of QuestDataType,������񲻴����������쳣
		"""
		return self.questsTable[ questID ]

	def questAdd( self, quest, tasks ):
		"""
		@param quest: ����ʵ��
		@type  quest: Quest
		@param tasks: ���������������ʵ����
		@type  tasks: QuestDataType
		@return: None
		"""
		questID = quest.getID()
		self.questsTable.add( questID, tasks )
		quest.sendQuestLog( self, tasks )

		tasksDict = tasks.getTasks()
		for i, taskInst in tasksDict.iteritems():
			taskType = taskInst.getType()
			if taskType in [csdefine.QUEST_OBJECTIVE_DELIVER, csdefine.QUEST_OBJECTIVE_EVENT_TRIGGER, csdefine.QUEST_OBJECTIVE_KILL]:
				self.onQuestBoxStateUpdate()
			if taskType == csdefine.QUEST_OBJECTIVE_PET_ACT:
				self.questPetActChanged()
		
		if self.isRewardQuest( questID ):
			startTime = self.rewardQuestLog[ "startTime" ]
			degree = self.rewardQuestLog[ "degree" ] + 1
			self.rewardQuestLog = { "startTime":startTime, "degree":degree }
			DEBUG_MSG( "rewardQuest degree is %s,questID is %s,player id is %s"%( degree, questID, self.id ) )
			self.acceptedRewardQuestRecord.append( questID )
			#������������״̬֪ͨ,״̬����ѽ���
			self.client.sendRewardQuestState( questID, csdefine.REWARD_QUEST_ACCEPT, self.rewardQuestLog[ "degree" ] )
			pass
		
		try:
			g_logger.acceptQuestLog( self.databaseID, self.getName(), questID, self.level, self.grade ) 
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )

	def onQuestBoxStateUpdate( self ):
		"""
		�������пͻ��˿��������ӵ�״̬

		@param quest: ����
		@type  quest: Quest
		@param taskIndex: ����Ŀ������
		@type  taskIndex: INT32
		"""
		self.client.onQuestBoxStateUpdate() #questBoxID �� �������ӵ�className


	def findQuestByType( self , questType ):
		"""
		Ѱ������ָ����������
		@param questType: �������  �鿴 csdefine.py
		@return: list [questid...]
		"""
		questIDs = []
		for questID in self.questsTable.keys():
			quest = self.getQuest( questID )
			if quest and quest.getType() == questType:
				questIDs.append( questID )

		return questIDs

	def questRemove( self, questID, isAbandon ):
		"""
		@param questID: ����ID
		@type  questID: UINT32
		@param isAbandon: ��ʶ�������������(True)��������ɺ���ϵͳɾ��(False)
		@type  isAbandon: INT8
		@return: None
		"""
		self.questsTable.remove( questID )
		self.getQuest( questID ).onRemoved( self )
		self.client.onQuestLogRemove( questID, isAbandon )
		if self.isRewardQuest( questID ):
			if isAbandon:
				startTime = self.rewardQuestLog[ "startTime" ]
				degree = self.rewardQuestLog[ "degree" ]
				if questID in self.acceptedRewardQuestRecord:
					self.acceptedRewardQuestRecord.remove( questID )
					degree = self.rewardQuestLog[ "degree" ] - 1
					DEBUG_MSG( "rewardQuest degree is %s,questID is %s,player id is %s"%( degree, questID, self.id ) )
				self.rewardQuestLog = { "startTime":startTime, "degree":degree }
				#������������״̬֪ͨ,״̬��ɿ��Խ���
				self.client.sendRewardQuestState( questID, csdefine.REWARD_QUEST_CAN_ACCEPT, self.rewardQuestLog[ "degree" ] )

	def onQuestComplete( self, questID ):
		"""
		���������յ���֪ͨ,��ʾ���Ѿ��������ˡ�

		@param questID: ����ID
		@type  questID: UINT32
		@return: None
		"""
		tempTasks = self.getQuestTasks( questID )
		self.questRemove( questID, 0 )												#ɾ�������¼
		tempTasks.complete( self )													# ������Ŀ�����������ɾ��������Ʒ�ȣ�
		for task in tempTasks.getTasks().itervalues():
			task.removePlayerTemp( self )
		self.questFinishQuest( questID )
		self.getQuest( questID ).onComplete( self )
		if self.isRewardQuest( questID ):
			self.completedRewardQuestRecord.append( questID )
		try:
			g_logger.completeQuestLog( self.databaseID, self.getName(), questID,  self.level, self.grade, int( time.time() - tempTasks.getAcceptTime() ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )

	def questTaskIsCompleted( self, questID ):
		"""
		��ѯ�Ƿ���������Ŀ�궼�Ѵﵽ

		@param questID: ����ID
		@type  questID: UINT32
		@return: BOOL
		@rtype:  BOOL
		"""
		self.setTemp( "completedQuestID",  questID )
		state = self.questsTable[questID].isCompleted( self )
		self.removeTemp( "completedQuestID" )
		return state

	def questTaskIsFailed( self, questID, taskIndex ) :
		"""
		��ѯĳ������Ŀ���Ƿ��Ѿ�ʧ��
		"""
		tasks = self.getQuestTasks( questID ).getTasks()
		return tasks[ taskIndex ].isFailed( self )

	def questIsFailed( self, questID ) :
		"""
		��ѯ�����Ƿ��Ѿ�ʧ��
		"""
		tasks = self.getQuestTasks( questID ).getTasks()
		for task in tasks.itervalues() :
			if task.isFailed( self ) :
				return True
		return False

	def has_quest( self, questID ):
		"""
		��ѯ�Ƿ����ָ��������

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.questsTable.has_quest( questID )

	def has_randomQuestGroup( self, questID ):
		"""
		��ѯ�Ƿ����ָ���������������

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.questsRandomLog.has_randomQuestGroup( questID )

	def questIsFull( self ):
		return len( self.questsTable ) >= Const.QUEST_MAX_ASSIGNMENT

	def updateQuestTeamTask(self, srcEntityID, questID, taskIndex, count ):
		"""
		Exposed method.
		"""
		if self.id != srcEntityID:
			srcEntity = BigWorld.entities[srcEntityID]
			WARNING_MSG( "%s(%i): other entity caller my method, entityID = %i, caller name = %s" % (self.playerName, self.id, srcEntityID, srcEntity.playerName) )
			return

		task = self.questsTable[questID].getTasks()[taskIndex]
		if task.getType() == csdefine.QUEST_OBJECTIVE_TEAM:
			task.val1 = count
			self.onTaskStateChange( questID, task, taskIndex )
			self.client.onTaskStateUpdate( questID, task )

	def countTeamOccupationNear( self, occupation ):
		"""
		���¼��������Ŀ(�ڽ������ʱ����ã�
		@param   occupation: ����ְҵ
		@type    occupation: INT
		rtype:   INT
		"""
		if not self.isInTeam():
			return 0

		count = 0
		for e in self.getTeamMemberMailboxs():
			if e.id == self.id:
				continue
			r = BigWorld.entities.get( e.id )
			if r is not None:
				if self.position.flatDistTo( r.position ) <= csconst.COMMUNICATE_DISTANCE:
					if r.getClass() == occupation:
						count += 1
		return count

	def questClearTeamMember( self ):
		"""
		"""
		self.questsTable.clearTeamAmount( self )


	def requestQuestLog( self ):
		"""
		@param questID: ����ID
		2008.06.09����Ϊ�� client ���� cell �е� role ͳһ�ְ����� ���� by hyw
		"""
		self.setTemp( "rqi_init_list", self.questsTable.keys() )						# ��ʼ����ǰ���͵���������ǰ���ǣ����͵Ĺ����У�questsTable ���䣩
		self.addTimer( 0.0, csconst.ROLE_INIT_INTERVAL, ECBExtend.UPDATE_CLIENT_QUESTLOG_CBID )

	def onTimer_updateClientQuestLogs( self, timerID, cbid ) :
		"""
		�ְ����¿ͻ���������־
		2008.06.09��by hyw
		"""
		if len( self.queryTemp( "rqi_init_list" ) ) == 0:
			self.cancel( timerID )								# ֹͣ timer
			self.removeTemp( "rqi_init_list" )
			self.client.onInitialized( csdefine.ROLE_INIT_QUEST_LOGS )
			return

		questID = self.queryTemp( "rqi_init_list" ).pop( 0 )
		quest = self.getQuest( questID )						# ��ȡ����
		if not quest or ( quest and not quest.isTasksOk( self ) ):
			self.questsTable.remove( questID )
			ERROR_MSG( "%s(%i): quest %i has not found. I will removed it." % (self.getName(), self.id, questID) )
			return

		tasks = self.questsTable[questID]
		quest.sendQuestLog( self, tasks )					# ����������־


	def requestCompletedQuest( self ):
		"""
		Explore Method
		��ѯ�Ѿ���ɵ�����
		2008.06.10����Ϊ�� client ���� cell �е� role ͳһ���� ���� by hyw
		"""
		qlist = self.questsLog.list()
		if len( qlist ) > 0:
			self.client.onCompletedQuestIDListReceive( qlist )
		self.client.onInitialized( csdefine.ROLE_INIT_COMPLETE_QUESTS )

	def abandonQuest( self, srcEntityID, questID ):
		"""
		Exposed method.
		��������������
		"""
		if not self.has_quest( questID ): return

		if self.state == csdefine.ENTITY_STATE_DEAD:
			self.statusMessage( csstatus.ROLE_QUEST_PLAYER_IS_DIED )
			return

		if self.getQuest( questID ).abandoned( self , csdefine.QUEST_REMOVE_FLAG_PLAYER_CHOOSE ):
			self.questRemove( questID, True )
			self.onQuestBoxStateUpdate()
		else:
			self.statusMessage( csstatus.ROLE_QUEST_NOT_ALLOW_TO_ABANDON_BY_PLAYER )
			return
		try:
			g_logger.abandonQuestLog( self.databaseID, self.getName(), questID,  self.level, self.grade )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )
	
	def questIsCompleted( self, questID ):
		"""
		query the quest whether or not finish.

		@return: BOOL
		@rtype:  BOOL
		"""
		if self.isRewardQuest( questID ):
			if questID in self.completedRewardQuestRecord:
				return True
			else:
				return False
		return self.questsLog.has( questID )

	def recordQuestLog( self, questID ):
		"""
		save quest log which is finish.
		"""
		self.questsLog.add( questID )

	def onTaskStateChange( self, questID, task, taskIndex ):
		"""
		����״̬�ı�
		@param   questID: ����ID
		@param   task: ����taskʵ��
		"""
		#��������ʧ�ܱ�Ǵ���add by wuxo 2011-12-27
		quest = self.getQuest( questID )
		if not quest:
			return

		quest_failFlag = self.queryTemp( "questOffLineFail", [] )
		if questID in quest_failFlag:
			if quest.query( self ) == csdefine.QUEST_STATE_FINISH: #�������ʱɾ��
				if self.isRewardQuest( questID ):
					#������������״̬֪ͨ,״̬��������
					self.client.sendRewardQuestState( questID, csdefine.REWARD_QUEST_COMPLETED, self.rewardQuestLog[ "degree" ] )
				quest_failFlag.remove(i)
			else:
				try:
					for task in self.questsTable[questID].getTasks().values():
						if task.val1 == -1: #����ʧ��
							quest_failFlag.remove(i)
				except:
					quest_failFlag.remove(i)

		if len(quest_failFlag) == 0:
			self.removeTemp("questOffLineFail")
		else:
			self.setTemp( "questOffLineFail", quest_failFlag )

		#����Ŀ����� do something
		if self.taskIsCompleted( questID, taskIndex ):
			quest.onTaskCompleted( self, taskIndex )

		if quest.getStyle() == csdefine.QUEST_STYLE_AUTO:
			if not quest.complete( self, 0, "" ):
				return

			nextQuestID = quest.getNextQuest( self )
			if nextQuestID != 0:
				nextQuest = self.getQuest( nextQuestID )
				nextQuest.accept( self )

	#--------------------------------------------------------------------------
	# ����Ϊ�Ի�������/�ӷ�װ,������Ʒ�������񼰹�������
	#--------------------------------------------------------------------------
	def gossipWith( self, srcEntityID, targetID, keydlg ):#��NPC��ʼ�Ի��͹��ܶԻ�
		"""
		Exposed method.
		"""
		if self.id != srcEntityID and srcEntityID != 0:
			srcEntity = BigWorld.entities[srcEntityID]
			WARNING_MSG( "%s(%i): other entity caller my method, entityID = %i, caller name = %s" % (self.playerName, self.id, srcEntityID, srcEntity.playerName) )
			return

		try:
			targetEntity = BigWorld.entities[targetID]
		except KeyError:
			INFO_MSG( "entity %i not exist in world" % srcEntityID )	# ���Ӧ����Զ�������ܵ���
			return

		if self.qieCuoState in [ csdefine.QIECUO_READY, csdefine.QIECUO_FIRE ]: # �д�׼���ͽ����ڼ䲻����NPC���жԻ�
			self.statusMessage( csstatus.QIECUO_IS_NOT_DO )
			return
			

		if getattr( targetEntity, "subState", 0 ) == csdefine.M_SUB_STATE_GOBACK:	#����ǹ��ﴦ�ڻ���״̬�����ܶԻ�
			return

		if self.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
			if self.isState( csdefine.ENTITY_STATE_DEAD ):
				self.statusMessage( csstatus.NPC_TRADE_DEAD_FORBID_TALK )
			else:
				self.statusMessage( csstatus.NPC_TRADE_FORBID_TALK )
			return

		self.onGossipTrigger( targetID )	# �Ի�����16:21 2008-12-1,wsf

		srcEntity = BigWorld.entities[srcEntityID]

		#if srcEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
		#	srcEntity.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
		#	return

		srcClass = targetEntity.getScript()
		srcClass.gossipWith( targetEntity, self, keydlg )	#���ڶԻ���ֻ��Ҫ��֤��ɫ��real, npc��ghostҲû�й�ϵ����zyx��

	def onGossipTrigger( self, targetID ):
		"""
		�Ի�����һЩ��Ϊ,�����Ͻ�ɫ��Ǳ��Ч��buff

		@param targetID : �Ի���npc id
		@type targetID : OBJECT_ID
		"""
		self.removeAllBuffByBuffID( csconst.PROWL_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE ] )

		# ��Ӹ���״̬��Ա����ӳ��ĶԻ�
		if self.isTeamCaptain() and self.isTeamFollowing():
			timeDelay = 0.1
			for entity in self.entitiesInRangeExt( csconst.TEAM_FOLLOW_DISTANCE, "Role", self.position ):
				if entity.captainID == self.id and entity.spaceID == self.spaceID and entity.isTeamFollowing() and entity.isReal():
					entity.setTemp( "talkNPCID", targetID )
					entity.setTemp( "talkID", "Talk" )
					entity.addTimer( timeDelay, 0, ECBExtend.AUTO_TALK_CBID )
					timeDelay += 0.1

	def selectQuestFromItem( self, srcEntityID, uid ):#����Ʒ�Ի�
		"""
		Exposed method.
		@param  uid: ��Ʒ��ΨһID
		@type   uid: INT64
		"""
		if self.id != srcEntityID and srcEntityID != 0:
			srcEntity = BigWorld.entities[srcEntityID]
			WARNING_MSG( "%s(%i): other entity caller my method, entityID = %i, caller name = %s" % (self.playerName, self.id, srcEntityID, srcEntity.playerName) )
			return
		if self.getState() == csdefine.ENTITY_STATE_DEAD:
			ERROR_MSG( "%s(%i): you are deadth." % (self.playerName, self.id) )
			return
		item = self.getItemByUid_( uid )
		if item is None:
			ERROR_MSG( "%s(%i): item not found. %i, %i" % (self.playerName, self.id, uid) )
			return
		questID = item.getQuestID()
		if questID == 0:
			ERROR_MSG( "%s(%i): no quest exist in item '%s'." % (self.playerName, self.id, item.id) )
			return
		quest = self.getQuest( questID )
		if quest is None:
			ERROR_MSG( "%s(%i): quest(%i) not found from item '%s'." % (self.playerName, self.id, questID, item.id) )
			return

		if quest.query( self ) != csdefine.QUEST_STATE_NOT_HAVE:
			INFO_MSG( "%s(%i): not allow select quest %i." % (self.playerName, self.id, questID) )
			self.statusMessage( csstatus.ROLE_QUEST_CANNOT_GET_QUEST )
			return
		self.selectQuest_( questID, None )
		#self.getQuest( self.lastSelectedQuest ).startGossip( self , 0, "Talk" )
		#if item.consumable():	# phw: ������ѡ�񲻽�������ô�죿�ȽϺõİ취�����ǰ�������Ʒ��Ϊ������Ψһ,���������Ѵ���Ʒɾ����
		#	item.setAmount( item.getAmount() - 1 ,self )
		quest.gossipDetail( self, None )



	def selectQuest_( self, questID, activationSrc ):
		"""
		ѡ������

		��Լ��ֻ��¼���ѡ�������������ṩ�ߣ����������������顣

		@param activationSrc: �������Դ,�����Entity���ʾ������й������,���������None���ʾ����Ʒ����
		@return: ��
		"""
		self.lastSelectedQuest = questID							# ��¼���һ��ѡ�������
		if activationSrc is None:
			self.lastQuestActiveObj = 0
		else:
			self.lastQuestActiveObj = activationSrc.id
		return



	def declineSelectedQuest( self, srcEntityID ):
		"""
		Exposed method.
		�ܾ���ǰ��ѡ�������
		��Ҫ����������,�������������,�˽ӿ�Ҳ��ûʲô���壻
		"""
		if self.id != srcEntityID :
			srcEntity = BigWorld.entities[srcEntityID]
			WARNING_MSG( "%s(%i): other entity caller my method, entityID = %i, caller name = %s" % (self.playerName, self.id, srcEntityID, srcEntity.playerName) )
			return

		if self.lastQuestActiveObj != 0:
			player = BigWorld.entities.get( self.lastQuestActiveObj )
			if player:
				player.statusMessage( csstatus.ROLE_QUEST_SOMEONE_DECLINE_QUEST, self.playerName )
				self.lastQuestActiveObj = 0
		self.lastSelectedQuest = 0

	def questChooseReward( self, srcEntityID, questID, rewardIndex, codeStr, targetID ):
		"""
		Exposed method.
		�������,���ѡ������
		@param questID: �ĸ����������
		@type  questID: QUESTID
		@param rewardIndex: �ͻ���ѡ��Ľ�����Ʒ���ڵ�����
		@type  rewardIndex: INT32
		@param codeStr: ����Ŀ�����н������ַ���
		@type  codeStr:	String  					" 'name1':value1,'name2':value2,..."
		@return: None
		"""
		if self.id != srcEntityID:
			return

		if questID <= 0:
			INFO_MSG( "questID is Error ,questID:%i rewardIndex:%i" % ( questID, rewardIndex ) )
			return
		quest = self.getQuest( questID )

		if targetID == 0:
			# û�жԻ�Ŀ���޷�������
			return

		if not self.wallow_getLucreRate():
			# �߻�Ҫ�������Ϸ����Ϊ0ʱ���޷��ύ����
			self.statusMessage( csstatus.ROLE_QUSET_CANNOT_GET_LUCRE )
			return

		if self.si_myState >= csdefine.TRADE_SWAP_BEING:
			self.statusMessage( csstatus.QUEST_BOX_BAG_FULL )
			return

		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION )
			return

		targetEntity = BigWorld.entities.get( targetID )
		if targetEntity is None:
			return
		if not targetEntity.isInteractionRange( self ):
			WARNING_MSG( "%s(%i): target too far." % (targetEntity.getName(), targetEntity.id) )
			return

		targetEntity.getScript().questChooseReward( targetEntity, self, questID, rewardIndex, codeStr )

	def questSelect( self, srcEntityID, questID, targetID ):
		"""
		Exposed method.

		@type targetID: target of gossip with. ������targetID����Ϊ0,��Ϊ����ӿ�һ���Ǵ�NPC���ϴ�����,�����Ĺ����������Ʒ���������������Ľӿڣ�
		"""
		if self.id != srcEntityID:
			return

		try:
			targetEntity = BigWorld.entities[targetID]
		except KeyError:
			INFO_MSG( "entity %i not exist in world" % targetID )	# ���Ӧ����Զ�������ܵ���
			return

		if not targetEntity.isInteractionRange( self ):
			WARNING_MSG( "%s(%i): target too far,my position is %s.target( %s)'s position is %s" % (self.getName(), self.id, self.position, targetEntity.className, targetEntity.position) )
			return	# ����Ŀ��̫Զ������̸

		srcClass = targetEntity.getScript()

		if srcClass.hasStartQuest( questID ) or srcClass.hasFinishQuest( questID ):
			# ֻ��ָ������������������б��в��������
			srcClass.questSelect( targetEntity, self, questID )

	def questAcceptForce( self, srcEntityID, questID, questEntityID ):
		"""
		Exposed method.
		����һ�����񡪡�ǿ�ƽ��ܳɹ��������κ��ж�
		@type targetID: target of gossip with. ����������Ϊ0���ʾ�����Ǵ���Ʒ�����ģ���ʱ�����ǹ�������
		"""
		if self.id != srcEntityID:
			return
		quest = self.getQuest( questID )
		if quest == None:
			ERROR_MSG( "Can not accept this quest! quest id is %s " % questID )
			return
		if questEntityID > 0:
			self.setTemp( "questEntityID", questEntityID )
		quest.accept( self )


	def questAccept( self, srcEntityID, questID, targetID ):
		"""
		Exposed method.
		����һ������
		@type targetID: target of gossip with. ����������Ϊ0���ʾ�����Ǵ���Ʒ�����ģ���ʱ�����ǹ�������
		"""
		if self.id != srcEntityID:
			return


		"""
		if self.getQuest( questID ).getStyle() == csdefine.QUEST_STYLE_LOOP_GROUP:
			if not self.groupQuestSavedAndFailedProcess( questID ):
				return
		"""
		targetEntity = BigWorld.entities.get( targetID )
		srcEntity    = BigWorld.entities.get( srcEntityID )

		if not srcEntity:
			return
		if srcEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
			srcEntity.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
			return False

		if targetEntity:
			if not targetEntity.isInteractionRange( self ):
				WARNING_MSG( "%s(%i): target too far." % (self.playerName, self.id) )
				return	# ����Ŀ��̫Զ������̸

			#if self.getQuest( questID ).getStyle() == csdefine.QUEST_STYLE_LOOP_GROUP:
			#	if not self.groupQuestSavedAndFailedProcess( questID ):
			#		return

			srcClass = targetEntity.getScript()
			if srcClass.hasStartQuest( questID ):	# �ǽ������NPC
				srcClass.questAccept( targetEntity, self, questID )
		else:
			# Ŀ�겻����,������Ʒ����
			quest = self.getQuest( questID )
			state = quest.query( self )
			if state != csdefine.QUEST_STATE_NOT_HAVE:
				INFO_MSG( "can't accept quest %i, state = %i." % (questID, state) )
				return
			#if self.getQuest( questID ).getStyle() == csdefine.QUEST_STYLE_LOOP_GROUP:
			#	if not self.groupQuestSavedAndFailedProcess( questID ):
			#		return
			quest.accept( self )

	def remoteQuestAccept( self, questID ):
		"""
		define method
		����һ������
		���ﾭ����base���ж��󣬲��ߵ���
		"""
		quest = self.getQuest( questID )
		quest.baseAccept( self )


	def groupQuestReAccept( self,questID ):
		"""
		������ʧ�ܣ����������½��ܣ���Ҫ��Ʒ���Ǯ�Ĵ���
		"""
		if self.money < self.getQuest(questID).getRepeatMoney():
			self.statusMessage( csstatus.ROLE_QUEST_GROUPQUEST_REACCEPT_FAILED )
			return False
		else:
			money = 0 - self.getQuest(questID).getRepeatMoney()
			self.addMoney( money, csdefine.CHANGE_MONEY_GROUPQUESTREACCEPT )
		#self.statusMessage( csstatus.ROLE_QUEST_GROUPQUEST_REACCEPT_FAILED, self.getGroupQuestCount(questID), self.getSubQuestCount(questID))
		return True

	def setActiveQuestID( self , questID ):
		"""
		���õ�ǰ�����ID �ṩ��startGossip ������ �� Ĭ��ʹ���������ͨ��,��Ϊ�������������ڶԻ�������
		@param 		 questID:  ��ǰ�Ի�����ID
		@type 		 questID: INT32
		@return: None
		"""
		self.lastSelectedQuest = questID

	def taskIsCompleted( self, questID, index ):
		"""
		��ѯ�Ƿ�ָ������Ŀ���Ѵﵽ
		@param questID: ����ID
		@type  questID: QUESTID
		@param index:   ����Ŀ������
		@type  index:	INT
		@return: BOOL
		@rtype:  BOOL
		"""
		if self.questsTable.has_quest( questID ):
			return self.questsTable[questID].isIndexTaskComplete( self, index )
		return True		# û�н��������ͱ�ʾ�Ѿ������

	def tasksIsCompleted( self, questID, indexList ):
		"""
		��ѯ�Ƿ���ָ������Ŀ���Ѵﵽ
		@param questID: ����ID
		@type  questID: QUESTID
		@param index:   ����Ŀ������
		@type  index:	INT
		@return: BOOL
		@rtype:  BOOL
		"""
		for index in indexList:
			if not self.taskIsCompleted( questID, index ):
				return False
		return True

	def hasTaskIndex( self, questID, index ):
		"""
		�Ƿ����ĳ����������
		"""
		if not self.has_quest( questID ):
			DEBUG_MSG( "player %i no has quest %i." % ( self.id, questID ) )
			return

		tasks = self.getQuestTasks( questID ).getTasks()
		return index in tasks

	# ----------------------------------------
	# ����Ϊ��ͻ��˷�����Ϣ�ķ�װ�ӿ�
	# ----------------------------------------
	def sendGossipComplete( self ,targetID ):
		"""
		@param 		 player: ROLE ʵ��
		@type 		 player: OBJECT_ID
		@return: None
		"""
		self.client.onGossipComplete( targetID )

	def setGossipText( self, text ):
		"""
		@param 		player: ROLE ʵ��
		@type 		 player: OBJECT_ID
		@param 		text: �������񴰿��ı�
		@type 		 text: str
		@return: 	None
		"""
		self.client.onSetGossipText( text )

	def addGossipOption( self, talkID, title, type = csdefine.GOSSIP_TYPE_NORMAL_TALKING ):
		"""
		����ϵͳ��ͨ�Ի�
		@param 		player: ROLE ʵ��
		@type 		 player: OBJECT_ID
		@type 		talkID: string
		@type 		 title: string
		@return:	 None

		type : Ĭ������ͨ�Ի����� csdefine.GOSSIP_TYPE_NORMAL_TALKING
		"""
		self.client.onAddGossipOption( talkID, title, type )

	def addGossipQuestOption( self, questID, state ):
		"""
		����ϵͳ����Ի�
		@param 		player: ROLE ʵ��
		@type  		player: OBJECT_ID
		@type dlgKey: string
		@type   title: string
		"""
		quest = self.getQuest( questID )
		self.client.onAddGossipQuestOption( questID, state, quest.getLevel( self ) )

	def sendQuestRewards( self, questID, rewards ):
		"""
		@param 		player: ROLE ʵ��
		@type 		 player: OBJECT_ID
		@type		 questID: INT32
		@param		 rewards: ������
		@type  		rewards: items
		@param 		rewardsChoose: ����ѡ����
		@type  		rewardsChoose: items
		@return: None
		"""
		self.client.onQuestRewards( questID, rewards )

	def sendObjectiveDetail( self, questID, objectiveDetail ):
		"""
		@param 		questID: ����ID
		@type		questID: INT32
		@param		objectiveDetail: ����Ŀ������
		@type		objectiveDetail: list
		"""
		self.client.onQuestObjectiveDetail( questID, cPickle.dumps( objectiveDetail, 2 ) )

	def sendQuestSubmitBlank( self, questID, submitInfo ):
		"""
		@param 		questID: ����ID
		@type		questID: INT32
		@param		submitInfo: �ύ��Ʒ����
		@type		submitInfo: tuple
		"""
		self.client.onQuestSubmitBlank( questID, cPickle.dumps( submitInfo, 2) )



	def sendQuestDetail( self, questID, level, targetID ):
		"""
		@type	questID: INT32
		@type	title: string
		@type	level:INT32
		@type	storyText:str
		@type	objectiveText:str
		@type	targetID: OBJECT_ID
		@return: None
		"""
		self.client.onQuestDetail( questID, level, targetID )

	def sendQuestIncomplete( self, questID, level, targetID ):
		"""
		@type	questID: INT32
		@type	title: string
		@type	level:INT32
		@type	incompleteText:str
		@type	targetID: OBJECT_ID
		@return: None
		"""
		self.client.onQuestIncomplete( questID, level, targetID )

	def sendQuestPrecomplete( self, questID, level, targetID ):
		"""
		@type	questID: INT32
		@type	title: string
		@type	level: INT32
		@type	precompleteText: str
		@type	targetID: OBJECT_ID
		@return: None
		"""
		self.client.onQuestPrecomplete( questID, level, targetID )

	def sendQuestComplete( self, questID, level, targetID ):
		"""
		@type	questID: INT32
		@type	title: string
		@type	level: INT32
		@type	completeText: str
		@type	targetID: OBJECT_ID
		@return: None
		"""
		self.client.onQuestComplete( questID, level, targetID )

	def sendTongMemberQuest( self, questID, questEntityID ):
		"""
		define method
		# ����Χ30�׷�Χ���������а���Ա��������������
		"""
		qData = self.queryTemp( "needSendTongQuest" )
		if qData is None:
			return
		g = BigWorld.entities.get
		for e in self.tong_onlineMemberMailboxs.itervalues():
			eEntity = g( e.id, None )
			if eEntity is None:
				continue
			if eEntity.spaceID == self.spaceID and eEntity.position.flatDistTo( self.position ) <= qData["dis"]:
				questLevel = 0
				questID = 0
				for i in qData["qus"]:
					level = int( i[1] )
					if level <= eEntity.level and level >= questLevel:
						questLevel = level
						questID = int( i[0] )
				e.client.dartTongInvite( questID, questEntityID )
		self.removeTemp( "needSendTongQuest" )

	def endGossip( self ,targetEntity ) :
		"""
		@param player: ROLE ʵ��
		@type  player: OBJECT_ID
		@return: None
		"""
		INFO_MSG( "player is endGossip")
		self.lastSelectedQuest = 0
		self.client.onEndGossip()


	def onAutoAddNewQuest( self, controllerID, userData ):
		"""
		"""
		self.getQuest( self.queryTemp( "newQuestAddID" ) ).accept( self )
		self.removeTemp( "newQuestAddID" )


	def onDieAffectQuest( self, player ):
		"""
		��ɫ�����������Ӱ��
		������Щ����Ҫ���ɫ����������������������ʧ��
		"""
		dart_id = self.queryTemp( "dart_id", 0)
		if dart_id != 0 and BigWorld.entities.has_key( dart_id ):
			dart = BigWorld.entities[dart_id]
			dart.enemyList.clear()
			dart.changeState( csdefine.ENTITY_STATE_FREE )

		resultList = self.questsTable.roleDieAffectQuest( player )
		for r in resultList:
			self.onTaskStateChange( r[0], self.questsTable[r[0]]._tasks[r[1]], r[1] )
			self.client.onTaskStateUpdate( r[0], self.questsTable[r[0]]._tasks[r[1]] )

		if self.vehicle is not None:
			if self.vehicle.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ):
				self.vehicle.disMountEntity( self.id, self.id )

	def questClearFollowNPC( self ):
		"""
		�����������NPC
		"""
		# ������������
		for questID, questData in self.questsTable.items():
			# ��ѯ�������Ƿ��и����NPC
			npcIDs = questData.query( "follow_NPC", [] )
			if npcIDs.__class__.__name__ == "int":
				npcIDs = [npcIDs]
			for npcID in npcIDs: #modify by wuxo2012-1-18
				if BigWorld.entities.has_key( npcID ):
					# ɱ�����NPC
					BigWorld.entities[ npcID ].defDestroy()
			# ������
			questData.set( "follow_NPC" , [] )

	def isMyOwnerFollowNPC( self, ID ):
		"""
		FollowNPC��ѯ���ǲ����ҵ�������
		"""
		for questID, questData in self.questsTable.items():
			npcID = questData.query( "follow_NPC", [] )
			if npcID.__class__.__name__ == "int":
				npcID = [npcID]
			if ID in npcID : #modify by wuxo 2012-1-18
				return True
		return False

	def beforeEnterSpaceDoor( self, destPosition, destDirection ):
		"""
		define method
		"""
		id = self.queryTemp("dart_id", 0)
		if id != 0:
			if BigWorld.entities.has_key( id ):
				if self.position.distTo( BigWorld.entities[id].position ) < DISTANCE_FOR_PLAYER_TAKE_SLAVE:				#ͨ��������
					if BigWorld.entities[id].isRideOwner:
						BigWorld.entities[id].disMountEntity( self.id, self.id )
					BigWorld.entities[id].flyToMasterSpace()

	def potentialQuestShare(self, questID, tasks ):
		"""
		define method.
		"""
		if self.questIsFull():
			self.statusMessage( csstatus.ROLE_QUEST_QUEST_BAG_FULL )
			return
		if len( self.findQuestByType( csdefine.QUEST_TYPE_POTENTIAL ) ) > 0:
			self.statusMessage( csstatus.POTENTIAL_HAS_SAME_TYPE_QUEST )
			return
		# �������ϴ���ʡbuff�ļһﲻ�ɹ����ȡǱ������ by ����
		buffs = self.getBuffs()
		if len( buffs ) != 0:
			for buff in buffs:
				buffID = buff['skill']._buffID
				if buffID is None or buffID == 0: continue
				if buffID == 299005:
					self.statusMessage( csstatus.ROLE_QUEST_BUFF_BAN_POTENTIAL )
					return
		self.questAdd( self.getQuest( questID ), tasks )
		self.statusMessage( csstatus.ROLE_QUEST_QUEST_ACCEPTED,	self.getQuest( questID ).getTitle() )
		try:
			g_logger.acceptQuestLog( self.databaseID, self.getName(), questID,  self.level, self.grade )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )

	def handleOffLineQuestEvent( self ):
		"""
		����ҵ����������ߴ���
		"""
		# ��������ϵĿƾ�����
		# self.deleteIEQuest()
		# ������Լ�����������Ҫ���������������
		#��������ʧ������add by wuxo 2011-12-26
		quest_failFlag = self.queryTemp( "questOffLineFail", [] )
		for i in quest_failFlag :
			if i in self.questsTable:
				for taskIndex in self.questsTable[i].getTasks().keys():
					self.questTaskFailed( i, taskIndex )

	def onAddBuff( self, buff ):
		"""
		������һ�� buff ʱ������
		"""
		self.questBuffAddOrRemoved( buff[ "skill" ].getBuffID(), 1 )

	def onRemoveBuff( self, buff ):
		"""
		ɾ��һ�� buff ʱ������
		"""
		self.questBuffAddOrRemoved( buff[ "skill" ].getBuffID(), 0 )

	def springRiddleReward( self ):
		"""
		Define method.
		�����ڵ��ս���
		"""
		awarder = Love3.g_rewards.fetch( csdefine.RCG_SPRING_LIGHT, self )
		freeSpace = self.getNormalKitbagFreeOrderCount()	# ����ʣ�������
		if freeSpace < len( awarder.items ):
			self.statusMessage( csstatus.ROLE_QUEST_GET_FU_BI_MAIL_NOTICE )
			title = cschannel_msgs.CELL_ROLEQUESTINTERFACE_3
			content = cschannel_msgs.CELL_ROLEQUESTINTERFACE_3
			self.mail_send_on_air_withItems( self.getName(), csdefine.MAIL_TYPE_QUICK, title, content, awarder.items )
		else:
			awarder.award( self, csdefine.ADD_ITEM_SPRING_FESTIVAL )
			self.statusMessage( csstatus.ROLE_QUEST_GET_FU_BI )

	def setTongDartJoinNum( self, questID, number ):
		"""
		define method
		���ý�ɫ��ǩ��һ�������ڵ����� by ����
		"""
		self.setTemp( "tongDartMembers", number )

	def tongDartExpReward( self ):
		"""
		define method
		�ڳ�ˢ�ٷ�ʱ��������Ҿ��齱��
		"""
		if not self.level in SecondExpDatas:
			return
		exp = SecondExpDatas[self.level] * 360
		self.addExp( exp, csdefine.CHANGE_EXP_TONG_DART_ROB )

	def questSingleReward( self, srcEntityID, questID ):
		"""
		Exposed method.
		�������,���ֱ�ӻ�ý���������ṩ������Ҫͨ��NPC��ֱ���ύ�������Ľӿ�ʹ�õġ�
		@param questID: �ĸ����������
		@type  questID: QUESTID
		"""
		if self.id != srcEntityID:
			return

		quest = self.getQuest( questID )
		if quest == None:
			return

		if not "" in quest.getObjectIdsOfFinish():
			return

		if self.si_myState >= csdefine.TRADE_SWAP_BEING:
			self.statusMessage( csstatus.QUEST_BOX_BAG_FULL )
			return

		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION )
			return

		if csdefine.QUEST_STATE_FINISH != quest.query( self ):
			return

		try:
			quest.complete( self, 0, "" )
		except:
			self.questRemove( questID, 0 )
			self.questFinishQuest( questID )
			EXCEHOOK_MSG("questID(%i) has bug in complete function! playerName:%s" % ( questID, self.getName()) )


	# -----------------------------------------------------------------------------------------------------
	# �������������أ��������������ʾ�Ĵ���
	# -----------------------------------------------------------------------------------------------------
	def onQuestTrapTipClicked( self, srcEntityID, entityID ):
		"""
		Exposed method.
		��ҵ������������ʾ�Ĵ���

		@param srcEntityID���������͹����ĵ�����id
		@type srcEntityID:	OBJECT_ID
		@param questID��	����ID
		@type questID:		INT32
		"""
		if srcEntityID != self.id:
			return
		try:
			entity = BigWorld.entities[ entityID ]
		except:
			ERROR_MSG( "%s(%i): entityID = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, entityID) )
			return
		entity.getScript().onTipClicked( self )

	# -----------------------------------------------------------------------------------------------------
	# AI�й�������������ݵĴ���
	# -----------------------------------------------------------------------------------------------------
	def onAIAddQuest( self, questID, timeDelay ):
		"""
		���Լ����һ������
		@param questID:		����ID
		@type questID:		QUESTID
		@param timeDelay:	���������ʾ��ʱʱ��
		@type timeDelay:	INT16
		"""
		quest = self.getQuest( questID )
		if quest and quest.query( self ) == csdefine.QUEST_STATE_NOT_HAVE:
			quest.accept( self )										# ��������
			self.delayCall( timeDelay, "showQuestLog", questID )
			
	#-----------------------------------------------------------------------
	# ��Ӫ�������
	#-----------------------------------------------------------------------
	def removeFailedCampQuests( self ):
		"""
		�Ƴ������������δ��ɵ���Ӫ�����Ӫ�ճ�����
		"""
		removeQuest = []
		for questID in self.questsTable.keys():
			quest = self.getQuest( questID )
			if quest.getType() in [ csdefine.QUEST_TYPE_CAMP_ACTIVITY, csdefine.QUEST_TYPE_CAMP_DAILY ] and not self.questTaskIsCompleted( questID ):
				if quest.query( self ) != csdefine.QUEST_STATE_FINISH:
					removeQuest.append( questID )
		for i in removeQuest:
			self.abandonQuest( self.id, i )

	#--------------------------------------------------------------------------------------------------------
	#�����������
	#--------------------------------------------------------------------------------------------------------
	def requestRewardQuest( self ):
		"""
		��������������Ϣ
		"""
		count = 0
		length = len( self.canAcceptRewardQuestRecord )
		timeData = sorted( g_rewardQuestLoader.getTimeDataFromToday() )
		presentTime = time.time()
		startTime = time.time()
		currentDay = time.localtime()[2]
		degree = 0
		if length == 0:
			self.rewardQuestRefresh( 1, csdefine.REWARD_QUEST_SYSTEM_REFRESH )
			self.rewardQuestLog = { "startTime":startTime, "degree":degree }
		else:
			lastDay = time.localtime( self.rewardQuestLog[ "startTime" ] )[2]
			if self.isNeedRefresh():
				self.rewardQuestRefresh( 0, csdefine.REWARD_QUEST_SYSTEM_REFRESH )
				if lastDay == currentDay:
					degree = self.rewardQuestLog[ "degree" ]
				self.rewardQuestLog = { "startTime":startTime, "degree":degree }
		nextRefreshTime = 0.0
		nextRefreshTimeInterval = 0.0
		for t in timeData:
			if presentTime < t:
				nextRefreshTimeInterval = t - presentTime
				nextRefreshTime = t
				self.addTimer( nextRefreshTimeInterval, 0, ECBExtend.REWARD_QUEST_SYSTEM_REFRESH )
				break
		self.sendRewardQuestDatas( nextRefreshTime, self.rewardQuestLog[ "degree" ] )
		self.client.onInitialized( csdefine.ROLE_INIT_REWARD_QUESTS )
		
	def onTimer_rewardQuestRefresh( self, timerID, cbid ):
		"""
		��ʱ������ˢ����������
		"""
		timeData = sorted( g_rewardQuestLoader.getTimeDataFromToday() )
		presentTime = time.time()
		startTime = time.time()
		currentDay = time.localtime()[2]
		lastDay = time.localtime( self.rewardQuestLog[ "startTime" ] )[2]
		degree = 0
		self.rewardQuestRefresh( 0, csdefine.REWARD_QUEST_SYSTEM_REFRESH )
		if lastDay == currentDay:
			degree = self.rewardQuestLog[ "degree" ]
		self.rewardQuestLog = { "startTime":startTime, "degree":degree }
		nextRefreshTime = 0.0
		nextRefreshTimeInterval = 0.0
		for t in timeData:
			if presentTime < t:
				nextRefreshTimeInterval = t - presentTime
				nextRefreshTime = t
				self.addTimer( nextRefreshTimeInterval, 0, ECBExtend.REWARD_QUEST_SYSTEM_REFRESH )
				break
		self.sendRewardQuestDatas( nextRefreshTime, self.rewardQuestLog[ "degree" ] )
		
	def rewardQuestItemRefresh( self, isAllRefresh, refreshType ):
		"""
		��Ʒˢ��
		"""
		self.rewardQuestRefresh( isAllRefresh, refreshType )
		timeData = sorted( g_rewardQuestLoader.getTimeDataFromToday() )
		presentTime = time.time()
		nextRefreshTime = 0.0
		for t in timeData:
			if presentTime < t:
				nextRefreshTime = t
				break
		self.sendRewardQuestDatas( nextRefreshTime, self.rewardQuestLog[ "degree" ] )
		
	def rewardQuestRefresh( self, isAllRefresh, refreshType ):
		"""
		��������ϵͳˢ��
		"""
		totalQuestList = []
		greenQualityNum = 0
		if isAllRefresh:
			#ȫ��ˢ�£�Ҳ��������ȫ�������������
			#��ȡ��ҵĶ�Ӧ����Ķ�ӦС��Ķ�Ӧ�ȼ�������ID������Щ������ȥ���
			for record in self.canAcceptRewardQuestRecord:
				questID = record.getQuestID()
				if self.has_quest( questID ):
					self.questRemove( questID, True )
			self.canAcceptRewardQuestRecord = []
			totalQuestList += self.rewardTongQuestRefresh( Const.REWARD_QUEST_SMALL_TYPE_NUM, Const.REWARD_QUEST_SMALL_TYPE_NUM )
			totalQuestList += self.rewardCampQuestRefresh( Const.REWARD_QUEST_NUM, [] )
			totalQuestList += self.rewardDailyQuestRefresh( Const.REWARD_QUEST_NUM, [] )
		else:
			#����ˢ�£��ų��Ѿ���ȡ����û���ύ������ID
			canAcceptRewardQuestRecord = self.canAcceptRewardQuestRecord
			excludeList = []
			removeList = []
			for record in canAcceptRewardQuestRecord:
				questID = record.getQuestID()
				if self.has_quest( questID ):
					excludeList.append( ( record.getBigType(), record.getSmallType(), questID ) )
					if record.getQuality() == csdefine.REWARD_QUEST_QUALITY_GREEN:
						greenQualityNum += 1
				else:
					removeList.append( record )
			for record in removeList:
				self.canAcceptRewardQuestRecord.remove( record )
			tongQuestNum = Const.REWARD_QUEST_SMALL_TYPE_NUM
			runMerchantQuestNum = Const.REWARD_QUEST_SMALL_TYPE_NUM
			campQuestNum = Const.REWARD_QUEST_NUM
			dailyQuestNum = Const.REWARD_QUEST_NUM
			campQuest = []
			dailyQuest = []
			for questItem in excludeList:
				if questItem[0] == csdefine.REWARD_QUEST_TYPE_TONG:
					if questItem[1] in [ csdefine.REWARD_QUEST_TYPE_TONG_BUILD, csdefine.REWARD_QUEST_TYPE_TONG_NORMAL ]:
						tongQuestNum -= 1
					elif questItem[1] == csdefine.REWARD_QUEST_TYPE_RUN_MERCHANT:
						runMerchantQuestNum -= 1
				elif questItem[0] == csdefine.REWARD_QUEST_TYPE_CAMP:
					if questItem[1] == csdefine.REWARD_QUEST_TYPE_CAMP_DAILY:
						campQuestNum -= 1
						campQuest.append( questItem )
				elif questItem[0] == csdefine.REWARD_QUEST_TYPE_DAILY:
					if questItem[1] in [ csdefine.REWARD_QUEST_TYPE_CRUSADE, csdefine.REWARD_QUEST_TYPE_MATERIAL, csdefine.REWARD_QUEST_TYPE_SPACE_COPY ]:
						dailyQuestNum -= 1
						dailyQuest.append( questItem )
			totalQuestList += self.rewardTongQuestRefresh( tongQuestNum, runMerchantQuestNum )
			totalQuestList += self.rewardCampQuestRefresh( campQuestNum, campQuest )
			totalQuestList += self.rewardDailyQuestRefresh( dailyQuestNum, dailyQuest )
		#����totalQuestList��ѡ�е��������һ������Ʒ�ʵ����
		self.completedRewardQuestRecord = []
		self.assignQuestQuality( totalQuestList, refreshType, greenQualityNum )
		
	def rewardTongQuestRefresh( self, tongQuestNum, runMerchantQuestNum ):
		"""
		����ճ������Լ���Ὠ������ˢ��,����һ����������ID��������࣬����С��������б�
		"""
		bigType = csdefine.REWARD_QUEST_TYPE_TONG
		totalQuestList = []
		if tongQuestNum == 0 and runMerchantQuestNum == 0:
			return totalQuestList
		if bigType in g_rewardQuestLoader.getQuestDatas().keys():
			tongBuildQuest = []
			tongNormalQuest = []
			if tongQuestNum != 0:
				if csdefine.REWARD_QUEST_TYPE_TONG_BUILD in g_rewardQuestLoader.getQuestDatas()[ bigType ].keys():
					tongBuildQuest = g_rewardQuestLoader.getQuestDataFromLevelAndType( bigType, csdefine.REWARD_QUEST_TYPE_TONG_BUILD, self.getLevel() )
				if csdefine.REWARD_QUEST_TYPE_TONG_NORMAL in g_rewardQuestLoader.getQuestDatas()[ bigType ].keys():
					tongNormalQuest = g_rewardQuestLoader.getQuestDataFromLevelAndType( bigType, csdefine.REWARD_QUEST_TYPE_TONG_NORMAL, self.getLevel() )
				questList = tongBuildQuest + tongNormalQuest
				if questList:
					quest = random.choice( questList )
					if quest in tongBuildQuest:
						totalQuestList.append( ( bigType, csdefine.REWARD_QUEST_TYPE_TONG_BUILD, quest ) )
					else:
						totalQuestList.append( ( bigType, csdefine.REWARD_QUEST_TYPE_TONG_NORMAL, quest ) )
			if runMerchantQuestNum != 0:
				runMerchantQuest = []
				if csdefine.REWARD_QUEST_TYPE_RUN_MERCHANT in g_rewardQuestLoader.getQuestDatas()[ bigType ].keys():
					runMerchantQuest = g_rewardQuestLoader.getQuestDataFromLevelAndType( bigType, csdefine.REWARD_QUEST_TYPE_RUN_MERCHANT, self.getLevel() )
				if runMerchantQuest:
					quest = random.choice( runMerchantQuest )
					if quest:
						totalQuestList.append( ( bigType, csdefine.REWARD_QUEST_TYPE_RUN_MERCHANT, quest ) )
		return totalQuestList
		
	def rewardCampQuestRefresh( self, campQuestNum, questList = None ):
		"""
		��Ӫ�ճ�����ˢ��,����һ����������ID��������࣬����С��������б�
		"""
		bigType = csdefine.REWARD_QUEST_TYPE_CAMP
		totalQuestList = []
		if campQuestNum == 0:
			return totalQuestList
		if bigType in g_rewardQuestLoader.getQuestDatas().keys():
			campDailyQuest = []
			if csdefine.REWARD_QUEST_TYPE_CAMP_DAILY in g_rewardQuestLoader.getQuestDatas()[ bigType ].keys():
				tempCampDailyQuest = g_rewardQuestLoader.getQuestDataFromLevelAndType( bigType, csdefine.REWARD_QUEST_TYPE_CAMP_DAILY, self.getLevel() )
			for questID,belongCamp in tempCampDailyQuest:
				if belongCamp == self.getCamp():
					campDailyQuest.append( questID )
			for questItem in questList:
				campDailyQuest.remove( questItem[2] )
			if campQuestNum >= len( campDailyQuest ):
				quest = campDailyQuest
			else:
				quest = random.sample( campDailyQuest, campQuestNum )
			for questID in quest:
				totalQuestList.append( ( bigType, csdefine.REWARD_QUEST_TYPE_CAMP_DAILY, questID ) )
		return totalQuestList
	
	def rewardDailyQuestRefresh( self, dailyQuestNum, questList = None ):
		"""
		ÿ������ˢ��,����һ����������ID��������࣬����С��������б�
		"""
		bigType = csdefine.REWARD_QUEST_TYPE_DAILY
		totalQuestList = []
		if dailyQuestNum == 0:
			return totalQuestList
		if bigType in g_rewardQuestLoader.getQuestDatas().keys():
			dailyCrusadeQuest = []
			dailyMaterialQuest = []
			dailySpaceCopyQuest = []
			if csdefine.REWARD_QUEST_TYPE_CRUSADE in g_rewardQuestLoader.getQuestDatas()[ bigType].keys():
				dailyCrusadeQuest = g_rewardQuestLoader.getQuestDataFromLevelAndType( bigType, csdefine.REWARD_QUEST_TYPE_CRUSADE, self.getLevel() )
			if csdefine.REWARD_QUEST_TYPE_MATERIAL in g_rewardQuestLoader.getQuestDatas()[ bigType ].keys():
				dailyMaterialQuest = g_rewardQuestLoader.getQuestDataFromLevelAndType( bigType, csdefine.REWARD_QUEST_TYPE_MATERIAL, self.getLevel() )
			if csdefine.REWARD_QUEST_TYPE_SPACE_COPY in g_rewardQuestLoader.getQuestDatas()[ bigType ].keys():
				dailySpaceCopyQuest = g_rewardQuestLoader.getQuestDataFromLevelAndType( bigType, csdefine.REWARD_QUEST_TYPE_SPACE_COPY, self.getLevel() )
			if dailyQuestNum == 1:
				for questItem in questList:
					if questItem[1] == csdefine.REWARD_QUEST_TYPE_CRUSADE:
						dailyCrusadeQuest = []
					elif questItem[1] == csdefine.REWARD_QUEST_TYPE_MATERIAL:
						dailyMaterialQuest = []
					elif questItem[1] == csdefine.REWARD_QUEST_TYPE_SPACE_COPY:
						dailySpaceCopyQuest = []
			questList = dailyCrusadeQuest + dailyMaterialQuest + dailySpaceCopyQuest
			if dailyQuestNum >= len( questList ):
				quest = questList
			else:
				quest = random.sample( questList, dailyQuestNum )
			for questID in quest:
				if questID in dailyCrusadeQuest:
					totalQuestList.append( ( bigType, csdefine.REWARD_QUEST_TYPE_CRUSADE, questID ) )
				elif questID in dailyMaterialQuest:
					totalQuestList.append( ( bigType, csdefine.REWARD_QUEST_TYPE_MATERIAL, questID ) )
				elif questID in dailySpaceCopyQuest:
					totalQuestList.append( ( bigType, csdefine.REWARD_QUEST_TYPE_SPACE_COPY, questID ) )
		return totalQuestList
		
	def assignQuestQuality( self, questList, refreshType, greenQualityNum ):
		"""
		����������������б����Ʒ�ʵ����
		"""
		whiteProbility = 0.0
		blueProbility = 0.0
		purpleProbility = 0.0
		greenProbility = 0.0
		minNum = 0
		maxNum = 0
		rewardQuestTypeList = []
		if refreshType == csdefine.REWARD_QUEST_SYSTEM_REFRESH:
			whiteProbility = g_rewardQuestLoader.getSystemProbilityData()[ "white" ]
			blueProbility = g_rewardQuestLoader.getSystemProbilityData()[ "blue" ]
			purpleProbility = g_rewardQuestLoader.getSystemProbilityData()[ "purple" ]
			greenProbility = g_rewardQuestLoader.getSystemProbilityData()[ "green" ]
			minNum = g_rewardQuestLoader.getSystemProbilityData()[ "minNum" ]
			maxNum = g_rewardQuestLoader.getSystemProbilityData()[ "maxNum" ]
			pass
		elif refreshType == csdefine.REWARD_QUEST_LOW_ITEM_REFRESH:
			whiteProbility = g_rewardQuestLoader.getLowItemProbilityData()[ "white" ]
			blueProbility = g_rewardQuestLoader.getLowItemProbilityData()[ "blue" ]
			purpleProbility = g_rewardQuestLoader.getLowItemProbilityData()[ "purple" ]
			greenProbility = g_rewardQuestLoader.getLowItemProbilityData()[ "green" ]
			minNum = g_rewardQuestLoader.getLowItemProbilityData()[ "minNum" ]
			maxNum = g_rewardQuestLoader.getLowItemProbilityData()[ "maxNum" ]
			pass
		elif refreshType == csdefine.REWARD_QUEST_HIGH_ITEM_REFRESH:
			whiteProbility = g_rewardQuestLoader.getHighItemProbilityData()[ "white" ]
			blueProbility = g_rewardQuestLoader.getHighItemProbilityData()[ "blue" ]
			purpleProbility = g_rewardQuestLoader.getHighItemProbilityData()[ "purple" ]
			greenProbility = g_rewardQuestLoader.getHighItemProbilityData()[ "green" ]
			minNum = g_rewardQuestLoader.getHighItemProbilityData()[ "minNum" ]
			maxNum = g_rewardQuestLoader.getHighItemProbilityData()[ "maxNum" ]
		start = 0
		node1 = whiteProbility
		node2 = node1 + blueProbility
		node3 = node2 + purpleProbility
		node4 = node3 + greenProbility
		copyQuestList = copy.deepcopy( questList )
		if minNum != 0 or maxNum != 0:
			if minNum != 0:																#���ٲ������ٸ���ɫƷ�ʵ�����
				self.assignMinNumQuestQuality( questList, minNum - greenQualityNum, node1, node2, node3, node4 )
			elif maxNum != 0:															#���������ٸ���ɫƷ�ʵ�����,�ȴ��ܵ�������ѡ���maxNum����������Ȼ���ո��ʶ�ÿ�����������ɫƷ��
				self.assignMinNumQuestQuality( questList, maxNum - greenQualityNum, node1, node2, node3, greenProbility )
		pass
		
	def assignMaxNumQuestQuality( self, questList, maxNum, node1, node2, node3, greenProbility ):
		"""
		��������ж��ٸ���ɫƷ������
		"""
		copyQuestList = copy.deepcopy( questList )
		if maxNum > len( questList ):
			quest = questList
		elif maxNum >= 0:
			quest = random.sample( questList, maxNum )
		elif maxNum < 0:
			quest = []
		for questItem in quest:
			randomNum = random.random()
			if randomNum >= 0 and randomNum < greenProbility:
				e = RewardQuestTypeImpl()
				e.setQuality( csdefine.REWARD_QUEST_QUALITY_GREEN )
				e.setBigType( questItem[0] )
				e.setSmallType( questItem[1] )
				e.setQuestID( questItem[2] )
				e.reset()
				self.set( "rewardQuestQuality_%i"%int( questItem[2] ), csdefine.REWARD_QUEST_QUALITY_GREEN )
				questInstance = self.getQuest( questItem[2] )
				if questInstance:
					e.setRewardsDetail( questInstance.getRewardDetailFromRewardQuest( self ) )
					if questInstance.getStyle() == csdefine.QUEST_STYLE_RANDOM:
						title = questInstance.getGroupQuest().getTitle()
					else:
						title = questInstance.getTitle()
					e.setTitle( title )
				copyQuestList.remove( questItem )
				self.canAcceptRewardQuestRecord.append( e )
		for questItem in copyQuestList:
			randomNum = random.random()
			e = RewardQuestTypeImpl()
			e.setBigType( questItem[0] )
			e.setSmallType( questItem[1] )
			e.setQuestID( questItem[2] )
			e.reset()
			if randomNum >= 0 and randomNum < node1:
				e.setQuality( csdefine.REWARD_QUEST_QUALITY_WHITE )
				self.set( "rewardQuestQuality_%i"%int( questItem[2] ), csdefine.REWARD_QUEST_QUALITY_WHITE )
			elif randomNum >= node1 and randomNum < node2:
				e.setQuality( csdefine.REWARD_QUEST_QUALITY_BLUE )
				self.set( "rewardQuestQuality_%i"%int( questItem[2] ), csdefine.REWARD_QUEST_QUALITY_BLUE )
			elif randomNum >= node2 and randomNum < node3:
				e.setQuality( csdefine.REWARD_QUEST_QUALITY_PURPLE )
				self.set( "rewardQuestQuality_%i"%int( questItem[2] ), csdefine.REWARD_QUEST_QUALITY_PURPLE )
			questInstance = self.getQuest( questItem[2] )
			if questInstance:
				e.setRewardsDetail( questInstance.getRewardDetailFromRewardQuest( self ) )
				if questInstance.getStyle() == csdefine.QUEST_STYLE_RANDOM:
					title = questInstance.getGroupQuest().getTitle()
				else:
					title = questInstance.getTitle()
				e.setTitle( title )
			self.canAcceptRewardQuestRecord.append( e )
		pass
	
	def assignMinNumQuestQuality( self, questList, minNum, node1, node2, node3, node4 ):
		"""
		���������ж��ٸ���ɫƷ������
		"""
		copyQuestList = copy.deepcopy( questList )
		if minNum > len( questList ):
			quest = questList
		elif minNum >= 0:
			quest = random.sample( questList, minNum )
		elif minNum < 0:
			quest = []
		for questItem in quest:
			e = RewardQuestTypeImpl()
			e.setQuality( csdefine.REWARD_QUEST_QUALITY_GREEN )
			e.setBigType( questItem[0] )
			e.setSmallType( questItem[1] )
			e.setQuestID( questItem[2] )
			e.reset()
			self.set( "rewardQuestQuality_%i"%int( questItem[2] ), csdefine.REWARD_QUEST_QUALITY_GREEN )
			questInstance = self.getQuest( questItem[2] )
			if questInstance:
				e.setRewardsDetail( questInstance.getRewardDetailFromRewardQuest( self ) )
				if questInstance.getStyle() == csdefine.QUEST_STYLE_RANDOM:
					title = questInstance.getGroupQuest().getTitle()
				else:
					title = questInstance.getTitle()
				e.setTitle( title )
			copyQuestList.remove( questItem )
			self.canAcceptRewardQuestRecord.append( e )
		for questItem in copyQuestList:
			randomNum = random.random()
			e = RewardQuestTypeImpl()
			e.setBigType( questItem[0] )
			e.setSmallType( questItem[1] )
			e.setQuestID( questItem[2] )
			e.reset()
			if randomNum >= 0 and randomNum < node1:
				e.setQuality( csdefine.REWARD_QUEST_QUALITY_WHITE )
				self.set( "rewardQuestQuality_%i"%int( questItem[2] ), csdefine.REWARD_QUEST_QUALITY_WHITE )
			elif randomNum >= node1 and randomNum < node2:
				e.setQuality( csdefine.REWARD_QUEST_QUALITY_BLUE )
				self.set( "rewardQuestQuality_%i"%int( questItem[2] ), csdefine.REWARD_QUEST_QUALITY_BLUE )
			elif randomNum >= node2 and randomNum < node3:
				e.setQuality( csdefine.REWARD_QUEST_QUALITY_PURPLE )
				self.set( "rewardQuestQuality_%i"%int( questItem[2] ), csdefine.REWARD_QUEST_QUALITY_PURPLE )
			elif randomNum >= node3 and randomNum <= node4:
				e.setQuality( csdefine.REWARD_QUEST_QUALITY_GREEN )
				self.set( "rewardQuestQuality_%i"%int( questItem[2] ), csdefine.REWARD_QUEST_QUALITY_GREEN )
			questInstance = self.getQuest( questItem[2] )
			if questInstance:
				e.setRewardsDetail( questInstance.getRewardDetailFromRewardQuest( self ) )
				if questInstance.getStyle() == csdefine.QUEST_STYLE_RANDOM:
					title = questInstance.getGroupQuest().getTitle()
				else:
					title = questInstance.getTitle()
				e.setTitle( title )
			self.canAcceptRewardQuestRecord.append( e )
		pass
		
	def isNeedRefresh( self ):
		"""
		�ж��Ƿ���Ҫˢ�£���Ҫ����True������Ҫ����False
		"""
		timeDatas = sorted( g_rewardQuestLoader.getTimeDataFromToday() )
		currentTime = time.time()
		day = time.localtime()[2]
		lastSpawnTime = self.rewardQuestLog[ "startTime" ]
		lastSpawnDay = time.localtime( self.rewardQuestLog[ "startTime" ] )[2]
		timeLength = len( timeDatas )
		index = -1
		t = time.localtime()
		todayEndTime = time.mktime( ( t[0], t[1], t[2], Const.ONE_DAY_HOUR, 0, 0, t[6], t[7], t[8] ) )
		todayStartTime = time.mktime( ( t[0], t[1], t[2], 0, 0, 0, t[6], t[7], t[8] ) )
		for times in timeDatas:
			if currentTime < times:
				index = timeDatas.index( times )
		if lastSpawnDay == day:
			if currentTime < todayEndTime and currentTime >= timeDatas[ timeLength - 1 ]:							#ͬһ�죬����ʱ����ڵ������һ��ʱ��㣬С��24��
				if lastSpawnTime < todayEndTime and lastSpawnTime >= timeDatas[ timeLength - 1 ]:		#��һ��ˢ��ʱ����ڵ������һ��ʱ��㣬С��24��
					#����ˢ�£�ֱ�ӽ����ݷ��͸��ͻ���
					return False
				elif lastSpawnTime < timeDatas[ timeLength - 1 ]:											#��һ��ˢ��ʱ��С�����һ��ʱ���
					return True
			elif currentTime < timeDatas[ timeLength - 1 ] and currentTime >= timeDatas[ 0 ]:								#����ʱ��С�����һ��ʱ��㣬���ڵ��ڵ�һ��ʱ��㣬��ôindex�϶����ҵ�������Ϊ-1
				if index != -1:																				#���index���ҵ���Ϊ�˴������������������һ�жϣ�
					if lastSpawnTime < timeDatas[ index ] and lastSpawnTime >= timeDatas[ index - 1 ]:		#�����һ��ˢ��ʱ��Ҳ�������Χ�ڣ��Ͳ���ˢ��
						#����ˢ�£�ֱ�ӽ����ݷ��͸��ͻ���
						return False
					elif lastSpawnTime < timeDatas[ index - 1 ]:					#�����һ��ˢ��ʱ�䲻�������Χ�ڣ���Ҫˢ�£���Ϊ��һ��ʱ���϶�������ʱ��ҪС�������жϴ���timeDatas[ index ]�������
						return True
			elif currentTime < timeDatas[ 0 ]:											#�������ʱ��С�ڵ�һ��ʱ��㣬����һ��ҲС�����ʱ��㣬����ͬһ�첻��ˢ��
				#����ˢ�£�ֱ�ӽ����ݷ��͸��ͻ���
				return False
		elif lastSpawnDay != day and day - lastSpawnDay == 1 :														#���һ��
			if lastSpawnTime < todayStartTime and lastSpawnTime >= timeDatas[ timeLength - 1 ] - Const.ONE_DAY_HOUR * 3600:			#��һ��ˢ��ʱ����ڵ���ǰһ������һ��ʱ��㣬С��ǰһ��24��
				if currentTime < timeDatas[ 0 ]:																	#����ʱ��С�ڵ�һ��ʱ��㣬˵����������һ������һ��ʱ��㵽�����һ��ʱ���֮��
					#����ˢ�£�ֱ�ӽ����ݷ��͸��ͻ���
					return False
				elif currentTime >= timeDatas[ 0 ]:																	#����ʱ����ڵ��ڵ�һ��ʱ��㣬˵�����ڲ�ͬʱ��η�Χ
					return True
			elif lastSpawnTime < timeDatas[ timeLength - 1 ] - Const.ONE_DAY_HOUR * 3600:					#��һ��ˢ��ʱ��С��ǰһ�����һ��ʱ��㣬˵������ʱ����ϴ�ˢ��ʱ�䲻��һ��ʱ��η�Χ��
				return True
		elif day - lastSpawnDay > 1 :																			#��һ��ˢ��ʱ�������ʱ�������������һ�죬��Ҫ����ˢ��
			return True
		
	def rewardQuestAccept( self, srcEntityID, questID ):
		"""
		Exposed method.
		������������
		@param srcEntityID���������͹����ĵ�����id
		@type srcEntityID:	OBJECT_ID
		@param questID��	����ID
		@type questID:		INT32
		"""
		if srcEntityID != self.id:
			return
		quest = self.getQuest( questID )
		if not quest:
			return
		if self.questIsCompleted( questID ):
			return
		quest.acceptRewardQuest( self )
		pass
		
	def rewardQuestAdd( self, quest, tasks ):
		"""
		@param quest: ����ʵ��
		@type  quest: Quest
		@param tasks: ���������������ʵ����
		@type  tasks: QuestDataType
		@return: None
		"""
		if self.rewardQuestLog[ "degree" ] >= csdefine.REWARD_QUEST_CAN_ACCEPT_NUM:
			self.client.onStatusMessage( csstatus.REWARD_QUEST_CAN_ACCEPTED_IS_FULL, "" )
		questID = quest.getID()
		self.questsTable.add( questID, tasks )
		quest.sendQuestLog( self, tasks )
		startTime = self.rewardQuestLog[ "startTime" ]
		degree = self.rewardQuestLog[ "degree" ] + 1
		self.rewardQuestLog = { "startTime":startTime, "degree":degree }
		self.acceptedRewardQuestRecord.append( questID )
		#quality = self.getRewardQuestQuality( questID )
		#self.set( "rewardQuestQuality_%i"%int( questID ), quality )
		#������������״̬֪ͨ,״̬����ѽ���
		DEBUG_MSG( "rewardQuest degree is %s,questID is %s,player id is %s"%( degree, questID, self.id ) )
		self.client.sendRewardQuestState( questID, csdefine.REWARD_QUEST_ACCEPT, self.rewardQuestLog[ "degree" ] )

		tasksDict = tasks.getTasks()
		for i, taskInst in tasksDict.iteritems():
			taskType = taskInst.getType()
			if taskType in [csdefine.QUEST_OBJECTIVE_DELIVER, csdefine.QUEST_OBJECTIVE_EVENT_TRIGGER, csdefine.QUEST_OBJECTIVE_KILL]:
				self.onQuestBoxStateUpdate()
			if taskType == csdefine.QUEST_OBJECTIVE_PET_ACT:
				self.questPetActChanged()
		
		try:
			g_logger.acceptQuestLog( self.databaseID, self.getName(), questID, self.level, self.grade ) 
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )
		
	def isRewardQuest( self, questID ):
		"""
		�ж��Ƿ�����������
		"""
		for record in self.canAcceptRewardQuestRecord:
			if questID == record.getQuestID():
				return True
		return False
		
	def sendRewardQuestDatas( self, nextRefreshTime, degree ):
		"""
		��ͻ��˷���������������
		"""
		#acceptedRewardQuestList = []
		#for record in self.canAcceptRewardQuestRecord:
		#	questID = record.getQuestID()
		#	if questID in self.questsTable.keys():
		#		acceptedRewardQuestList.append( questID )
		acceptedRewardQuestList = list( self.acceptedRewardQuestRecord )
		self.client.receiveRewardQuestDatas( self.canAcceptRewardQuestRecord, acceptedRewardQuestList, self.completedRewardQuestRecord, nextRefreshTime, degree )
		
	def getRewardQuestQuality( self, questID ):
		"""
		�������������Ʒ��
		"""
		for record in self.canAcceptRewardQuestRecord:
			if questID == record.getQuestID():
				return record.getQuality()
		return csdefine.REWARD_QUEST_QUALITY_WHITE
		
	def useItemRefreshRewardQuest( self, srcEntityID ):
		"""
		Exposed method
		����Ʒˢ����������
		"""
		lowItemID  = csconst.REWARD_QUEST_LOW_ITEM
		highItemID  = csconst.REWARD_QUEST_HIGH_ITEM
		lowItems = self.findItemsByIDFromNKCK( lowItemID )
		highItems = self.findItemsByIDFromNKCK( highItemID )
		if lowItems:
			if self.iskitbagsLocked():
				self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
				return
			item = lowItems[0]
			item.use( self,self ) #��Ϊuse���������е���checkUse���м�飬�����ݲ���飬ֱ��ʹ��
		else:
			if highItems:
				if self.iskitbagsLocked():
					self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
					return
				item = highItems[0]
				item.use( self,self ) #��Ϊuse���������е���checkUse���м�飬�����ݲ���飬ֱ��ʹ��

	def getQuestRewardSlots( self, exposed, questID, rewardIndex, codeStr, questTargetID, useGold ):
		"""
		Exposed method
		�����������������ϻ�����
		@useGold bool �Ƿ�ʹ��Ԫ��
		"""
		multiple = random.random.choice( [1, 3, 5] )
		
		#֪ͨ�ͻ������ɽ��
		self.client.setQuestRewardSlots( multiple )
		
		if useGold:
			multiple += 1
		
		#��������������
		tkey = Const.QUEST_SLOTS_MULTIPLE_KEY % questID
		self.setTemp( tkey, multiple )
		
		#�������
		self.questChooseReward( self.id, questID, rewardIndex, codeStr, questTargetID )
	
	def getQuestSlotsMultiple( self, questID ):
		"""
		ȡ���ϻ����Ľ�������
		"""
		tkey = Const.QUEST_SLOTS_MULTIPLE_KEY % questID
		multiple = self.queryTemp( tkey, 1 )
		return multiple
	
	def removeQuestSlotsInfo( self, questID ):
		"""
		ɾ��������ϻ�����ʱ��Ϣ
		"""
		tkey = Const.QUEST_SLOTS_MULTIPLE_KEY % questID
		self.removeTemp( tkey )