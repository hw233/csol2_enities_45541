# -*- coding: gb18030 -*-
#
# $Id $

"""
运镖任务模块 spf
"""

import BigWorld
from bwdebug import *
from string import Template
from Quest import *
from QuestDataType import QuestDataType
from QuestRandomRecordType import QuestRandomRecordType
import random
import QTReward
import QTTask
import QTRequirement
import time
import QTScript
import ItemTypeEnum
import sys
import Language
import csdefine
import csstatus
import csconst
from utils import vector3TypeConvert

class QuestDart( Quest ):
	dartConfigSection = Language.openConfigSection("config/server/DartConfig.xml")
	def __init__( self ):
		Quest.__init__( self )
		self._finish_count = 1 #默认为1
		
	def init( self, section ):
		"""
		"""
		Quest.init( self, section )
		formatStr = lambda string : "".join( [ e.strip( "\t " ) for e in string.splitlines(True) ] )

		self._id = section["id"].asInt
		
		if not self.dartConfigSection.has_key( str( self._id ) ):
			ERROR_MSG( "Dart quest(%i) has not be config in DartConfig.xml!"%self._id )
			return

		self.repeatable_ = 1	# 此类型的任务强制任务能重复接

		self._title = section.readString( "title" )
		self._level = section.readInt( "level" )

		objIdsStr = section.readString( "start_by" )
		self._start_objids = objIdsStr.split('|')

		self._start_itemID = section.readInt( "start_by_item" )
		objIdsStr = section.readString( "finish_by" )
		self._finish_objids = objIdsStr.split('|')

		self._next_quest = section.readString( "next_quest" )
		self._can_share = section.readInt( "can_share" )	# 是否能共享

		self._msg_log_detail	= formatStr( section.readString( "msg_log_detail" ) )
		self._msg_objective		= formatStr( section.readString( "msg_objective" ) )
		self._msg_detail		= formatStr( section.readString( "msg_detail" ) )
		self._msg_incomplete	= formatStr( section.readString( "msg_incomplete" ) )
		self._msg_precomplete	= formatStr( section.readString( "msg_precomplete" ) )
		self._msg_complete		= formatStr( section.readString( "msg_complete" ) )

		self._type = csdefine.QUEST_TYPE_DART
		self._finish_count = section.readInt( "repeat_upper_limit" )
		self.sec = self.dartConfigSection[str(self._id)]

		if self.dartConfigSection[str(self._id)]["DartType"].asInt == 1:
			self.configNormalDart()
		elif self.dartConfigSection[str(self._id)]["DartType"].asInt == 2:
			self.configExpDart()
		elif self.dartConfigSection[str(self._id)]["DartType"].asInt == 3:
			self.configFamilyDart()
		elif self.dartConfigSection[str(self._id)]["DartType"].asInt == 4:
			self.configFamilyMemberDart()
		elif self.dartConfigSection[str(self._id)]["DartType"].asInt == 7:
			self.configTongDart( section )
		elif self.dartConfigSection[str(self._id)]["DartType"].asInt == 8:
			self.configTongMemberDart( section )

	def getFactionID( self ):
		"""
		获得此任务镖局的势力
		"""
		return self.sec[ "MyFactionID" ].asInt


	def onAccept( self, player, tasks ):
		"""
		virtual method.
		执行任务实际处理
		"""
		Quest.onAccept( self, player, tasks )
		tasks.set( "acceptTime", time.time() )
		lpLog = player.getLoopQuestLog( self._id, True )
		if lpLog:
			lpLog.incrDegree()
		questEntityID = player.queryTemp( "questEntityID", 0 )
		if questEntityID > 0:
			questEntity = BigWorld.entities.get( questEntityID )
			if questEntity is not None and questEntity.getEntityType() == csdefine.ENTITY_TYPE_VEHICLE_DART:
				questEntity.setDartMember( player.id )
			player.removeTemp( "questEntityID" )
		return True


	def onRemoved( self, player ):
		"""
		任务移去时通知玩家去掉头顶标记
		"""
		if player.hasFlag( csdefine.ROLE_FLAG_CP_DARTING ):
			player.removeFlag( csdefine.ROLE_FLAG_CP_DARTING )
		else:
			player.removeFlag( csdefine.ROLE_FLAG_XL_DARTING )


	def abandoned( self, player, flags ):
		"""
		virtual method.
		运镖任务的放弃只能通过总镖头和大当家完成
		@param player: instance of Role Entity
		@type  player: Entity
		@return: None
		"""
		#为了便于测试先注释掉
		if  flags != csdefine.QUEST_REMOVE_FLAG_NPC_CHOOSE:
			player.statusMessage( csstatus.ROLE_QUEST_DART_ABANDONED_FAILED )
			return False
		player.statusMessage( csstatus.ROLE_QUEST_DART_ABANDONED )
		player.gainMoney( int( self.getYaJin() ) / 4, csdefine.CHANGE_MONEY_ABANDONED )		#返回押金的1/4

		return Quest.abandoned( self, player, flags )


	def getYaJin( self ):
		"""
		"""
		for i in self.beforeAccept_:
			if isinstance( i, QTScript.QTSCheckDeposit ):
				return i._deposit
		return 0


	def isExpensiveDart( self ):
		"""
		是否为贵重镖
		"""
		for i in self.beforeAccept_:
			if isinstance( i, QTScript.QTSCheckItem ):
				return i._itemID == 50101005
		return False


	def reward_( self, player, rewardIndex = 0 ):
		"""
		virtual method. call by complete() method.
		给任务完成奖励。

		@param      player: instance of Role Entity
		@type       player: Entity
		@param rewardIndex: 选择奖励。
		@type  rewardIndex: UINT8
		@return: BOOL
		@rtype:  BOOL
		"""
		items = []
		if self.rewardsFixedItem_:
			items.extend( self.rewardsFixedItem_.getItems( player, self.getID() ) )
		if self.rewardsChooseItem_:
			items.extend( self.rewardsChooseItem_.getItems( player, self.getID() ) )
		if self.rewardsFixedRandItem_:
			items.extend( self.rewardsFixedRandItem_.getItems( player, self.getID() ) )
		if player.checkItemsPlaceIntoNK_( items ) == csdefine.KITBAG_NO_MORE_SPACE:
			player.statusMessage( csstatus.ROLE_QUEST_KITBAG_FULL_FOR_COMPLETE )
			return False
		if player.checkItemsPlaceIntoNK_( items ) == csdefine.KITBAG_ITEM_COUNT_LIMIT:
			player.statusMessage( csstatus.ROLE_QUEST_KITBAG_ITEM_LIMIT_FOR_COMPLETE )
			return False

		for reward in self.rewards_:
			if not reward.check( player ):
				return False

		# give all reward to player except item
		rewardInfoList = []
		for reward in self.rewards_:
			rewardInfoList.extend(reward.do( player, self.getID() ))

		# give item to player
		for item in items:
			tempItem = item.new()
			player.addItemAndRadio( tempItem, ItemTypeEnum.ITEM_GET_QUEST, reason = csdefine.ADD_ITEM_QUESTDART )

		if BigWorld.globalData.has_key('Dart_Activity'):
			# give all reward to player except item
			player.client.onStatusMessage( csstatus.DART_ACTIVITY_SUCCESS, "" )
			rewardInfoList = []
			for reward in self.rewards_:
				#if reward.m_type == csdefine.QUEST_REWARD_MONEY:
					#reward._amount -= self.getYaJin()
				if reward.m_type == csdefine.QUEST_REWARD_DEPOSIT:	# 不需要奖励押金
					continue
				rewardInfoList.extend(reward.do( player, self.getID() ))
				#if reward.m_type == csdefine.QUEST_REWARD_MONEY:
					#reward._amount += self.getYaJin()

			# give item to player
			for item in items:
				tempItem = item.new()
				player.addItemAndRadio( tempItem, ItemTypeEnum.ITEM_GET_QUEST, reason = csdefine.ADD_ITEM_QUESTDART )

		#self.sendCompleteMsg( player , rewardInfoList )
		return True

	#------------------------------------配置专用---------------------------------------------------

	def dartRequirement( self ):
		"""
		"""
		instance = QTRequirement.createRequirement( "QTRDartPrestige" )
		instance._param1 = self.sec["MyFactionID"].asInt
		instance._param2 = self.sec["NeedPrestige"].asInt
		self.requirements_.append( instance )

		instance = QTRequirement.createRequirement( "QTRLevel" )
		instance._minLvl = self.sec["MinLevel"].asInt
		instance._maxLvl = self.sec["MaxLevel"].asInt
		self.requirements_.append( instance )


	def makeDart( self ):
		"""
		"""
		instance = QTScript.createScript( "QTSGnerateDart" )
		instance._eventIndex		= 1											#任务目标索引
		instance._dartCarEntityIDs	= self.sec.readString( "DartID" )			#要生成的镖车实体ID列表
		instance._destNPCID			= self.sec.readString( "EndNPCID" )			#目的NPC的ID
		instance._factionID			= self.sec.readInt( "MyFactionID" )			#镖局势力ID
		instance._questID			= self.sec.readInt( "QuestID" )				#任务ID
		instance._dartPos			= None										#镖车生成点坐标
		
		position = self.sec.readString( "DartPos" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( %s ) Bad format '%s' in section DartPos " % ( self.__class__.__name__, position ) )
			else:
				instance._dartPos = pos
		instance._dartType			= self.sec.readInt( "DartType" )			#运镖类型

		self.beforeAccept_.append( instance )


	def dartScript( self ):
		"""
		"""
		instance = QTScript.createScript( "QTSCheckLevel" )
		instance._minLevel		= self.sec.readInt( "MinLevel" )				#任务所需最低级别
		instance._maxLevel		= self.sec.readInt( "MaxLevel" )				#任务所需最高级别
		instance._minLevTalk	= self.sec.readString( "LowLevelDes" )			#级别不够的对白
		instance._maxLevTalk	= self.sec.readString( "HeightLevelDes" )		#级别过高的对白
		instance._npcClassName	= self.sec.readString( "StartNPCID" )			#接任务的NPC className
		self.beforeAccept_.append( instance )

		instance = QTScript.createScript( "QTSCheckDeposit" )
		instance._deposit		= self.sec.readInt( "Yajin" )					#押金数量
		instance._dialog		= self.sec.readString( "YaJinNotEnough" )		#押金不够对白
		instance._npcClassName	= self.sec.readString( "StartNPCID" )			#接任务的NPC className
		self.beforeAccept_.append( instance )

		instance = QTScript.createScript( "QTSNotHasQuestType" )
		instance._questType		= csdefine.QUEST_TYPE_DART						#任务类型
		instance._dialog		= self.sec.readString( "HasMyDartQuest" )		#已有此类型任务提示对白
		instance._dialog_op		= self.sec.readString( "HasOtherDartQuest" )	#如果有对立任务类型提示对白
		instance._factionID		= self.sec.readInt( "MyFactionID" )				#镖局所属势力id(目前只有镖局需要配置此参数)
		instance._npcClassName	= self.sec.readString( "StartNPCID" )			#接任务的NPC className
		self.beforeAccept_.append( instance )

		instance = QTScript.createScript( "QTSNotHasQuestType" )
		instance._questType		= csdefine.QUEST_TYPE_MEMBER_DART				#任务类型
		instance._dialog		= self.sec.readString( "HasMyDartQuest" )		#已有此类型任务提示对白
		instance._dialog_op		= self.sec.readString( "HasOtherDartQuest" )	#如果有对立任务类型提示对白
		instance._factionID		= self.sec.readInt( "MyFactionID" )				#镖局所属势力id(目前只有镖局需要配置此参数)
		instance._npcClassName	= self.sec.readString( "StartNPCID" )			#接任务的NPC className
		self.beforeAccept_.append( instance )

		instance = QTScript.createScript( "QTSNotHasQuestType" )
		instance._questType		= csdefine.QUEST_TYPE_ROB						#任务类型
		instance._dialog		= self.sec.readString( "HasMyRobDartQuest" )	#已有此类型任务提示对白
		instance._dialog_op		= self.sec.readString( "HasOtherRobDartQuest" )	#如果有对立任务类型提示对白
		instance._factionID		= self.sec.readInt( "MyFactionID" )				#镖局所属势力id(目前只有镖局需要配置此参数)
		instance._npcClassName	= self.sec.readString( "StartNPCID" )			#接任务的NPC className
		self.beforeAccept_.append( instance )

		instance = QTScript.createScript( "QTSSetFaction" )
		instance._questID		= self.sec.readInt( "QuestID" )					#任务id
		instance._factionID		= self.sec.readInt( "MyFactionID" )				#镖局势力id
		self.beforeAccept_.append( instance )

		#对接任务行为进行排序
		for i in self.beforeAccept_:
			if i.__class__.__name__ == "QTSIsCaptain":
				self.beforeAccept_.remove( i )
				self.beforeAccept_.append( i )
				break

		for i in self.beforeAccept_:
			if i.__class__.__name__ == "QTSCheckItem":
				self.beforeAccept_.remove( i )
				self.beforeAccept_.append( i )
				break

		for i in self.beforeAccept_:
			if i.__class__.__name__ == "QTSNotHasQuestType":
				self.beforeAccept_.remove( i )
				self.beforeAccept_.append( i )
				break

		for i in self.beforeAccept_:
			if i.__class__.__name__ == "QTSCheckDeposit":
				self.beforeAccept_.remove( i )
				self.beforeAccept_.append( i )
				break

		instance = QTScript.createScript( "QTSAfterMissionComplete" )
		instance._factionID		= self.sec.readInt( "MyFactionID" )			#镖局势力id
		instance._completeVal	= self.sec.readInt( "RewardPrestigeMy" )		#完成任务增加的声望值
		instance._abandoneVal	= self.sec.readInt( "AbandonPrestige" )		#放弃或失败减少的声望值
		instance._questType		= self.sec.readInt( "DartStyle" )			#任务类型(5为运镖，6为劫镖)
		instance._abandonedFlag	= {37:"sm_dartNotoriousXinglong", 38:"sm_dartNotoriousChangping"}
		instance._completedFlag	= {37:"sm_dartCreditXinglong", 38:"sm_dartCreditChangping"}
		self.afterComplete_.append( instance )


	def normalDartSpecialRequirement( self ):
		"""
		"""
		instance = QTRequirement.createRequirement( "QTRNormalDartCount" )
		instance._count = self.sec["DartCount"].asInt
		self.requirements_.append( instance )


	def expDartSpecialRequirement( self ):
		"""
		"""
		instance = QTRequirement.createRequirement( "QTRExpDartCount" )
		instance._count = self.sec["DartCount"].asInt
		self.requirements_.append( instance )


	def familyDartSpecialRequirement( self ):
		"""
		"""
		instance = QTRequirement.createRequirement( "QTRFamilyDartCount" )
		instance._count = self.sec["DartCount"].asInt
		self.requirements_.append( instance )
		
	def tongDartSpecialRequirement( self ):
		"""
		"""
		instance = QTRequirement.createRequirement( "QTRTongDartCount" )
		instance._count = self.sec["DartCount"].asInt
		self.requirements_.append( instance )

	def dartTask( self ):
		"""
		"""
		instance = QuestTaskDataType.createTask( "QTTaskEventTrigger" )
		instance.index = 1
		instance.val2 = 1									# total complete of amount
		instance.str2 = self.sec["DartDes"].asString		# describe
		self.tasks_[instance.index] =  instance

		instance = QuestTaskDataType.createTask( "QTTaskTime" )
		instance.index	= 2
		instance._lostTime = self.sec["Time"].asInt
		self.tasks_[instance.index] =  instance


	def dartReward( self ):
		"""
		"""
		instance = QTReward.createReward( "QTRewardExpDart" )
		instance._amount = self.sec.readInt( "RewardExp" )
		self.rewards_.append( instance )

		instance = QTReward.createReward( "QTRewardPrestige" )
		instance._prestigeID = self.sec.readInt( "MyFactionID" )					#势力ID
		instance._value		 = self.sec.readInt( "RewardPrestigeMy" )				#声望值
		self.rewards_.append( instance )

		instance = QTReward.createReward( "QTRewardPrestige" )
		instance._prestigeID = self.sec.readInt( "OtherFactionID" )					#势力ID
		instance._value		 = -self.sec.readInt( "RewardPrestigeOther" )			#声望值
		self.rewards_.append( instance )

		instance = QTReward.createReward( "QTRewardDeposit" )
		instance._amount = self.sec.readInt( "Yajin" )
		self.rewards_.append( instance )

	def dartRewardTong( self, section ):
		"""
		"""
		if section.has_key( "rewards" ):
			for sec in section["rewards"].values():
				typeStr = sec.readString( "type" )
				instance = QTReward.createReward( typeStr )
				instance.init( self, sec )
				if typeStr == "QTRewardMoneyByTemp":
					instance._amount = self.sec.readInt( "RewardMoney" )
				elif typeStr == "QTRewardDeposit":
					instance._amount = self.sec.readInt( "Yajin" )
				elif typeStr == "QTTongContributeNormal":
					instance._amount = self.sec.readInt( "RewardContribute" )
				elif typeStr == "QTTongContribute":
					instance._amount = self.sec.readInt( "RewardContribute" )
				self.rewards_.append( instance )
		instance = QTReward.createReward( "QTTongContributeNormal" )
		instance._amount = self.sec.readInt( "RewardContribute" )					#势力ID
		self.rewards_.append( instance )
		instance = QTReward.createReward( "QTRewardDeposit" )
		instance._amount = self.sec.readInt( "Yajin" )
		self.rewards_.append( instance )

	def expDartItem( self ):
		"""
		"""
		instance = QTScript.createScript( "QTSCheckItem" )
		instance._itemID	= self.sec.readInt( "ExpDartItem" )					#所需物品的ID
		instance._itemAmount= 1													#所需物品数量
		instance._dialog	= self.sec.readString( "HasNotExpDartItem" )		#缺少物品的对白
		instance._npcClassName = self.sec.readString( "StartNPCID" )			#接任务的NPC className
		self.beforeAccept_.append( instance )


	def familyDartLeader( self ):
		"""
		"""
		instance = QTScript.createScript( "QTSIsCaptain" )
		questsStr				= self.sec.readString( "MemberDartID" )			#任务id
		instance._dialog		= self.sec.readString( "NotFamilyLeader" )		#不是族长的对白
		instance._distance		= 30.0											#族长范围内多少距离的玩家
		instance._npcClassName	= self.sec.readInt( "StartNPCID" )				#接任务的NPC className
		instance._quests = []
		for i in questsStr.split('|'):
			instance._quests.append( i.split(':') )
		instance._quests.reverse()
		self.beforeAccept_.append( instance )


	def familyAfterComplete( self ):
		"""
		"""
		instance = QTScript.createScript( "QTSAfterFamilyComplete" )
		questsStr				= self.sec.readString( "MemberDartID" )			#任务id
		instance._eventIndex	= 1
		instance._distance		= 100.0					#距离
		instance._quests = []
		for i in questsStr.split('|'):
			instance._quests.append( i.split(':') )
		instance._quests.reverse()
		self.afterComplete_.append( instance )


	def familyMemberRequirement( self ):
		"""
		"""
		instance = QTRequirement.createRequirement( "QTRLevel" )
		instance._minLvl = self.sec["MinLevel"].asInt
		instance._maxLvl = self.sec["MaxLevel"].asInt
		self.requirements_.append( instance )
		
	def tongDartLeader( self ):
		"""
		"""
		instance = QTScript.createScript( "QTSIsCaptain" )
		questsStr				= self.sec.readString( "MemberDartID" )			#任务id
		instance._dialog		= self.sec.readString( "NotFamilyLeader" )		#不是族长的对白
		instance._distance		= 30.0											#族长范围内多少距离的玩家
		instance._npcClassName	= self.sec.readInt( "StartNPCID" )				#接任务的NPC className
		instance._quests = []
		for i in questsStr.split('|'):
			instance._quests.append( i.split(':') )
		instance._quests.reverse()
		self.beforeAccept_.append( instance )
		
	def tongAfterComplete( self ):
		"""
		"""
		instance = QTScript.createScript( "QTSAfterTongComplete" )
		questsStr				= self.sec.readString( "MemberDartID" )			#任务id
		instance._eventIndex	= 1
		instance._distance		= 100.0					#距离
		instance._quests = []
		for i in questsStr.split('|'):
			instance._quests.append( i.split(':') )
		instance._quests.reverse()
		self.afterComplete_.append( instance )

	def tongMemberRequirement( self ):
		"""
		"""
		instance = QTRequirement.createRequirement( "QTRLevel" )
		instance._minLvl = self.sec["MinLevel"].asInt
		instance._maxLvl = self.sec["MaxLevel"].asInt
		self.requirements_.append( instance )

	def configNormalDart( self ):
		"""
		普通镖
		"""
		self.normalDartSpecialRequirement()
		self.makeDart()
		self.dartRequirement()
		self.dartScript()
		self.dartTask()
		self.dartReward()


	def configExpDart( self ):
		"""
		贵重镖
		"""
		self.expDartSpecialRequirement()
		self.makeDart()
		self.expDartItem()
		self.dartRequirement()
		self.dartScript()
		self.dartTask()
		self.dartReward()


	def configFamilyDart( self ):
		"""
		家族镖
		"""
		self.familyDartSpecialRequirement()
		self.makeDart()
		self.familyDartLeader()
		self.dartRequirement()
		self.dartScript()
		self.familyAfterComplete()
		self.dartTask()
		self.dartReward()
		
	def configTongDart( self, section ):
		"""
		帮会镖
		"""
		self.tongDartSpecialRequirement()
		self.makeDart()
		#self.tongDartLeader()
		instance = QTRequirement.createRequirement( "QTRLevel" )
		instance._minLvl = self.sec["MinLevel"].asInt
		instance._maxLvl = self.sec["MaxLevel"].asInt
		self.requirements_.append( instance )
		self.dartScript()
		instance = QTScript.createScript( "QTSAddDartCount" )
		instance._dartType		= self.sec.readInt( "DartType" )				#镖局任务类型
		instance._value			= 1												#次数值
		self.beforeAccept_.append( instance )
		#self.tongAfterComplete()
		self.dartTask()
		self.dartRewardTong(section)

	def configFamilyMemberDart( self ):
		"""
		家族成员镖
		"""
		self.familyDartSpecialRequirement()
		self.familyMemberRequirement()
		self.dartScript()
		self.dartTask()
		self.dartReward()
		
	def configTongMemberDart( self, section ):
		"""
		帮会成员镖
		"""
		self.tongDartSpecialRequirement()
		self.tongMemberRequirement()
		self.dartScript()
		instance = QTScript.createScript( "QTSAddDartCount" )
		instance._dartType		= self.sec.readInt( "DartType" )				#镖局任务类型
		instance._value			= 1												#次数值
		self.beforeAccept_.append( instance )
		self.dartTask()
		self.dartRewardTong( section )

	def sendQuestLog( self, player, questLog ):
		"""
		"""
		Quest.sendQuestLog( self, player, questLog )
		if player.questIsFailed( self._id ):
			return
		self.addPlayerDartFlag( player )


	def addPlayerDartFlag( self, player ):
		"""
		"""
		factionID = self.getFactionID()					#获取镖局所属势力
		player.updateDartTitle( factionID, True )		#增加运镖称号
		if factionID == csconst.FACTION_CP:
			player.addFlag( csdefine.ROLE_FLAG_CP_DARTING )
		else:
			player.addFlag( csdefine.ROLE_FLAG_XL_DARTING )
		player.client.updateTitlesDartRob( factionID )
