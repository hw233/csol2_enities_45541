# -*- coding:gb18030 -*-

from bwdebug import *
import csdefine
import csconst
from Quest import Quest
from Resource.QuestLoader import QuestsFlyweight
import cschannel_msgs
import QuestTaskDataType
import random
import items
from Resource.QuestRewardFromTableLoader import QuestRewardFromTableLoader
import QTReward
import csstatus
import ItemTypeEnum

g_questRewardFromTable = QuestRewardFromTableLoader.instance()
g_quests = QuestsFlyweight.instance()

class QuestPotentialSpecial( Quest ):
	"""
	潜能副本特殊任务，此任务的等级、奖励、交任务NPC必须和玩家接任务时所具有的潜能任务一致，	此任务依附于潜能副本任务
	"""
	def __init__( self ):
		"""
		"""
		Quest.__init__( self )
		self._style = csdefine.QUEST_STYLE_POTENTIAL
		self._reward_lv = {}	# 对应等级的奖励
		
	def init( self, section ):
		Quest.init( self, section )
		pDataInfos = g_questRewardFromTable.get( str( self.getID() ) )	# 初始化奖励
		for key, value in pDataInfos.iteritems():
			instance = QTReward.createReward( "QTRewardPotential" )
			instance._potential = value["potential"]
			self._reward_lv[ key] = instance
			
	def newTasks_( self, player ):
		"""
		virtual method. call by accept() method.
		开始新任务，产生一个与玩家当前所具有的潜能任务一致的任务目标实例
		任务中Task变量用来当作任务目标，这里用来当作任务，淡疼。
		
		@return: instance of QuestDataType or derive it；如果任务目标产生失败则必须返回None
		@rtype:  QuestDataType/None
		"""
		questIDs = player.findQuestByType( csdefine.QUEST_TYPE_POTENTIAL )
		if len( questIDs ) == 0:
			ERROR_MSG( "player( %s ) have no potential quest." % player.getName() )
			return None
			
		questID = questIDs[ 0 ]
		potentialQDT = player.questsTable[questID]
		specialPtQuest = Quest.newTasks_( self, player )
		specialPtQuest.set( "qLevel", potentialQDT.query( "qLevel" ) )
		specialPtQuest.set( "style", potentialQDT.query( "style" ) )
		specialPtQuest.set( "type", potentialQDT.query( "type" ) )
		specialPtQuest.set( "lineNumber", potentialQDT.query( "lineNumber" ) )
		specialPtQuest.set( "potentialQusetID", questID )
		potentialQDT.set( "specialPtQuestID", self.getID() )	# 此任务需要和已有的潜能任务捆绑，潜能任务完成时此任务也要完成
		
		ptQuest = g_quests[ questID ]
		if random.randint(1, 100) <= ptQuest.rewardsItemRate:
			itemIDs = ptQuest.rewardsItemList.keys()
			specialPtQuest.set( "rewardItemID", itemIDs[ random.randint( 0, len( itemIDs ) - 1 ) ] )
		return specialPtQuest
		
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
		specialPtQuest = player.questsTable[self.getID()]
		lv = specialPtQuest.query( "qLevel", 0 )
		potentialQuset = g_quests[specialPtQuest.query( "potentialQusetID" )]	# 获得潜能副本任务
		
		rewardItemID = specialPtQuest.query( "rewardItemID", 0 )
		rewardItem = None
		if rewardItemID > 0:
			rewardItem = items.instance().createDynamicItem( rewardItemID, 1 )
			ret = player.checkItemsPlaceIntoNK_( [ rewardItem ] )
			if ret == csdefine.KITBAG_NO_MORE_SPACE:
				player.statusMessage( csstatus.ROLE_QUEST_KITBAG_FULL_FOR_COMPLETE )
				return False
			elif ret == csdefine.KITBAG_ITEM_COUNT_LIMIT:
				player.statusMessage( csstatus.ROLE_QUEST_KITBAG_ITEM_LIMIT_FOR_COMPLETE )
				return False

		if not self._reward_lv[ lv ].check( player ):
			return False

		if 	rewardItem is not None:
			player.addItemAndRadio( rewardItem, ItemTypeEnum.ITEM_GET_QUEST, reason = csdefine.ADD_ITEM_QUESTPOTENTIAL )
			
		self._reward_lv[ lv ].do( player, g_quests.getPotentialLvQuestMapping( lv ) )
		return Quest.reward_( self, player, rewardIndex )

	def getRewardsDetail( self, player ):
		"""
		获得奖励描述细节
		
		这个任务是依赖潜能副本任务而存在的，如果没接潜能副本任务，接这个任务是没任何意义的。
		"""
		questIDs = player.findQuestByType( csdefine.QUEST_TYPE_POTENTIAL )
		if len( questIDs ) == 0:
			ERROR_MSG( "player( %s ) have no potential quest." % player.getName() )
			return []
		ptQuestID = questIDs[0]
		lv = player.questsTable[ ptQuestID ].query( "qLevel", 0 )
		return [ self._reward_lv[ lv ].transferForClient( player, self.getID() ) ]

	def query( self, player ):
		"""
		查询玩家对某一个任务的进行状态。

		@return: 返回值类型请查看common里的QUEST_STATE_*
		@rtype:  UINT8
		"""
		questID = self.getID()
		if player.questIsCompleted( questID ):
			return csdefine.QUEST_STATE_COMPLETE						# 已做过该任务
		if player.has_quest( questID ):
			# 已接了该任务
			if player.questTaskIsCompleted( questID ):
				return csdefine.QUEST_STATE_FINISH						# 任务目标已完成
			else:
				return csdefine.QUEST_STATE_NOT_FINISH					# 任务目标未完成
		else:
			# 没有接该任务
			if self.checkRequirement( player ):
				questIDs = player.findQuestByType( csdefine.QUEST_TYPE_POTENTIAL )
				if len( questIDs ) == 0:
					printStackTrace()
					INFO_MSG( "player( %s ) have no potential quest." % player.getName() )
					return csdefine.QUEST_STATE_NOT_ALLOW
				if g_quests[questIDs[ 0 ]].getObjectIdsOfFinish() == self.getObjectIdsOfFinish():
					return csdefine.QUEST_STATE_NOT_HAVE			# 可以接但还未接该任务
			return csdefine.QUEST_STATE_NOT_ALLOW					# 不够条件接该任务