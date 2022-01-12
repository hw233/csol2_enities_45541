# -*- coding: gb18030 -*-
#
# $Id $

"""
随机任务模块
"""

import csdefine
import csstatus
from QuestRandomGroup import *
import random
from string import Template
import QTReward
import QTTask
import ItemTypeEnum
import sys
import Love3
from Statistic import Statistic
g_Statistic = Statistic.instance()


TONG_NORMAL_SPELL = 122152003
TONG_BUILD_SPELL = 122152004
TONG_FETE_SPELL = 122152005


class QuestTongNormalLoopGroup( QuestRandomGroup ):
	def __init__( self ):
		QuestRandomGroup.__init__( self )
		self._type = csdefine.QUEST_TYPE_TONG_NORMAL

	def init( self, section ):
		"""
		"""
		QuestRandomGroup.init( self, section )
		self._count_rewards_set ={}
		for sec in section["count_rewards"].values():
			tempDict = {}
			self._count_rewards_set[sec.readInt("index")] = tempDict

			tempDict["count"] = sec["count"].asInt
			tempDict["rate"] = float( sec["rate"].asString )

			tempDict["rewards"] = []
			if sec.has_key( "rewards" ):
				for subsec in sec["rewards"].values():
					instance = QTReward.createReward( subsec.readString( "type" ) )
					instance.init( self, subsec )
					instance.setExtraParam( 20, 2 )
					tempDict["rewards"].append( instance )

			tempDict["rewards_fixed_item"] = None
			extSection = sec["rewards_fixed_item"]
			if extSection and len( extSection ) > 0:
				tempDict["rewards_fixed_item"] = QTRewardItems()
				tempDict["rewards_fixed_item"].init( self, extSection )

			tempDict["rewards_fixed_random_item"] = None
			extSection = sec["rewards_fixed_random_item"]
			if extSection and len( extSection ) > 0:
				tempDict["rewards_fixed_random_item"] = QTRewardFixedRndItems()
				tempDict["rewards_fixed_random_item"].init( self, extSection )

	def getRepeatMoney( self ):
		"""
		"""
		return 0

	def getCountRewardsDetail( self, player ):
		"""
		获得奖励描述细节
		"""
		rewards = []
		rewardsFixedItem = None
		rewardsFixedRandItem = None
		count = player.getSubQuestCount( self._id ) + 1
		e = self._count_rewards_set[ count ]
		if e["rate"] > random.random():
			if e["rewards"]:
				rewards.extend( e["rewards"] )
			if e["rewards_fixed_item"]:
				rewardsFixedItem =  e["rewards_fixed_item"]
			if e["rewards_fixed_random_item"]:
				rewardsFixedRandItem = e["rewards_fixed_random_item"]


		r = []
		for reward in rewards:
			r.append( reward.transferForClient( player, self._id ) )
		if rewardsFixedItem:
			r.append( rewardsFixedItem.transferForClient( player, self._id ) )
		if rewardsFixedRandItem:
			r.append( rewardsFixedRandItem.transferForClient( player, self._id ) )
		return r

	def reward_( self, playerEntity, rewardIndex = 0 ):
		"""
		给予任务完成奖励（子任务）
		@param      playerEntity: instance of Role Entity
		@type       playerEntity: Entity
		@rtype: BOOL
		"""
		count = playerEntity.getSubQuestCount( self._id )
		if count <= 0:
			count = 1
		rewards_ = []
		rewardsFixedItem_ = None
		rewardsFixedRandItem_ = None
		e = self._count_rewards_set[ count ]
		if e["rate"] > random.random():
			if e["rewards"]:
				rewards_.extend( e["rewards"] )
			if e["rewards_fixed_item"]:
				rewardsFixedItem_ =  e["rewards_fixed_item"]
			if e["rewards_fixed_random_item"]:
				rewardsFixedRandItem_ = e["rewards_fixed_random_item"]

		items = []
		if rewardsFixedItem_:
			items.extend( rewardsFixedItem_.getItems( playerEntity, self.getID() ) )

		if rewardsFixedRandItem_:
			items.extend( rewardsFixedRandItem_.getItems( playerEntity, self.getID() ) )

		if playerEntity.checkItemsPlaceIntoNK_( items ) == csdefine.KITBAG_NO_MORE_SPACE:
			playerEntity.statusMessage( csstatus.ROLE_QUEST_KITBAG_FULL_FOR_COMPLETE )
			return False
		if playerEntity.checkItemsPlaceIntoNK_( items ) == csdefine.KITBAG_ITEM_COUNT_LIMIT:
			playerEntity.statusMessage( csstatus.ROLE_QUEST_KITBAG_ITEM_LIMIT_FOR_COMPLETE )
			return False

		for rw  in rewards_:
			rw.do( playerEntity, self._id )

		for item in items:
			tempItem = item.new()
			playerEntity.addItemAndRadio( tempItem, ItemTypeEnum.ITEM_GET_QUEST, reason = csdefine.ADD_ITEM_QUESTTONGNORMALLOOPGROUP )
		return True

	def doFixedCountRandomReward( self, player, count ):
		"""
		"""
		pass

	def abandoned( self, player, flags ):
		"""
		放弃任务增加反省buff
		"""	
		Love3.g_skills[TONG_NORMAL_SPELL].receiveLinkBuff( player, player )		
		return QuestRandomGroup.abandoned( self, player, flags )

	def accept( self, player ):
		"""
		virtual method.

		@param     player: instance of Role Entity
		@type      player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		tongMB = player.tong_getSelfTongEntity()  
		tongMB.queryTongNormalCount(  player.base, self.getID() )
		
	def complete( self, player, rewardIndex, codeStr = "" ):
		"""
		交任务
		"""
		tongMB = player.tong_getSelfTongEntity()  
		tongMB.addTongNormalCount( )	
		return QuestRandomGroup.complete( self, player, rewardIndex, codeStr = "" )
		
	def checkRequirement( self, player ):
		"""
		virtual method.
		判断玩家的条件是否足够接当前任务。
		@return: 如果达不到接任务的要求则返回False。
		@rtype:  BOOL
		"""
		if player.tong_dbID == 0 or player.tongNormalQuestOpenType == 0:		# 帮主没开日常就不让看到任务选项
			return False
		return QuestRandomGroup.checkRequirement( self, player )
		
	def newTasks_( self, player ):
		"""
		开始新任务。返回一个任务实例。从这个随机任务子任务列表中生成适合玩家的任务id临时列表，从这临时id列表随机抽取一个返回。
		@rtype: QuestDataType
		"""
		temp_set = []
		giveItemIDs = []
		for key in self._quest_set:
			if self._quest_set[key].fitPlayer( player ) and self._quest_set[key].getPatternType() == player.tongNormalQuestOpenType:	#找到一组任务中适合玩家的那些任务
				temp_set.append( key )
		if len( temp_set ) == 0:
			player.statusMessage( csstatus.ROLE_QUEST_RANDON_NOT_FIT )
			return None

		key = temp_set[random.randint( 0, len(temp_set) - 1 )]

		for script in self._quest_set[key].beforeAccept_:
			if not script.query( player ):
				return None

		for script in self._quest_set[key].beforeAccept_:
			if isinstance( script, QTSGiveItems ):
				giveItems = script._items
				for i in giveItems:
					giveItemIDs.append( i[0] )
			script.do( player )

		tasks = self._quest_set[key].newTasks_( player )	#取得子任务的目标
		tasks.setQuestID( self._id )						#使用父任务的ID
		tasks.set( "subQuestID", key )						#子任务的ID存储在扩展数据中
		tasks.set( "style", self._style )			#任务样式存储
		tasks.set( "type", self._type )				#任务类型存储
		tasks.set( "giveItemIDs", giveItemIDs )		#接任务给物品的ID

		return tasks

class QuestTongFeteGroup( QuestRandomGroup ):
	def __init__( self ):
		QuestRandomGroup.__init__( self )
		self._type = csdefine.QUEST_TYPE_TONG_FETE

	def init( self, section ):
		"""
		"""
		QuestRandomGroup.init( self, section )

		self.rewards_set ={}
		for sec in section["group_rewards"].values():
			tempDict = self.rewards_set
			tempDict["rewards"] = []
			if sec.has_key( "rewards" ):
				for subsec in sec["rewards"].values():
					instance = QTReward.createReward( subsec.readString( "type" ) )
					instance.init( self, subsec )
					tempDict["rewards"].append( instance )

			tempDict["rewards_fixed_item"] = None
			extSection = sec["rewards_fixed_item"]
			if extSection and len( extSection ) > 0:
				tempDict["rewards_fixed_item"] = QTRewardItems()
				tempDict["rewards_fixed_item"].init( self, extSection )

			tempDict["rewards_fixed_random_item"] = None
			extSection = sec["rewards_fixed_random_item"]
			if extSection and len( extSection ) > 0:
				tempDict["rewards_fixed_random_item"] = QTRewardFixedRndItems()
				tempDict["rewards_fixed_random_item"].init( self, extSection )

	def getRepeatMoney( self ):
		"""
		"""
		return 0

	def abandoned( self, player, flags ):
		"""
		放弃任务
		重置单组任务记录
		"""
		if QuestRandomGroup.abandoned( self, player, flags ):
			Love3.g_skills[TONG_FETE_SPELL].receiveLinkBuff( player, player )
			# 增加提示信息： 您放弃了帮会祭祀任务，获得反省状态，期间无法再次接受帮会祭祀任务。（CSOL-9767）
			player.statusMessage( csstatus.TONG_FETE_QUEST_ABANDON )
			#player.tong_payContribute( 1 ) 案策划要求，取消扣除帮贡的设定( CSOL-9767 )
			return True
		return False

	def getRewardsDetail( self, playerEntity ):
		"""
		获得奖励描述细节（子任务）
		@param      playerEntity: instance of Role Entity
		@type       playerEntity: Entity
		"""
		rewards = []
		rewardsFixedItem = None
		rewardsFixedRandItem = None

		e = self.rewards_set
		if e["rewards"]:
			rewards.extend( e["rewards"] )
		if e["rewards_fixed_item"]:
			rewardsFixedItem =  e["rewards_fixed_item"]
		if e["rewards_fixed_random_item"]:
			rewardsFixedRandItem = e["rewards_fixed_random_item"]


		r = []
		for reward in rewards:
			r.append( reward.transferForClient( playerEntity, self._id ) )
		if rewardsFixedItem:
			r.append( rewardsFixedItem.transferForClient( playerEntity, self._id ) )
		if rewardsFixedRandItem:
			r.append( rewardsFixedRandItem.transferForClient( playerEntity, self._id ) )

		return r

	def reward_( self, playerEntity, rewardIndex = 0 ):
		"""
		给予任务完成奖励（子任务）
		@param      playerEntity: instance of Role Entity
		@type       playerEntity: Entity
		@rtype: BOOL
		"""
		rewards_ = []
		rewardsFixedItem_ = None
		rewardsFixedRandItem_ = None

		e = self.rewards_set
		if e["rewards"]:
			rewards_.extend( e["rewards"] )
		if e["rewards_fixed_item"]:
			rewardsFixedItem_ =  e["rewards_fixed_item"]
		if e["rewards_fixed_random_item"]:
			rewardsFixedRandItem_ = e["rewards_fixed_random_item"]

		items = []
		if rewardsFixedItem_:
			items.extend( rewardsFixedItem_.getItems( playerEntity, self.getID() ) )

		if rewardsFixedRandItem_:
			items.extend( rewardsFixedRandItem_.getItems( playerEntity, self.getID() ) )

		if playerEntity.checkItemsPlaceIntoNK_( items ) == csdefine.KITBAG_NO_MORE_SPACE:
			playerEntity.statusMessage( csstatus.ROLE_QUEST_KITBAG_FULL_FOR_COMPLETE )
			return False
		if playerEntity.checkItemsPlaceIntoNK_( items ) == csdefine.KITBAG_ITEM_COUNT_LIMIT:
			playerEntity.statusMessage( csstatus.ROLE_QUEST_KITBAG_ITEM_LIMIT_FOR_COMPLETE )
			return False

		for rw  in rewards_:
			rw.do( playerEntity, self._id )

		for item in items:
			tempItem = item.new()
			playerEntity.addItemAndRadio( tempItem, ItemTypeEnum.ITEM_GET_QUEST, reason = csdefine.ADD_ITEM_QUESTTONGFETEGROUP )

		BigWorld.globalData["TongManager"].addTongFeteValue( playerEntity.tong_dbID, 1 )
		return True

	def doFixedCountRandomReward( self, player, count ):
		"""
		"""
		pass

	def addGroupRewards( self, playerEntity, point ):
		"""
		给予组任务完成奖励
		组队完成任务的奖励当遇到玩家背包空位不够，或金钱太多等问题，就不会给予
		@param      playerEntity: instance of Role Entity
		@type       playerEntity: Entity
		@param point: 任务积分
		@type  point: INT
		"""
		pass



class QuestTongBuildGroup( QuestRandomGroup ):
	def __init__( self ):
		QuestRandomGroup.__init__( self )
		self._type = csdefine.QUEST_TYPE_TONG_BUILD

	def init( self, section ):
		"""
		"""
		QuestRandomGroup.init( self, section )

		self.rewards_set ={}
		for sec in section["group_rewards"].values():
			tempDict = self.rewards_set
			tempDict["rewards"] = []
			if sec.has_key( "rewards" ):
				for subsec in sec["rewards"].values():
					instance = QTReward.createReward( subsec.readString( "type" ) )
					instance.init( self, subsec )
					tempDict["rewards"].append( instance )

			tempDict["rewards_fixed_item"] = None
			extSection = sec["rewards_fixed_item"]
			if extSection and len( extSection ) > 0:
				tempDict["rewards_fixed_item"] = QTRewardItems()
				tempDict["rewards_fixed_item"].init( self, extSection )

			tempDict["rewards_fixed_random_item"] = None
			extSection = sec["rewards_fixed_random_item"]
			if extSection and len( extSection ) > 0:
				tempDict["rewards_fixed_random_item"] = QTRewardFixedRndItems()
				tempDict["rewards_fixed_random_item"].init( self, extSection )

	def getRepeatMoney( self ):
		"""
		"""
		return 0

	def getRewardsDetail( self, playerEntity ):
		"""
		获得奖励描述细节（子任务）
		@param      playerEntity: instance of Role Entity
		@type       playerEntity: Entity
		"""
		rewards = []
		rewardsFixedItem = None
		rewardsFixedRandItem = None

		e = self.rewards_set
		if e["rewards"]:
			rewards.extend( e["rewards"] )
		if e["rewards_fixed_item"]:
			rewardsFixedItem =  e["rewards_fixed_item"]
		if e["rewards_fixed_random_item"]:
			rewardsFixedRandItem = e["rewards_fixed_random_item"]


		r = []
		for reward in rewards:
			r.append( reward.transferForClient( playerEntity, self._id ) )
		if rewardsFixedItem:
			r.append( rewardsFixedItem.transferForClient( playerEntity, self._id ) )
		if rewardsFixedRandItem:
			r.append( rewardsFixedRandItem.transferForClient( playerEntity, self._id ) )

		# 加上子任务奖励
		tasks = playerEntity.getQuestTasks( self._id )
		subQuestID = tasks.query( "subQuestID" )
		r.extend( self._quest_set[subQuestID].getRewardsDetail( playerEntity ) )

		return r

	def reward_( self, playerEntity, rewardIndex = 0 ):
		"""
		给予任务完成奖励（子任务）
		@param      playerEntity: instance of Role Entity
		@type       playerEntity: Entity
		@rtype: BOOL
		"""
		rewards_ = []
		rewardsFixedItem_ = None
		rewardsFixedRandItem_ = None

		e = self.rewards_set
		if e["rewards"]:
			rewards_.extend( e["rewards"] )
		if e["rewards_fixed_item"]:
			rewardsFixedItem_ =  e["rewards_fixed_item"]
		if e["rewards_fixed_random_item"]:
			rewardsFixedRandItem_ = e["rewards_fixed_random_item"]

		items = []
		if rewardsFixedItem_:
			items.extend( rewardsFixedItem_.getItems( playerEntity, self.getID() ) )

		if rewardsFixedRandItem_:
			items.extend( rewardsFixedRandItem_.getItems( playerEntity, self.getID() ) )

		if playerEntity.checkItemsPlaceIntoNK_( items ) == csdefine.KITBAG_NO_MORE_SPACE:
			playerEntity.statusMessage( csstatus.ROLE_QUEST_KITBAG_FULL_FOR_COMPLETE )
			return False
		if playerEntity.checkItemsPlaceIntoNK_( items ) == csdefine.KITBAG_ITEM_COUNT_LIMIT:
			playerEntity.statusMessage( csstatus.ROLE_QUEST_KITBAG_ITEM_LIMIT_FOR_COMPLETE )
			return False

		for rw  in rewards_:
			rw.do( playerEntity, self._id )

		for item in items:
			tempItem = item.new()
			playerEntity.addItemAndRadio( tempItem, ItemTypeEnum.ITEM_GET_QUEST, reason = csdefine.ADD_ITEM_QUESTTONGBUILDGROUP )
		return True

	def doFixedCountRandomReward( self, player, count ):
		"""
		"""
		pass

	def addGroupRewards( self, playerEntity, point ):
		"""
		给予组任务完成奖励
		组队完成任务的奖励当遇到玩家背包空位不够，或金钱太多等问题，就不会给予
		@param      playerEntity: instance of Role Entity
		@type       playerEntity: Entity
		@param point: 任务积分
		@type  point: INT
		"""
		pass

	def complete( self, player, rewardIndex, codeStr = "" ):
		"""
		交任务
		"""
		if player.getNormalKitbagFreeOrderCount() < 2:
			player.statusMessage( csstatus.ROLE_QUEST_TONG_GIVE_FREE_BLANK )
			return
		tasks = player.getQuestTasks( self._id )
		subQuestID = tasks.query( "subQuestID" )

		if not self._quest_set[subQuestID].complete( player, rewardIndex, codeStr ):
			return

		self.reward_( player )
		player.onQuestComplete( self.getID() )		#使用组ID

		# 统计模块新增任务完成次数
		g_Statistic.addQuestDayStat( player, self._id )

	def abandoned( self, player, flags ):
		"""
		放弃任务增加反省buff
		"""
		Love3.g_skills[TONG_BUILD_SPELL].receiveLinkBuff( player, player )		
		return QuestRandomGroup.abandoned( self, player, flags )
