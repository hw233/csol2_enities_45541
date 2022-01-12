# -*- coding: gb18030 -*-
#
# $Id: SpaceFace.py,v 1.10 2007-09-24 07:38:39 kebiao Exp $

import time
import BigWorld
from bwdebug import *
from MsgLogger import g_logger
import csconst
import csstatus
import csdefine

class TongCampaign:
	"""
	����Ľӿ�
	"""
	def __init__( self ):
		# ����������ʱ�䣨ÿ��ֻ������һ�Σ����ֵ�����棬���������������ɼ���������
		# �������������¼�, �û������Ҫһ����������˲����ƻ�ƽ��.
		self.lastCampaignMonsterRaidData = 0
		self.campaignMonsterRaidTimerID = 0	# ��� ħ����Ϯ ʱ��TIMERID

	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		if cbID == csdefine.MONSTER_RAID_TIME_OUT_CBID :
			self.onCampaignMonsterRaidTimer()
			self.campaignMonsterRaidTimerID = 0

#---------------------------------------------------------------
# ħ����Ϯ���
#---------------------------------------------------------------
	def startCampaign_monsterRaid( self, memberDBID, monsterLevel ):
		"""
		define method.
		���뿪ʼ��� ħ����Ϯ �
		@param monsterLevel: �����ѡ��˴ι���ļ���
		"""
		if not memberDBID in self._onlineMemberDBID:
			return

		# �������� �������Ӧ�� ����������
		if not monsterLevel in [ 50, 70, 90, 110, 130, 150,	]:
			return

		member = self.getMemberInfos( memberDBID ).getBaseMailbox()
		t = time.localtime()
		tdata = t[0] + t[1] + t[2]
		
		

		if self.level < 2 :
			self.statusMessage( member, csstatus.TONG_CAMPAIGN_LEVEL_INVALID )
			return		
		elif self.lastCampaignMonsterRaidData == tdata :
			self.statusMessage( member, csstatus.TONG_CAMPAIGN_COUNT_INVALID )
			return
		elif not self.checkMemberDutyRights( self.getMemberInfos( memberDBID ).getGrade(), csdefine.TONG_RIGHT_ACTIVITY ): # Ȩ�޼��
			self.statusMessage( member, csstatus.TONG_GRADE_INVALID )
			return
		elif self.shenshouType <= 0 or self.shenshouReviveTime > 0:
			self.statusMessage( member, csstatus.TONG_NAGUAL_DEAD_ACTION_FAILED )
			return
		elif self.getValidMoney() < csconst.TONG_MONSTERRAID_REQUEST_MONEY:
			self.statusMessage( member, csstatus.TONG_OPEN_ACT_MONEY_LACK )
			return

		self.payMoney( csconst.TONG_MONSTERRAID_REQUEST_MONEY, True, csdefine.TONG_CHANGE_MONEY_REQUEST_MONSTER_RAID  )
		self.lastCampaignMonsterRaidData = tdata
		# self.territoryMB ������һ��������ΪNONE�� ��Ϊ��������������Ļ
		self.territoryMB.startCampaign_monsterRaid( monsterLevel )
		self.territoryMB.cell.startCampaign_monsterRaid()	# ֪ͨcell����ħ����Ϯ

		self.campaignMonsterRaidTimerID = self.addTimer( 15 * 60, 0, csdefine.MONSTER_RAID_TIME_OUT_CBID )
		self.statusMessageToOnlineMember( csstatus.TONG_CAMPAIGN_START )

		try:
			g_logger.actJoinLog( csdefine.ACTIVITY_TONG_CAMPAIGN, csdefine.ACTIVITY_JOIN_TONG, self.databaseID, self.getName() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def onCampaignMonsterRaidTimer( self ):
		"""
		ħ����Ϯ �ʱ�䵽�¼�
		"""
		# self.territoryMB ������һ��������ΪNONE�� ��Ϊ��������������Ļ
		# ��ʹ���������� ��Ѿ�ʧЧ Ҳ�����ߵ�������
		self.territoryMB.overCampaign_monsterRaid()
		self.territoryMB.cell.endCampaign_monsterRaid()		# ֪ͨcellħ����Ϯ����
		self.statusMessageToOnlineMember( csstatus.TONG_CAMPAIGN_OVER )

	def onCappaign_monsterRaidComplete( self ):
		"""
		define method.
		ħ����Ϯ �����Ѿ����
		"""
		self.territoryMB.cell.endCampaign_monsterRaid()		# ֪ͨcellħ����Ϯ����
		if self.campaignMonsterRaidTimerID > 0:
			self.delTimer( self.campaignMonsterRaidTimerID )
		self.addExp( csconst.TONG_EXP_REWARD_MONSTERRAED, csdefine.TONG_CHANGE_EXP_MONSTER_RAID )
		self.statusMessageToOnlineMember( csstatus.TONG_CAMPAIGN_OVER )
		
#----------------------------------------------------------------------------
# ����������
#----------------------------------------------------------------------------
	def requestCreateTongRace( self, playerBase ):
		"""
		define method
		���󿪰������
		"""
		timeTuple = time.localtime()
		day = str( timeTuple[0] ) + str( timeTuple[1] ) + str( timeTuple[2] )
		if self.lastCreateTongRaceTime == day:
			playerBase.client.onStatusMessage( csstatus.ROLE_HAS_CREATE_TONG_RACE_TODAY, "" )
			return
		if self.getValidMoney() < csconst.TONG_RACE_REQUEST_MONEY:
			playerBase.client.onStatusMessage( csstatus.TONG_OPEN_ACT_MONEY_LACK, "" )
			return
			
		self.lastCreateTongRaceTime = day
		self.payMoney( csconst.TONG_RACE_REQUEST_MONEY, True, csdefine.TONG_CHANGE_MONEY_REQUEST_RACE  )
		self.statusMessageToOnlineMember( csstatus.TONG_OPEN_RACE_HORSE )
		playerBase.client.onStatusMessage( csstatus.TONG_ACT_OPEN_SUCCESS, "" )
		BigWorld.globalData['RacehorseManager'].createTongRace( playerBase, self.databaseID )
	
	def onTongRaceOver( self ):
		"""
		define method
		�������
		"""
		self.addExp( csconst.TONG_EXP_REWARD_RACE, csdefine.TONG_CHANGE_EXP_RACE )
		
#---------------------------------------------------------------------------
# ����������
#---------------------------------------------------------------------------
	def openTongDartQuest( self, playerBase ):
		"""
		define method
		���������������
		"""
		timeTuple = time.localtime()
		day = str( timeTuple[0] ) + str( timeTuple[1] ) + str( timeTuple[2] )
		if self.lastOpenTongDartQuestTime == day:
			playerBase.client.onStatusMessage( csstatus.TONG_HAS_OPEN_TONG_DART_QUEST, "" )
			return
		if self.getValidMoney() < csconst.TONG_OPEN_DART_QUEST_REQUEST_MONEY:
			playerBase.client.onStatusMessage( csstatus.TONG_OPEN_ACT_MONEY_LACK, "" )
			return
		
		self.lastOpenTongDartQuestTime = day
		self.payMoney( csconst.TONG_OPEN_DART_QUEST_REQUEST_MONEY, True, csdefine.TONG_CHANGE_MONEY_OPEN_DART_QUEST  )
		playerBase.client.onStatusMessage( csstatus.TONG_ACT_OPEN_SUCCESS, "" )
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			emb.cell.onDartQuestStatusChange( True )

#---------------------------------------------------------------------------
# ����ճ��������
#---------------------------------------------------------------------------
	def openTongNormalQuest( self, playerBase, type ):
		"""
		define method
		��������ճ�����
		@param : type UINT8 ����ճ�����������
		"""
		timeTuple = time.localtime()
		day = str( timeTuple[0] ) + str( timeTuple[1] ) + str( timeTuple[2] )
		lastOpenDay = self.lastOpenTongNormalQuestTime.split("_")[0]
		if lastOpenDay == day:
			playerBase.client.onStatusMessage( csstatus.TONG_HAS_OPEN_TONG_NORMAL_QUEST, "" )
			return
		if self.getValidMoney() < csconst.TONG_OPEN_NORMAL_QUEST_REQUEST_MONEY:
			playerBase.client.onStatusMessage( csstatus.TONG_OPEN_ACT_MONEY_LACK, "" )
			return
		
		self.lastOpenTongNormalQuestTime = day + "_" + str( type )
		self.payMoney( csconst.TONG_OPEN_NORMAL_QUEST_REQUEST_MONEY, True, csdefine.TONG_CHANGE_MONEY_OPEN_NORMAL_QUEST  )
		playerBase.client.onStatusMessage( csstatus.TONG_ACT_OPEN_SUCCESS, "" )
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			emb.cell.onNormalQuestStatusChange( type )
		
	def initTongQuestState( self, mb ):
		"""
		������ߵ�½���ʱ��ʼ�����ں��ճ�������״̬
		"""
		timeTuple = time.localtime()
		day = str( timeTuple[0] ) + str( timeTuple[1] ) + str( timeTuple[2] )
		if self.lastOpenTongDartQuestTime == day:
			mb.cell.onDartQuestStatusChange( True )
		if self.lastOpenTongNormalQuestTime.split("_")[0] == day:
			type = int( self.lastOpenTongNormalQuestTime.split("_")[1] )
			mb.cell.onNormalQuestStatusChange( type )
		
	def resetTongQuest( self ):
		"""
		define method
		���ð������: ������ڡ�����ճ�
		"""
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			emb.cell.onDartQuestStatusChange( False )
			emb.cell.onNormalQuestStatusChange( 0 )

# $Log: not supported by cvs2svn $
#