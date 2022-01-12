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
	帮会活动的接口
	"""
	def __init__( self ):
		# 帮会活动最后申请时间（每天只能申请一次）这个值不保存，如果服务器重启则可继续申请活动，
		# 重启属于意外事件, 该活动申请需要一定付出，因此不会破坏平衡.
		self.lastCampaignMonsterRaidData = 0
		self.campaignMonsterRaidTimerID = 0	# 帮会活动 魔物来袭 时间TIMERID

	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		if cbID == csdefine.MONSTER_RAID_TIME_OUT_CBID :
			self.onCampaignMonsterRaidTimer()
			self.campaignMonsterRaidTimerID = 0

#---------------------------------------------------------------
# 魔物来袭相关
#---------------------------------------------------------------
	def startCampaign_monsterRaid( self, memberDBID, monsterLevel ):
		"""
		define method.
		申请开始帮会 魔物来袭 活动
		@param monsterLevel: 玩家所选择此次怪物的级别
		"""
		if not memberDBID in self._onlineMemberDBID:
			return

		# 级别不正常 不给予回应， 可能作弊了
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
		elif not self.checkMemberDutyRights( self.getMemberInfos( memberDBID ).getGrade(), csdefine.TONG_RIGHT_ACTIVITY ): # 权限检测
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
		# self.territoryMB 在这里一定不可能为NONE， 因为玩家在领地中申请的活动
		self.territoryMB.startCampaign_monsterRaid( monsterLevel )
		self.territoryMB.cell.startCampaign_monsterRaid()	# 通知cell开启魔物来袭

		self.campaignMonsterRaidTimerID = self.addTimer( 15 * 60, 0, csdefine.MONSTER_RAID_TIME_OUT_CBID )
		self.statusMessageToOnlineMember( csstatus.TONG_CAMPAIGN_START )

		try:
			g_logger.actJoinLog( csdefine.ACTIVITY_TONG_CAMPAIGN, csdefine.ACTIVITY_JOIN_TONG, self.databaseID, self.getName() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def onCampaignMonsterRaidTimer( self ):
		"""
		魔物来袭 活动时间到事件
		"""
		# self.territoryMB 在这里一定不可能为NONE， 因为玩家在领地中申请的活动
		# 即使重启机器， 活动已经失效 也不会走到这里来
		self.territoryMB.overCampaign_monsterRaid()
		self.territoryMB.cell.endCampaign_monsterRaid()		# 通知cell魔物来袭结束
		self.statusMessageToOnlineMember( csstatus.TONG_CAMPAIGN_OVER )

	def onCappaign_monsterRaidComplete( self ):
		"""
		define method.
		魔物来袭 活动帮会已经完成
		"""
		self.territoryMB.cell.endCampaign_monsterRaid()		# 通知cell魔物来袭结束
		if self.campaignMonsterRaidTimerID > 0:
			self.delTimer( self.campaignMonsterRaidTimerID )
		self.addExp( csconst.TONG_EXP_REWARD_MONSTERRAED, csdefine.TONG_CHANGE_EXP_MONSTER_RAID )
		self.statusMessageToOnlineMember( csstatus.TONG_CAMPAIGN_OVER )
		
#----------------------------------------------------------------------------
# 帮会赛马相关
#----------------------------------------------------------------------------
	def requestCreateTongRace( self, playerBase ):
		"""
		define method
		请求开帮会赛马
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
		赛马结束
		"""
		self.addExp( csconst.TONG_EXP_REWARD_RACE, csdefine.TONG_CHANGE_EXP_RACE )
		
#---------------------------------------------------------------------------
# 帮会运镖相关
#---------------------------------------------------------------------------
	def openTongDartQuest( self, playerBase ):
		"""
		define method
		开启帮会运镖任务
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
# 帮会日常任务相关
#---------------------------------------------------------------------------
	def openTongNormalQuest( self, playerBase, type ):
		"""
		define method
		开启帮会日常任务
		@param : type UINT8 帮会日常子任务类型
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
		加入或者登陆帮会时初始化运镖和日常任务开启状态
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
		重置帮会任务: 帮会运镖、帮会日常
		"""
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			emb.cell.onDartQuestStatusChange( False )
			emb.cell.onNormalQuestStatusChange( 0 )

# $Log: not supported by cvs2svn $
#