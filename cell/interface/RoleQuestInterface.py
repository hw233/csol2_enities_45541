# -*- coding: gb18030 -*-
#
# $Id: RoleQuestInterface.py,v 1.93 2008-09-05 01:40:40 zhangyuxing Exp $

"""
任务系统 for Role 部份
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
from Resource.RewardQuestLoader import RewardQuestLoader		# 悬赏任务配置
g_rewardQuestLoader = RewardQuestLoader.instance()

DISTANCE_FOR_PLAYER_TAKE_SLAVE	= 20						#在多大距离内，玩家携带镖车一起过传送门

class RoleRandomQuestInterface:
	"""
	随机任务接口
	"""
	def __init__( self ):
		pass


	def addSubQuestCount( self, questID, count):
		"""
		设置随机组进行次数
		@type	questID: QUESTID
		@param  count:	组任务次数增加
		@type	count:	INT
		"""
		self.questsRandomLog.addCount( questID, count )

	def setSubQuestCount( self, questID, count):
		"""
		设置随机组进行次数
		@type	questID: QUESTID
		@param  count:	组任务次数增加
		@type	count:	INT
		"""
		if self.questsRandomLog.has_randomQuestGroup( questID ):
			self.questsRandomLog._questsRandomLog[questID].count = count

	def getSubQuestCount( self, questID ):
		"""
		获得单组子任务次数
		@type	questID: QUESTID
		@rtype : INT
		"""
		return self.questsRandomLog.getCount( questID )

	def setSubQTCountRewardRate( self, questID, count, rate ):
		"""
		设置环任务奖励随机概率
		"""
		self.questsRandomLog.setSubQTCountRewardRate( questID, count, rate )

	def getSubQTCountRewardRate( self, questID, count ):
		"""
		获取环任务奖励随机概率
		"""
		return self.questsRandomLog.getSubQTCountRewardRate( questID, count )

	def resetSubQTCountRewardRate( self, questID ):
		"""
		重置环任务奖励随机概率
		"""
		self.questsRandomLog.resetSubQTCountRewardRate( questID )

	def payQuestDeposit( self, questID, deposit ):
		"""
		支付随机任务押金
		@type	questID: QUESTID
		@param 	deposit: 押金增加值
		@type	deposint:int
		"""
		if deposit == 0:return
		self.payMoney( deposit, csdefine.CHANGE_MONEY_PAYQUESTDEPOSIT )
		self.questsRandomLog.addDeposit( questID, deposit )

	def returnDeposit( self, questID ):
		"""
		返回一批随机任务押金
		@type questID: QUESTID
		@rtype : INT
		"""
		deposit = self.questsRandomLog.returnDeposit( questID )
		return self.gainMoney( deposit, csdefine.CHANGE_MONEY_RETURNDEPOSIT )
		#self.statusMessage( csstatus.ROLE_QUEST_DEPOSIT_RETURN )

	def addGroupPoint( self, questID, point ):
		"""
		增加循环积分
		@type questID: QUESTID
		@param point: 积分增加值
		@type  point: INT
		"""
		#--------- 以下为防沉迷系统的判断 --------#
		gameYield = self.wallow_getLucreRate()
		if point >=0:
			point = point * gameYield
		#--------- 以上为防沉迷系统的判断 --------#
		self.questsRandomLog.addPoint( questID, point )

	def takeGroupPoint( self, questID):
		"""
		取走一批随机任务的积分
		@type questID: QUESTID
		@rtype : INT
		"""
		return self.questsRandomLog.takePoint( questID )

	def addRandomLogs( self, questID, record ):
		"""
		增加一项随机任务记录
		@type questID: QUESTID
		"""
		self.questsRandomLog[questID] = record


	def checkStartGroupTime( self, questID ):
		"""
		判断随机任务开始时间是不是今天
		@type questID: QUESTID
		"""
		return self.questsRandomLog.checkStartGroupTime( questID )

	def resetGroupQuest( self, questID ):
		"""
		重置随机组任务
		@type questID: QUESTID
		"""
		self.questsRandomLog.resetGroupQuest( questID )

	def addGroupQuestCount( self, questID ):
		"""
		增加随机组次数
		@type questID: QUESTID
		"""
		self.questsRandomLog.addGroupQuestCount( questID )

	def setGroupQuestCount( self, questID, num):
		"""
		设置随机组次数 for GM
		@type questID: QUESTID
		@type num: INT
		"""
		if self.questsRandomLog.has_randomQuestGroup( questID ):
			self.questsRandomLog._questsRandomLog[questID].degree = num

	def resetSingleGroupQuest( self, questID ):
		"""
		重置随机单组任务
		@type questID: QUESTID
		"""
		self.questsRandomLog.resetSingleGroupQuest( questID )

	def getGroupQuestCount( self, questID ):
		"""
		获得组任务完成次数
		@type questID: QUESTID
		@rtype : INT
		"""
		return self.questsRandomLog.getGroupQuestCount( questID )

	def setGroupCurID( self, questID, subQuestID ):
		"""
		设置随机任务组子任务ID
		@type questID: QUESTID
		@type subQuestID: QUESTID
		"""
		self.questsRandomLog.setGroupCurID( questID, subQuestID )

	def queryGroupCurID( self, questID ):
		"""
		查询当前随机任务组子任务ID
		@type questID: INT
		@rtype : QUESTID
		"""
		return self.questsRandomLog.queryGroupCurID( questID )

	def isGroupQuestRecorded( self, questID ):
		"""
		是否是记录过的组任务
		"""
		return self.questsRandomLog.isGroupQuestRecorded( questID )

	def setGroupQuestRecorded( self, questID, isRecorded ):
		"""
		设置记录过的组任务
		"""
		self.questsRandomLog.setGroupQuestRecorded( questID, isRecorded )

	def recordRandomQuest( self, questID):
		"""
		记录随机任务的信息
		"""
		#从玩家角色身上拿走道具

		if not self.has_randomQuestGroup( questID ):
			self.statusMessage( csstatus.ROLE_QUEST_RANDON_NOT_HAVE )
			return
		self.recordQuestsRandomLog.add( questID, self.questsRandomLog[questID].copy() )
		#self.recordQuestsRandomLog.setGroupQuestRecorded( questID, True )
		self.statusMessage( csstatus.ROLE_QUEST_RANDON_RECORD_SUCCESSED )

	def readRandomQuestRecord( self, srcEntityID, questID ):
		"""
		Exposed method.
		读取随机任务的信息
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

		# 读取随机任务后，删除failedGroupQuestList中记录(存储任务时候，把任务设置为失败)
		dataQuestID = str(time.localtime()[2])+':'+str(questID)
		if dataQuestID in self.failedGroupQuestList:
			self.failedGroupQuestList.remove( dataQuestID )

	def loadGroupQuest( self, questID, subQuestID ):
		"""
		根据组任务ID和子任务ID来加载一个已知任务
		"""
		if self.getQuest( questID ) is None:
			return
		self.getQuest( questID ).loadQuest( self, subQuestID )


	def delRandomQuestRecord( self, questID ):
		"""
		删除一条随机任务记录
		"""
		self.recordQuestsRandomLog.delete( questID )


	def addFailedGroupQuest( self, questID ):
		"""
		增加一个环任务失败记录
		"""
		dataQuestID = str(time.localtime()[2])+':'+str(questID)
		if not (dataQuestID in self.failedGroupQuestList ):
			self.failedGroupQuestList.append( dataQuestID )


	def addSaveQuestRecord( self, questID ):
		"""
		增加一个存储过的任务记录
		注释：
			存储过的任务，玩家隔天恢复任务记录，做完当前环数是，还可以做该天的环数
		"""
		dataQuestID = str(time.localtime()[2])+':'+str(questID)
		if not (dataQuestID in self.savedGroupQuestList ):
			self.savedGroupQuestList.append( dataQuestID )


	def newDataGroupQuest( self, questID ):
		"""
		新一天的环任务
		注释：
			存储过的环任务，在之后的某天做完后，还可以做当天的环任务
		"""
		for i in self.savedGroupQuestList:
			if i.split(':')[1] == str( questID ):
				self.resetGroupQuest( questID )
				self.savedGroupQuestList.remove( questID )
			return True
		return False


	def groupQuestSavedAndFailedProcess( self, questID ):
		"""
		环任务存档管理和失败管理
		注释：
			存档管理包括存储的任务处理和正在做存档任务的处理
		"""
		if not self.recordQuestsRandomLog.has_randomQuestGroup( questID ):
			"""
			如果玩家没有使用道具记录环任务存档，则执行正常的环任务接受流程
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
	运镖任务接口
	"""
	def __init__( self ):
		"""
		"""
		self.addDartActivity()
		#self.resetDartPrestige()
		self.queryAboutDart()

	def isDarting( self ):
		"""
		玩家是否有运镖任务在身
		"""
		return self.hasFlag( csdefine.ROLE_FLAG_XL_DARTING ) or self.hasFlag( csdefine.ROLE_FLAG_CP_DARTING )

	def isRobbing( self ):
		"""
		玩家是否有劫镖任务在身
		"""
		return self.hasFlag( csdefine.ROLE_FLAG_XL_ROBBING ) or self.hasFlag( csdefine.ROLE_FLAG_CP_ROBBING )

	def isRobbingOppose( self, prestige ):
		"""
		玩家是否有对立镖局劫镖任务在身
		"""
		if prestige == csconst.FACTION_CP:
			return self.hasFlag( csdefine.ROLE_FLAG_XL_ROBBING )
		else:
			return self.hasFlag( csdefine.ROLE_FLAG_CP_ROBBING )


	def hasQuestMerchant( self ):
		"""
		玩家是否有跑商任务在身
		"""
		return self.hasFlag( csdefine.ROLE_FLAG_MERCHANT )



	def isRobbingComplete( self ):
		"""
		劫镖任务是否完成
		劫镖任务的完成同其他任务不一样，根据策划的要求，只要在规定时间内狙杀了镖车就算完成
		狙杀镖车后即时规定时间内不交任务，也不算失败
		"""
		for qID in self.questsTable._quests:
			if self.getQuest( qID ).getType() == csdefine.QUEST_TYPE_ROB:
				return self.getQuest( qID ).isCompleted(  self )
		return False

	def isDartingComplete( self ):
		"""
		运镖任务是否完成
		运镖任务的完成同其他任务不一样，根据策划的要求，只要在规定时间内运镖就算完成
		运镖后即时规定时间内不交任务，也不算失败
		"""
		for qID in self.questsTable._quests:
			if self.getQuest( qID ).getType() == csdefine.QUEST_TYPE_DART or self.getQuest( qID ).getType() == csdefine.QUEST_TYPE_MEMBER_DART:
				return self.getQuest( qID ).isCompleted(  self )
		return False

	def onDartActivityStart( self, controllerID, userData ):
		"""
		开始运镖活动
		"""
		self.statusMessage( csstatus.ROLE_QUEST_DART_ACTIVITY_START )
		self.setTemp('dart_activety', True )

	def onDartActivityEnd( self, controllerID, userData ):
		"""
		结束运镖活动
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
			self.addTimer( startTime, 0, ECBExtend.QUEST_DART_ACTIVITY_START_CBID )			#国运活动开始

		if endTime > 0:
			self.addTimer( endTime, 0, ECBExtend.QUEST_DART_ACTIVITY_END_CBID )				#国运活动结束


	def weekTimeMinus( self, w, h, m = 0):
		"""
		返回到达当前周的某一天的某个时间还需要多少秒
		0 是周一
		例如： 周日晚上9点
		weekTimeMinus（ 6, 21 )
		"""
		date = time.localtime()
		return (w-date[6])*24*3600+(h-date[3])*3600+(m-date[4])*60   #gmtime 比我们慢8小时



	def resetDartPrestige( self ):
		"""
		"""
		BigWorld.globalData['DartManager'].requestPlayerDartPrestige( self.getName(), self.base )

	def updateDartPrestige( self, xValue, cValue ):
		"""
		define method

		@param xValue	:兴隆镖局声望值
		@param cValue	:昌平镖局声望值
		"""
		self.setPrestige( csconst.FACTION_XL, xValue )			#兴隆镖局声望
		self.setPrestige( csconst.FACTION_CP, cValue )			#昌平镖局声望

	def handleDartFailed( self ):
		"""
		define method
		处理运镖任务失败表现
		"""
		resultList = self.questsTable.handleDartFailed( self )

		for r in resultList:
			self.onTaskStateChange( r[0], self.questsTable[r[0]]._tasks[r[1]], r[1] )
			self.client.onTaskStateUpdate( r[0], self.questsTable[r[0]]._tasks[r[1]] )


	def queryAboutDart( self ):
		"""
		上线取得镖车信息
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
		判断杀人者和被杀者是否满足劫镖和运镖关系
		"""
		
		# 杀人者有运镖任务
		if killer.isDarting():
			return True
		
		# 杀人者有劫镖任务
		if killer.isRobbing():
			if killer.hasFlag( csdefine.ROLE_FLAG_XL_ROBBING ):
				if self.hasFlag( csdefine.ROLE_FLAG_CP_DARTING ) and killer.level - self.queryTemp( "Dart_level" , self.level ) < csconst.DART_ROB_MIN_LEVEL:		# 杀运镖者
					return True
				elif len(self.queryTemp("attackDartRoleID",[])) != 0 and killer.id in self.queryTemp("attackDartRoleID"):		# 杀运镖者帮会的帮手
					return True
					
			if killer.hasFlag( csdefine.ROLE_FLAG_CP_ROBBING ):
				if self.hasFlag( csdefine.ROLE_FLAG_XL_DARTING ) and killer.level - self.queryTemp( "Dart_level" , self.level ) < csconst.DART_ROB_MIN_LEVEL:
					return True
				elif len(self.queryTemp("attackDartRoleID",[])) != 0 and killer.id in self.queryTemp("attackDartRoleID"):
					return True
		
		# 杀人者没有劫镖任务
		else:
			if self.isDarting():	# 劫野镖的情况
				if killer.level - self.level < csconst.DART_ROB_MIN_LEVEL:
					return True
			if self.isRobbing():
				if len(killer.findBuffsByBuffID( 99029 )) != 0:			# 帮会成员杀劫镖者
					if ( self.hasFlag( csdefine.ROLE_FLAG_CP_ROBBING ) and killer.queryTemp( "TongDart_factionID",0 ) == csdefine.FACTION_XINGLONG )\
						or ( self.hasFlag( csdefine.ROLE_FLAG_XL_ROBBING ) and killer.queryTemp( "TongDart_factionID",0 ) == csdefine.FACTION_CHANGPING ):
							if self.level - killer.queryTemp( "TongDart_level",0 ) < csconst.DART_ROB_MIN_LEVEL:
								return True
			else:
				if len(self.queryTemp("attackDartRoleID",[])) != 0 and killer.id in self.queryTemp("attackDartRoleID"):		# 帮会成员被坏人杀了
					DEBUG_MSG( "Tong member %s(%i) is killed by player %s(%i)" %( self.getName, self.id, killer.getName(), killer.id ) )
					return True
				if len(killer.queryTemp("attackDartRoleID",[])) != 0 and self.id in killer.queryTemp("attackDartRoleID"):		# 坏人被帮会成员杀了
					DEBUG_MSG( "Player %s(%i) is killed by tong member %s(%i)" %( self.getName, self.id, killer.getName(), killer.id ) )
					return True
		
		return False

	def requestTakeToMaster( self, baseMailBox ):
		"""
		define method
		请求到达主人所在位置
		"""
		baseMailBox.cell.onReceiveMasterInfo( self, self.position )

	def dart_spaceDartCountResult( self, count ):
		"""
		Define method.
		当前地图发出镖车数量的结果回调

		@param count : 镖车数量
		@type count : INT16
		"""
		self.setGossipText( self.popTemp( "DartSpaceInfoQuery_talkString", "%s" ) % count )
		self.sendGossipComplete( self.popTemp( "DartSpaceInfoQuery_talkNPCID", self.id ) )

class RoleActivityInterface:
	"""
	活动接口
	"""
	def __init__( self ):
		"""
		"""
		pass

	def moneyToYinpiao( self, money ):
		"""
		"""
		if self.getAllYinpiaoValue() < 0:			# 小于零表示身上没有银票
			self.statusMessage( csstatus.ROLE_YIN_PIAO_NOT_FOUND )
			return
		if self.money < money:
			self.statusMessage( csstatus.ROLE_QUEST_NOT_ENOUGH_MONEY_FOR_CHAGRE_YINPIAO )
			return
		yinpiaoMoney = money * 80 / 100  #充值比例改为1：0.8 by姜毅
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
		有没有跑商任务
		"""
		for i in self.questsTable._quests:
			if self.getQuest( i ).getType() == csdefine.QUEST_TYPE_RUN_MERCHANT:
				return True
		return False

	def getMerchantQuest( self ):
		"""
		获取跑商任务
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
		得到科举回答题目的经验奖励
		"""
		self.addExp( exp, csdefine.CHANGE_EXP_KEJUREWARD )

	def addWuDaoAward( self, round, step, isWinner ):
		"""
		处理武道大会奖励，策划制定奖励CSOL-2656
		"""
		rank = pow( 2, 5 - round )

		if isWinner:
			self.addExp( int( 5 * self.level * pow( 40 - rank, 2.3 ) ), csdefine.CHANGE_EXP_WUDAOAWARD )
			money = int( 0.5 * self.level * pow( 38 - rank, 2.3 ) )
			self.gainMoney( money, csdefine.CHANGE_MONEY_WUDAOAWARD )

			if round == 5: # 第五轮获胜者为第一名
				self.sysBroadcast( cschannel_msgs.CELL_ROLEQUESTINTERFACE_1 %( self.getName(), step*10, step*10+9 ) )
				self.addTitle( 36 )
				awarder = Love3.g_rewards.fetch( csdefine.RCG_WD_FORE_LEVEL, self )
				awarder.award( self, csdefine.ADD_ITEM_ADDWUDAOAWARD )

		else:
			self.addExp( int( 2.5 * self.level * pow( 40 - rank, 2.3 ) ), csdefine.CHANGE_EXP_WUDAOAWARD )
			money = int( 0.25 * self.level * pow( 38 - rank, 2.3 ) )
			self.gainMoney( money,csdefine.CHANGE_MONEY_WUDAOAWARD )

			if round == 5: # 第五轮失败者为第二名
				self.addTitle( 37 )
				awarder = Love3.g_rewards.fetch( csdefine.RCG_WD_THREE_LEVEL , self )
				awarder.award( self, csdefine.ADD_ITEM_ADDWUDAOAWARD )

	def showMerchantQuestFlag( self ):
		"""
		玩家头顶显示跑商标记
		"""
		if not self.hasFlag( csdefine.ROLE_FLAG_MERCHANT ) :
			self.addFlag( csdefine.ROLE_FLAG_MERCHANT )

	def removeMerchantQuestFlag( self ):
		"""
		玩家头顶显示跑商标记
		"""
		if self.hasFlag( csdefine.ROLE_FLAG_MERCHANT ) :
			self.removeFlag( csdefine.ROLE_FLAG_MERCHANT )

	def showBloodItemFlag( self ):
		"""
		玩家头顶显示带血玩家标记
		"""
		if not self.hasFlag( csdefine.ROLE_FLAG_BLOODY_ITEM ) :
			self.addFlag( csdefine.ROLE_FLAG_BLOODY_ITEM )

	def removeBloodItemFlag( self ):
		"""
		玩家头顶显示带血玩家标记
		"""
		if self.hasFlag( csdefine.ROLE_FLAG_BLOODY_ITEM ) :
			self.removeFlag( csdefine.ROLE_FLAG_BLOODY_ITEM )


	def checkTeamInCopySpace( self, mailbox ):
		"""
		检查进入副本的时候是否有队伍
		"""
		if not self.isInTeam():
			self.statusMessage( csstatus.TEAM_NOT_IN_LEAVE_COPY )
			self.leaveTeamTimer = self.addTimer( 120, 0, ECBExtend.LEAVE_TEAM_TIMER )


class TasksNotify:
	"""
	任务通知接口
	"""
	def __init__( self ):
		"""
		"""
		pass

	def updataQuestState( self, resultList ):
		"""
		更新任务数据信息
		"""
		if resultList != []:
			for r in resultList:
				task = self.questsTable[r[0]]._tasks[r[1]]
				self.onTaskStateChange( r[0], task, r[1] )
				self.client.onTaskStateUpdate( r[0], task )
				self.onQuestBoxStateUpdate()

	def questItemAmountChanged( self, item, quantity ):
		"""
		被通知玩家背包有物品被改变

		@param   item: 物品实例
		@type    item: instance
		@param quantity: 数量,正为增加,负为减少
		@type  quantity: INT32
		"""
		r = self.questsTable.addDeliverAmount( self, item, quantity )
		self.updataQuestState( r )
		if cschannel_msgs.CELL_ROLEQUESTINTERFACE_2 in item.name():
			if quantity > 0:
				self.showBloodItemFlag()
			else:
				for item in self.getAllItems() :		# 目前没找到更好的遍历方法
					if cschannel_msgs.CELL_ROLEQUESTINTERFACE_2 in item.name() :
						return
				self.removeBloodItemFlag()

	def onEnterSpace_( self ):
		"""
		进入了新的空间
		"""
		sapceLabel = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		self.updataQuestState( self.questsTable.enterNewSpaceTrigger( self, sapceLabel ) )
	
	def onEnterSpaceAutoNextQuest( self, exposed ):
		"""
		exposed method
		传入地图后，自动打开接任务界面
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
						if e.getScript().questQuery( e, self, nextQuestID ) == csdefine.QUEST_STATE_NOT_HAVE:		# 还没有接该任务
							self.getQuest( nextQuestID ).gossipDetail( self, e )
						break
		
	def questYinpiaoValueChange( self, item ):
		"""
		银票数值发生变化
		"""
		r = self.questsTable.addYinpiaoDeliverAmount( self, item )
		self.updataQuestState( r )


	def questPetEvent( self, eventType ):
		"""
		宠物相关事件

		@param   item: 物品实例
		@type    item: instance
		@param quantity: 数量,正为增加,负为减少
		@type  quantity: INT32
		"""
		r = self.questsTable.addPetEvent( self, eventType )
		self.updataQuestState( r )


	def questPetAmountAdd( self, petClassName, petDBID ):
		"""
		通知玩家宠物加1

		@param   item: 物品实例
		@type    item: instance
		@param quantity: 数量,正为增加,负为减少
		@type  quantity: INT32
		"""
		r = self.questsTable.addDeliverPetAmount( self, petClassName, petDBID )
		self.updataQuestState( r )

	def questPetAmountSub( self, petClassName, petDBID ):
		"""
		通知玩家宠物有减少1

		@param   item: 物品实例
		@type    item: instance
		@param quantity: 数量,正为增加,负为减少
		@type  quantity: INT32
		"""
		r = self.questsTable.subDeliverPetAmount( self, petClassName, petDBID )
		self.updataQuestState( r )


	def questTaskIncreaseState( self, questID, taskIndex ):
		"""
		Define Method.
		被通知指定任务有一个任务事件被完成
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

		#押镖任务成功时需要删掉玩家身上相应的标记 add by chenweilan
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
		通知完成一条科举试题
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
		通知回答问题
		"""
		self.remove( "current_question_id" )
		r = self.questsTable.addNormalAnswerQuestion( self, questionType, isRight )
		self.updataQuestState( r )


	def questTaskFailed( self, questID, taskIndex ):
		"""
		Define Method.
		通知一个事件任务失败
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
		被通知指定任务有一个任务事件失败
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
		被通知有怪物被玩家杀死
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
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
		被通知有镖车被玩家杀死
		"""
		r = self.questsTable.increaseDartKilled( self, dartQuestID, factionID )
		self.updataQuestState( r )

	def questPetActChanged( self ):
		"""
		Define Method.
		被通知宠物的激活状态发生改变
		"""
		r = self.questsTable.updatePetActState( self, self.pcg_hasActPet() )
		self.updataQuestState( r )

	def questMonsterEvoluted( self, className ):
		"""
		Define Method
		被通知有怪物被玩家进化
		"""
		r = self.questsTable.increaseEvolution( self, className )
		self.updataQuestState( r )

	def questSkillLearned( self, skillID ):
		"""
		被通知有技能被玩家学习成功
		"""
		r = self.questsTable.increaseSkillLearned( self, skillID )

		self.updataQuestState( r )

	def questLivingSkillLearned(self, skillID):
		r = self.questsTable.increaseLivingSkillLearned(self, skillID)
		self.updataQuestState( r )

	def questFinishQuest( self, questID ):
		"""
		通知有任务完成
		"""
		r = self.questsTable.questFinish( questID )
		self.updataQuestState( r )

	def questRoleLevelUp( self, level ):
		"""
		等级有变化
		"""
		r = self.questsTable.increaseLevel( level )
		self.updataQuestState( r )

	def questIncreaseItemUsed( self, itemID ):
		"""
		使用物品完成任务,由物品调用。
		"""
		r = self.questsTable.increaseItemUsed( self, itemID )
		self.updataQuestState( r )



	def questPetAmountChange( self, quantity ):
		"""
		增加一个宠物数量
		"""
		r = self.questsTable.addPetAmount( self, quantity )
		self.updataQuestState( r )


	def questTalk( self, targetClassName ):
		"""
		对话完成普通任务的一个任务目标
		"""
		r = self.questsTable.addTalk( self, targetClassName )
		self.updataQuestState( r )


	def questBuffAddOrRemoved( self, buffID, val ):
		"""
		Define Method
		被通知有buff被增加或移除
		"""
		r = self.questsTable.updateBuffState( buffID, val )
		self.updataQuestState( r )


	def questPotentialFinish( self ):
		"""
		完成潜能任务

		@param   item: 物品实例
		@type    item: instance
		@param quantity: 数量,正为增加,负为减少
		@type  quantity: INT32
		"""
		r = self.questsTable.addPotentialFinish( self )
		self.updataQuestState( r )


	def questIncreaseSkillUsed( self, skillID, className ):
		"""
		使用物品完成任务,由物品调用。
		"""
		r = self.questsTable.increaseSkillUsed( self, skillID, className )
		self.updataQuestState( r )


	def questSetRevivePos( self, spaceName ):
		"""
		使用物品完成任务,由物品调用。
		"""
		r = self.questsTable.updateSetRevivePos( self, spaceName )
		self.updataQuestState( r )
		
	def questCampMoraleChange( self, camp, amount ):
		"""
		增加或减少阵营士气
		"""
		r = self.questsTable.onChangeCampMorale( self, camp, amount )
		self.updataQuestState( r )

	def questVehicleActived( self, VehicleID ):
		"""
		激活骑宠任务
		"""
		r = self.questsTable.increaseVehicleActived( self, VehicleID )
		self.updataQuestState( r )

g_quests = QuestsFlyweight.instance()
class RoleQuestInterface( TasksNotify, RoleRandomQuestInterface, RoleDartQuestInterface, RoleActivityInterface ):
	"""
	玩家任务接口
	"""
	def __init__( self ):

		RoleRandomQuestInterface.__init__( self )
		RoleDartQuestInterface.__init__( self )
		RoleActivityInterface.__init__( self )

	def onDestroy( self ):
		"""
		离线时调用
		"""
		self.questClearTeamMember()				# 清理组队信息
		self.questClearFollowNPC()				# 清理护送NPC任务的NPC
		self.handleOffLineQuestEvent()			# 对玩家的任务做下线处理

	def getQuest( self, questID ):
		"""
		根据任务ID号取得全局的任务实例（非玩家自身已接的任务实例）

		@param questID: 任务唯一标识
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
		获取某个任务的环任务列表
		@param questID: QUESTID; 需要获取的任务编号
		@param createIfNotExist: BOOL; 表示如果找不到是否创建一个新的并加入到列表中
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
		获取自身已接的某个任务的任务目标

		@return: instance of QuestDataType,如果任务不存在则会产生异常
		"""
		return self.questsTable[ questID ]

	def questAdd( self, quest, tasks ):
		"""
		@param quest: 任务实例
		@type  quest: Quest
		@param tasks: 该任务的所有需求实例；
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
			#发送悬赏任务状态通知,状态变成已接受
			self.client.sendRewardQuestState( questID, csdefine.REWARD_QUEST_ACCEPT, self.rewardQuestLog[ "degree" ] )
			pass
		
		try:
			g_logger.acceptQuestLog( self.databaseID, self.getName(), questID, self.level, self.grade ) 
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )

	def onQuestBoxStateUpdate( self ):
		"""
		处理所有客户端看到的箱子的状态

		@param quest: 任务
		@type  quest: Quest
		@param taskIndex: 任务目标索引
		@type  taskIndex: INT32
		"""
		self.client.onQuestBoxStateUpdate() #questBoxID 是 任务箱子的className


	def findQuestByType( self , questType ):
		"""
		寻找所有指定类别的任务
		@param questType: 任务类别  查看 csdefine.py
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
		@param questID: 任务ID
		@type  questID: UINT32
		@param isAbandon: 标识是玩家主动放弃(True)或任务完成后由系统删除(False)
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
				#发送悬赏任务状态通知,状态变成可以接受
				self.client.sendRewardQuestState( questID, csdefine.REWARD_QUEST_CAN_ACCEPT, self.rewardQuestLog[ "degree" ] )

	def onQuestComplete( self, questID ):
		"""
		交任务后会收到此通知,表示你已经把任务交了。

		@param questID: 任务ID
		@type  questID: UINT32
		@return: None
		"""
		tempTasks = self.getQuestTasks( questID )
		self.questRemove( questID, 0 )												#删除任务记录
		tempTasks.complete( self )													# 对任务目标进行清理（如删除任务物品等）
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
		查询是否所有任务目标都已达到

		@param questID: 任务ID
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
		查询某个任务目标是否已经失败
		"""
		tasks = self.getQuestTasks( questID ).getTasks()
		return tasks[ taskIndex ].isFailed( self )

	def questIsFailed( self, questID ) :
		"""
		查询任务是否已经失败
		"""
		tasks = self.getQuestTasks( questID ).getTasks()
		for task in tasks.itervalues() :
			if task.isFailed( self ) :
				return True
		return False

	def has_quest( self, questID ):
		"""
		查询是否接了指定的任务

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.questsTable.has_quest( questID )

	def has_randomQuestGroup( self, questID ):
		"""
		查询是否接了指定的随机任务任务

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
		重新计算队友数目(在交任务的时候调用）
		@param   occupation: 对友职业
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
		@param questID: 任务ID
		2008.06.09：改为由 client 请求 cell 中的 role 统一分包发送 －－ by hyw
		"""
		self.setTemp( "rqi_init_list", self.questsTable.keys() )						# 初始化当前发送到的索引（前提是：发送的过程中，questsTable 不变）
		self.addTimer( 0.0, csconst.ROLE_INIT_INTERVAL, ECBExtend.UPDATE_CLIENT_QUESTLOG_CBID )

	def onTimer_updateClientQuestLogs( self, timerID, cbid ) :
		"""
		分包更新客户端任务日志
		2008.06.09：by hyw
		"""
		if len( self.queryTemp( "rqi_init_list" ) ) == 0:
			self.cancel( timerID )								# 停止 timer
			self.removeTemp( "rqi_init_list" )
			self.client.onInitialized( csdefine.ROLE_INIT_QUEST_LOGS )
			return

		questID = self.queryTemp( "rqi_init_list" ).pop( 0 )
		quest = self.getQuest( questID )						# 获取任务
		if not quest or ( quest and not quest.isTasksOk( self ) ):
			self.questsTable.remove( questID )
			ERROR_MSG( "%s(%i): quest %i has not found. I will removed it." % (self.getName(), self.id, questID) )
			return

		tasks = self.questsTable[questID]
		quest.sendQuestLog( self, tasks )					# 发送任务日志


	def requestCompletedQuest( self ):
		"""
		Explore Method
		查询已经完成的任务
		2008.06.10：改为由 client 请求 cell 中的 role 统一发送 －－ by hyw
		"""
		qlist = self.questsLog.list()
		if len( qlist ) > 0:
			self.client.onCompletedQuestIDListReceive( qlist )
		self.client.onInitialized( csdefine.ROLE_INIT_COMPLETE_QUESTS )

	def abandonQuest( self, srcEntityID, questID ):
		"""
		Exposed method.
		玩家请求放弃任务
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
		任务状态改变
		@param   questID: 任务ID
		@param   task: 任务task实例
		"""
		#任务下线失败标记处理add by wuxo 2011-12-27
		quest = self.getQuest( questID )
		if not quest:
			return

		quest_failFlag = self.queryTemp( "questOffLineFail", [] )
		if questID in quest_failFlag:
			if quest.query( self ) == csdefine.QUEST_STATE_FINISH: #任务完成时删除
				if self.isRewardQuest( questID ):
					#发送悬赏任务状态通知,状态变成已完成
					self.client.sendRewardQuestState( questID, csdefine.REWARD_QUEST_COMPLETED, self.rewardQuestLog[ "degree" ] )
				quest_failFlag.remove(i)
			else:
				try:
					for task in self.questsTable[questID].getTasks().values():
						if task.val1 == -1: #任务失败
							quest_failFlag.remove(i)
				except:
					quest_failFlag.remove(i)

		if len(quest_failFlag) == 0:
			self.removeTemp("questOffLineFail")
		else:
			self.setTemp( "questOffLineFail", quest_failFlag )

		#任务目标完成 do something
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
	# 以下为对话及任务交/接封装,包括物品触发任务及共享任务
	#--------------------------------------------------------------------------
	def gossipWith( self, srcEntityID, targetID, keydlg ):#与NPC开始对话和功能对话
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
			INFO_MSG( "entity %i not exist in world" % srcEntityID )	# 这个应该永远都不可能到达
			return

		if self.qieCuoState in [ csdefine.QIECUO_READY, csdefine.QIECUO_FIRE ]: # 切磋准备和进行期间不能与NPC进行对话
			self.statusMessage( csstatus.QIECUO_IS_NOT_DO )
			return
			

		if getattr( targetEntity, "subState", 0 ) == csdefine.M_SUB_STATE_GOBACK:	#如果是怪物处于回跑状态，则不能对话
			return

		if self.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
			if self.isState( csdefine.ENTITY_STATE_DEAD ):
				self.statusMessage( csstatus.NPC_TRADE_DEAD_FORBID_TALK )
			else:
				self.statusMessage( csstatus.NPC_TRADE_FORBID_TALK )
			return

		self.onGossipTrigger( targetID )	# 对话触发16:21 2008-12-1,wsf

		srcEntity = BigWorld.entities[srcEntityID]

		#if srcEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
		#	srcEntity.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
		#	return

		srcClass = targetEntity.getScript()
		srcClass.gossipWith( targetEntity, self, keydlg )	#对于对话，只需要保证角色是real, npc是ghost也没有关系。（zyx）

	def onGossipTrigger( self, targetID ):
		"""
		对话触发一些行为,比如打断角色的潜行效果buff

		@param targetID : 对话的npc id
		@type targetID : OBJECT_ID
		"""
		self.removeAllBuffByBuffID( csconst.PROWL_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE ] )

		# 组队跟随状态队员共享队长的对话
		if self.isTeamCaptain() and self.isTeamFollowing():
			timeDelay = 0.1
			for entity in self.entitiesInRangeExt( csconst.TEAM_FOLLOW_DISTANCE, "Role", self.position ):
				if entity.captainID == self.id and entity.spaceID == self.spaceID and entity.isTeamFollowing() and entity.isReal():
					entity.setTemp( "talkNPCID", targetID )
					entity.setTemp( "talkID", "Talk" )
					entity.addTimer( timeDelay, 0, ECBExtend.AUTO_TALK_CBID )
					timeDelay += 0.1

	def selectQuestFromItem( self, srcEntityID, uid ):#与物品对话
		"""
		Exposed method.
		@param  uid: 物品的唯一ID
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
		#if item.consumable():	# phw: 如果玩家选择不接任务怎么办？比较好的办法可能是把这类物品设为背包中唯一,而接任务后把此物品删除；
		#	item.setAmount( item.getAmount() - 1 ,self )
		quest.gossipDetail( self, None )



	def selectQuest_( self, questID, activationSrc ):
		"""
		选择任务。

		契约：只记录最后选择的任务和任务提供者；不做任务其它事情。

		@param activationSrc: 给任务的源,如果是Entity则表示从玩家中共享而来,如果给的是None则表示从物品触发
		@return: 无
		"""
		self.lastSelectedQuest = questID							# 记录最后一次选择的任务
		if activationSrc is None:
			self.lastQuestActiveObj = 0
		else:
			self.lastQuestActiveObj = activationSrc.id
		return



	def declineSelectedQuest( self, srcEntityID ):
		"""
		Exposed method.
		拒绝当前被选择的任务；
		主要用于任务共享,如果任务共享不存在,此接口也就没什么意义；
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
		任务完成,玩家选择奖励。
		@param questID: 哪个任务完成了
		@type  questID: QUESTID
		@param rewardIndex: 客户端选择的奖励物品所在的索引
		@type  rewardIndex: INT32
		@param codeStr: 任务目标自行解析的字符串
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
			# 没有对话目标无法交任务
			return

		if not self.wallow_getLucreRate():
			# 策划要求玩家游戏收益为0时，无法提交任务
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

		@type targetID: target of gossip with. 理论上targetID不会为0,因为这个接口一定是从NPC身上触发的,其它的共享任务和物品触发任务都有其额外的接口；
		"""
		if self.id != srcEntityID:
			return

		try:
			targetEntity = BigWorld.entities[targetID]
		except KeyError:
			INFO_MSG( "entity %i not exist in world" % targetID )	# 这个应该永远都不可能到达
			return

		if not targetEntity.isInteractionRange( self ):
			WARNING_MSG( "%s(%i): target too far,my position is %s.target( %s)'s position is %s" % (self.getName(), self.id, self.position, targetEntity.className, targetEntity.position) )
			return	# 距离目标太远不允许交谈

		srcClass = targetEntity.getScript()

		if srcClass.hasStartQuest( questID ) or srcClass.hasFinishQuest( questID ):
			# 只有指定的任务存在于任务列表中才允许继续
			srcClass.questSelect( targetEntity, self, questID )

	def questAcceptForce( self, srcEntityID, questID, questEntityID ):
		"""
		Exposed method.
		接受一个任务——强制接受成功，不做任何判断
		@type targetID: target of gossip with. 如果这个参数为0则表示任务是从物品得来的（暂时不考虑共享任务）
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
		接受一个任务
		@type targetID: target of gossip with. 如果这个参数为0则表示任务是从物品得来的（暂时不考虑共享任务）
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
		if srcEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
			srcEntity.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
			return False

		if targetEntity:
			if not targetEntity.isInteractionRange( self ):
				WARNING_MSG( "%s(%i): target too far." % (self.playerName, self.id) )
				return	# 距离目标太远不允许交谈

			#if self.getQuest( questID ).getStyle() == csdefine.QUEST_STYLE_LOOP_GROUP:
			#	if not self.groupQuestSavedAndFailedProcess( questID ):
			#		return

			srcClass = targetEntity.getScript()
			if srcClass.hasStartQuest( questID ):	# 是接任务的NPC
				srcClass.questAccept( targetEntity, self, questID )
		else:
			# 目标不存在,属于物品触发
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
		接受一个任务。
		这里经过了base方判定后，才走到这
		"""
		quest = self.getQuest( questID )
		quest.baseAccept( self )


	def groupQuestReAccept( self,questID ):
		"""
		环任务失败（放弃）重新接受，需要物品或金钱的处理
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
		设置当前活动任务ID 提供给startGossip 任务共享 等 默认使用这个任务通信,因为这个任务就是正在对话的任务
		@param 		 questID:  当前对话任务ID
		@type 		 questID: INT32
		@return: None
		"""
		self.lastSelectedQuest = questID

	def taskIsCompleted( self, questID, index ):
		"""
		查询是否指定任务目标已达到
		@param questID: 任务ID
		@type  questID: QUESTID
		@param index:   任务目标索引
		@type  index:	INT
		@return: BOOL
		@rtype:  BOOL
		"""
		if self.questsTable.has_quest( questID ):
			return self.questsTable[questID].isIndexTaskComplete( self, index )
		return True		# 没有接这个任务就表示已经完成了

	def tasksIsCompleted( self, questID, indexList ):
		"""
		查询是否多个指定任务目标已达到
		@param questID: 任务ID
		@type  questID: QUESTID
		@param index:   任务目标索引
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
		是否存在某个任务索引
		"""
		if not self.has_quest( questID ):
			DEBUG_MSG( "player %i no has quest %i." % ( self.id, questID ) )
			return

		tasks = self.getQuestTasks( questID ).getTasks()
		return index in tasks

	# ----------------------------------------
	# 以下为向客户端发送消息的封装接口
	# ----------------------------------------
	def sendGossipComplete( self ,targetID ):
		"""
		@param 		 player: ROLE 实例
		@type 		 player: OBJECT_ID
		@return: None
		"""
		self.client.onGossipComplete( targetID )

	def setGossipText( self, text ):
		"""
		@param 		player: ROLE 实例
		@type 		 player: OBJECT_ID
		@param 		text: 设置任务窗口文本
		@type 		 text: str
		@return: 	None
		"""
		self.client.onSetGossipText( text )

	def addGossipOption( self, talkID, title, type = csdefine.GOSSIP_TYPE_NORMAL_TALKING ):
		"""
		任务系统普通对话
		@param 		player: ROLE 实例
		@type 		 player: OBJECT_ID
		@type 		talkID: string
		@type 		 title: string
		@return:	 None

		type : 默认是普通对话才用 csdefine.GOSSIP_TYPE_NORMAL_TALKING
		"""
		self.client.onAddGossipOption( talkID, title, type )

	def addGossipQuestOption( self, questID, state ):
		"""
		任务系统任务对话
		@param 		player: ROLE 实例
		@type  		player: OBJECT_ID
		@type dlgKey: string
		@type   title: string
		"""
		quest = self.getQuest( questID )
		self.client.onAddGossipQuestOption( questID, state, quest.getLevel( self ) )

	def sendQuestRewards( self, questID, rewards ):
		"""
		@param 		player: ROLE 实例
		@type 		 player: OBJECT_ID
		@type		 questID: INT32
		@param		 rewards: 任务奖励
		@type  		rewards: items
		@param 		rewardsChoose: 任务选择奖励
		@type  		rewardsChoose: items
		@return: None
		"""
		self.client.onQuestRewards( questID, rewards )

	def sendObjectiveDetail( self, questID, objectiveDetail ):
		"""
		@param 		questID: 任务ID
		@type		questID: INT32
		@param		objectiveDetail: 任务目标描述
		@type		objectiveDetail: list
		"""
		self.client.onQuestObjectiveDetail( questID, cPickle.dumps( objectiveDetail, 2 ) )

	def sendQuestSubmitBlank( self, questID, submitInfo ):
		"""
		@param 		questID: 任务ID
		@type		questID: INT32
		@param		submitInfo: 提交物品描述
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
		# 在周围30米范围内搜索所有帮会成员并发送任务邀请
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
		@param player: ROLE 实例
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
		角色死亡对任务的影响
		比如有些任务要求角色不能死亡，死亡就算任务失败
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
		清理护送任务的NPC
		"""
		# 遍历所有任务
		for questID, questData in self.questsTable.items():
			# 查询此任务是否有跟随的NPC
			npcIDs = questData.query( "follow_NPC", [] )
			if npcIDs.__class__.__name__ == "int":
				npcIDs = [npcIDs]
			for npcID in npcIDs: #modify by wuxo2012-1-18
				if BigWorld.entities.has_key( npcID ):
					# 杀了这个NPC
					BigWorld.entities[ npcID ].defDestroy()
			# 清除标记
			questData.set( "follow_NPC" , [] )

	def isMyOwnerFollowNPC( self, ID ):
		"""
		FollowNPC查询你是不是我的主人样
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
				if self.position.distTo( BigWorld.entities[id].position ) < DISTANCE_FOR_PLAYER_TAKE_SLAVE:				#通过传送门
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
		# 对于身上带反省buff的家伙不可共享接取潜能任务 by 姜毅
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
		对玩家的任务做下线处理
		"""
		# 除玩家身上的科举任务
		# self.deleteIEQuest()
		# 这里可以继续对其他需要处理的任务做处理
		#处理下线失败任务add by wuxo 2011-12-26
		quest_failFlag = self.queryTemp( "questOffLineFail", [] )
		for i in quest_failFlag :
			if i in self.questsTable:
				for taskIndex in self.questsTable[i].getTasks().keys():
					self.questTaskFailed( i, taskIndex )

	def onAddBuff( self, buff ):
		"""
		当增加一个 buff 时被调用
		"""
		self.questBuffAddOrRemoved( buff[ "skill" ].getBuffID(), 1 )

	def onRemoveBuff( self, buff ):
		"""
		删除一个 buff 时被调用
		"""
		self.questBuffAddOrRemoved( buff[ "skill" ].getBuffID(), 0 )

	def springRiddleReward( self ):
		"""
		Define method.
		给春节灯谜奖励
		"""
		awarder = Love3.g_rewards.fetch( csdefine.RCG_SPRING_LIGHT, self )
		freeSpace = self.getNormalKitbagFreeOrderCount()	# 背包剩余格子数
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
		设置角色标签：一起帮会运镖的人数 by 姜毅
		"""
		self.setTemp( "tongDartMembers", number )

	def tongDartExpReward( self ):
		"""
		define method
		镖车刷劫匪时，给与玩家经验奖励
		"""
		if not self.level in SecondExpDatas:
			return
		exp = SecondExpDatas[self.level] * 360
		self.addExp( exp, csdefine.CHANGE_EXP_TONG_DART_ROB )

	def questSingleReward( self, srcEntityID, questID ):
		"""
		Exposed method.
		任务完成,玩家直接获得奖励。这个提供给不需要通过NPC，直接提交完成任务的接口使用的。
		@param questID: 哪个任务完成了
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
	# 随机任务陷阱相关，点击触发陷阱提示的处理
	# -----------------------------------------------------------------------------------------------------
	def onQuestTrapTipClicked( self, srcEntityID, entityID ):
		"""
		Exposed method.
		玩家点击触发陷阱提示的处理

		@param srcEntityID：隐含传送过来的调用者id
		@type srcEntityID:	OBJECT_ID
		@param questID：	任务ID
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
	# AI中关于玩家任务数据的处理
	# -----------------------------------------------------------------------------------------------------
	def onAIAddQuest( self, questID, timeDelay ):
		"""
		给自己添加一个任务
		@param questID:		任务ID
		@type questID:		QUESTID
		@param timeDelay:	任务界面显示延时时间
		@type timeDelay:	INT16
		"""
		quest = self.getQuest( questID )
		if quest and quest.query( self ) == csdefine.QUEST_STATE_NOT_HAVE:
			quest.accept( self )										# 接受任务
			self.delayCall( timeDelay, "showQuestLog", questID )
			
	#-----------------------------------------------------------------------
	# 阵营任务相关
	#-----------------------------------------------------------------------
	def removeFailedCampQuests( self ):
		"""
		移除玩家身上所有未完成的阵营活动和阵营日常任务
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
	#悬赏任务相关
	#--------------------------------------------------------------------------------------------------------
	def requestRewardQuest( self ):
		"""
		请求悬赏任务信息
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
		到时间请求刷新悬赏任务
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
		物品刷新
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
		悬赏任务系统刷新
		"""
		totalQuestList = []
		greenQualityNum = 0
		if isAllRefresh:
			#全部刷新，也就是任务全部进行随机分配
			#获取玩家的对应大类的对应小类的对应等级段任务ID，在这些任务中去随机
			for record in self.canAcceptRewardQuestRecord:
				questID = record.getQuestID()
				if self.has_quest( questID ):
					self.questRemove( questID, True )
			self.canAcceptRewardQuestRecord = []
			totalQuestList += self.rewardTongQuestRefresh( Const.REWARD_QUEST_SMALL_TYPE_NUM, Const.REWARD_QUEST_SMALL_TYPE_NUM )
			totalQuestList += self.rewardCampQuestRefresh( Const.REWARD_QUEST_NUM, [] )
			totalQuestList += self.rewardDailyQuestRefresh( Const.REWARD_QUEST_NUM, [] )
		else:
			#部分刷新，排除已经接取但还没有提交的任务ID
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
		#对于totalQuestList中选中的任务进行一个任务品质的随机
		self.completedRewardQuestRecord = []
		self.assignQuestQuality( totalQuestList, refreshType, greenQualityNum )
		
	def rewardTongQuestRefresh( self, tongQuestNum, runMerchantQuestNum ):
		"""
		帮会日常任务以及帮会建设任务刷新,返回一个包含任务ID，任务大类，任务小类的任务列表
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
		阵营日常任务刷新,返回一个包含任务ID，任务大类，任务小类的任务列表
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
		每日任务刷新,返回一个包含任务ID，任务大类，任务小类的任务列表
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
		对随机产生的任务列表进行品质的随机
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
			if minNum != 0:																#最少产生多少个绿色品质的任务
				self.assignMinNumQuestQuality( questList, minNum - greenQualityNum, node1, node2, node3, node4 )
			elif maxNum != 0:															#最多产生多少个绿色品质的任务,先从总的任务中选择出maxNum个数的任务，然后按照概率对每个任务分配绿色品质
				self.assignMinNumQuestQuality( questList, maxNum - greenQualityNum, node1, node2, node3, greenProbility )
		pass
		
	def assignMaxNumQuestQuality( self, questList, maxNum, node1, node2, node3, greenProbility ):
		"""
		分配最多有多少个绿色品质任务
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
		分配最少有多少个绿色品质任务
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
		判断是否需要刷新，需要返回True，不需要返回False
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
			if currentTime < todayEndTime and currentTime >= timeDatas[ timeLength - 1 ]:							#同一天，现在时间大于等于最后一个时间点，小于24点
				if lastSpawnTime < todayEndTime and lastSpawnTime >= timeDatas[ timeLength - 1 ]:		#上一次刷新时间大于等于最后一个时间点，小于24点
					#不用刷新，直接将数据发送给客户端
					return False
				elif lastSpawnTime < timeDatas[ timeLength - 1 ]:											#上一次刷新时间小于最后一个时间点
					return True
			elif currentTime < timeDatas[ timeLength - 1 ] and currentTime >= timeDatas[ 0 ]:								#现在时间小于最后一个时间点，大于等于第一个时间点，那么index肯定能找到，不会为-1
				if index != -1:																				#如果index能找到（为了代码清晰起见，加入这一判断）
					if lastSpawnTime < timeDatas[ index ] and lastSpawnTime >= timeDatas[ index - 1 ]:		#如果上一次刷新时间也在这个范围内，就不用刷新
						#不用刷新，直接将数据发送给客户端
						return False
					elif lastSpawnTime < timeDatas[ index - 1 ]:					#如果上一次刷新时间不在这个范围内，就要刷新（因为上一次时间点肯定比现在时间要小，不用判断大于timeDatas[ index ]的情况）
						return True
			elif currentTime < timeDatas[ 0 ]:											#如果现在时间小于第一个时间点，而上一次也小于这个时间点，又是同一天不必刷新
				#不用刷新，直接将数据发送给客户端
				return False
		elif lastSpawnDay != day and day - lastSpawnDay == 1 :														#相隔一天
			if lastSpawnTime < todayStartTime and lastSpawnTime >= timeDatas[ timeLength - 1 ] - Const.ONE_DAY_HOUR * 3600:			#上一次刷新时间大于等于前一天的最后一个时间点，小于前一天24点
				if currentTime < timeDatas[ 0 ]:																	#现在时间小于第一个时间点，说明都处于上一天的最后一个时间点到今天第一个时间点之间
					#不用刷新，直接将数据发送给客户端
					return False
				elif currentTime >= timeDatas[ 0 ]:																	#现在时间大于等于第一个时间点，说明处于不同时间段范围
					return True
			elif lastSpawnTime < timeDatas[ timeLength - 1 ] - Const.ONE_DAY_HOUR * 3600:					#上一次刷新时间小于前一天最后一个时间点，说明现在时间和上次刷新时间不在一个时间段范围内
				return True
		elif day - lastSpawnDay > 1 :																			#上一次刷新时间和现在时间相隔天数大于一天，需要重新刷新
			return True
		
	def rewardQuestAccept( self, srcEntityID, questID ):
		"""
		Exposed method.
		接受悬赏任务
		@param srcEntityID：隐含传送过来的调用者id
		@type srcEntityID:	OBJECT_ID
		@param questID：	任务ID
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
		@param quest: 任务实例
		@type  quest: Quest
		@param tasks: 该任务的所有需求实例；
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
		#发送悬赏任务状态通知,状态变成已接受
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
		判断是否是悬赏任务
		"""
		for record in self.canAcceptRewardQuestRecord:
			if questID == record.getQuestID():
				return True
		return False
		
	def sendRewardQuestDatas( self, nextRefreshTime, degree ):
		"""
		向客户端发送悬赏任务数据
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
		返回悬赏任务的品质
		"""
		for record in self.canAcceptRewardQuestRecord:
			if questID == record.getQuestID():
				return record.getQuality()
		return csdefine.REWARD_QUEST_QUALITY_WHITE
		
	def useItemRefreshRewardQuest( self, srcEntityID ):
		"""
		Exposed method
		用物品刷新悬赏任务
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
			item.use( self,self ) #因为use函数里面有调用checkUse进行检查，这里暂不检查，直接使用
		else:
			if highItems:
				if self.iskitbagsLocked():
					self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
					return
				item = highItems[0]
				item.use( self,self ) #因为use函数里面有调用checkUse进行检查，这里暂不检查，直接使用

	def getQuestRewardSlots( self, exposed, questID, rewardIndex, codeStr, questTargetID, useGold ):
		"""
		Exposed method
		设置任务奖励倍数（老虎机）
		@useGold bool 是否使用元宝
		"""
		multiple = random.random.choice( [1, 3, 5] )
		
		#通知客户端生成结果
		self.client.setQuestRewardSlots( multiple )
		
		if useGold:
			multiple += 1
		
		#设置任务倍数变量
		tkey = Const.QUEST_SLOTS_MULTIPLE_KEY % questID
		self.setTemp( tkey, multiple )
		
		#完成任务
		self.questChooseReward( self.id, questID, rewardIndex, codeStr, questTargetID )
	
	def getQuestSlotsMultiple( self, questID ):
		"""
		取得老虎机的奖励倍数
		"""
		tkey = Const.QUEST_SLOTS_MULTIPLE_KEY % questID
		multiple = self.queryTemp( tkey, 1 )
		return multiple
	
	def removeQuestSlotsInfo( self, questID ):
		"""
		删除保存的老虎机临时信息
		"""
		tkey = Const.QUEST_SLOTS_MULTIPLE_KEY % questID
		self.removeTemp( tkey )