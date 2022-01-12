# -*- coding: gb18030 -*-
#
# $Id $

"""
随机任务模块
"""

from Quest import *
from QuestDataType import QuestDataType
from QuestRandomRecordType import QuestRandomRecordType
from string import Template
from QTScript import QTSGiveItems
from bwdebug import *
import csdefine
import csstatus
import QTReward
import QTTask
import random
from Statistic import Statistic
g_Statistic = Statistic.instance()

class QuestRandomGroup( Quest ):
	def __init__( self ):
		Quest.__init__( self )
		self._quest_set = {}						# 随机任务集合 key is questID, value is instance of Quest
		self._pattern_set = {}						# 随机任务的模式结合 key is a type of patterns. value is the msg of a pattern
		self._group_count = 0						# 一组随机任务的数目（也就是完成多少随机任务发最终奖励）
		self._group_reward_set = {}					#最终奖励集合（依据积分分几个层次）
		self._count_rewards_set ={}					#固定环数随机奖励
		self._deposit_count = 0						#第几次退还押金
		self._deposit = 0							#随机任务押金
		self._repeatTimePerDate = 0					#1天允许完成组数
		self._style = csdefine.QUEST_STYLE_RANDOM_GROUP	# 任务样式

	def init( self, section ):
		"""
		"""
		Quest.init( self, section )

		self._group_count = section.readInt( "group_count" )
		self._deposit_count = section.readInt( "deposit_count" )
		self._deposit = 0 #押金机制取消
		self._repeatNeedMoney = section.readInt( "deposit" )
		self._repeatTimePerDate = section.readInt( "repeat_time_per_date" )
		self.repeatable_ = 1	# 此类型的任务强制任务能重复接

		for sec in section["pattern"].values():
			tempDict = {}
			self._pattern_set[sec.readInt( "type" )] = tempDict
			tempDict["msg_objective"] 	= Template( sec.readString( "msg_objective" ) )
			tempDict["msg_detail"] 		= Template( sec.readString( "msg_detail" ) )
			tempDict["msg_log_detail"] 	= Template( sec.readString( "msg_log_detail" ) )
			tempDict["msg_incomplete"] 	= Template( sec.readString( "msg_incomplete" ) )
			tempDict["msg_precomplete"]	= Template( sec.readString( "msg_precomplete" ) )
			tempDict["msg_complete"] 	= Template( sec.readString( "msg_complete" ) )

		for sec in section["group_rewards"].values():
			tempDict = {}
			self._group_reward_set[sec.readInt("index")] = tempDict

			tempDict["point_min"] = sec["point_min"].asInt
			tempDict["point_max"] = sec["point_max"].asInt

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

	def setID( self, id ):
		"""
		"""
		self._id = id


	def beforeAccept( self, player ):
		"""
		virtual method.
		执行接任务的判断
		"""
		if not self.beforeGroupAccept( player ):
			return None

		tasks = Quest.beforeAccept( self, player )
		if tasks is None:
			return None

		return tasks

	def beforeGroupAccept( self, player ):
		"""
		virtual method.
		执行接组任务判断
		"""
		if not player.has_randomQuestGroup( self._id ): 					#增加随机任务记录判断
			record = QuestRandomRecordType()
			record.init( self._id )
			record.reset()
			player.addRandomLogs( self._id, record )

		if not player.checkStartGroupTime( self._id ) and not player.isGroupQuestRecorded( self._id ):
			# 随机任务每天的重置(不同的日期 and 不是读取的环任务记录)
			player.resetGroupQuest( self._id )

		if self._repeatTimePerDate <= player.getGroupQuestCount( self._id ) and player.isGroupQuestRecorded( self._id ):
			player.resetGroupQuest( self._id )
			player.setGroupQuestRecorded( self._id, False )

		if self._repeatTimePerDate <= player.getGroupQuestCount( self._id ): #随机任务每天的重做次数
			"""
			当任务达到最大次数时，还需要考虑现在做的是以前的存档任务，还是就是当天的环任务
			如果是存档任务，则还可以继续做当天的任务。
			"""
			if not player.newDataGroupQuest( self._id ):
				player.statusMessage( csstatus.ROLE_QUEST_GROUP_ENOUGH )
				return False

		if player.getSubQuestCount( self._id ) == 0:								#如果又回到了一组的第一个随机任务（进行押金处理）
			if player.money < self._deposit:									#押金判断
				player.statusMessage( csstatus.ROLE_QUEST_DEPOSIT_NOT_ENOUGH )
				return False
			player.payQuestDeposit( self._id, self._deposit )


		return True



	def onAccept( self, player, tasks ):
		"""
		virtual method.
		执行任务实际处理
		"""
		Quest.onAccept( self, player, tasks )
		player.setGroupCurID( self._id, tasks.query("subQuestID") )


	def getCountTitle( self, player ):
		return self.getTitle()

	def getRewardsDetail( self, player ):
		"""
		获得奖励描述细节（子任务）
		@param      player: instance of Role Entity
		@type       player: Entity
		"""
		tasks = player.getQuestTasks( self._id )
		subQuestID = tasks.query( "subQuestID" )
		tempList = self._quest_set[subQuestID].getRewardsDetail( player )
		tempList.extend( self.getCountRewardsDetail( player ) )
		return tempList


	def getCountRewardsDetail( self, player ):
		"""
		获得奖励描述细节
		"""
		rewards = []
		rewardsFixedItem = None
		rewardsFixedRandItem = None
		for e in self._count_rewards_set.itervalues():
			count = e["count"]
			if not ( player.getSubQuestCount( self._id ) + 1) % count:
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

	def reward_( self, player, rewardIndex = 0 ):
		"""
		给予任务完成奖励（子任务）
		@param      player: instance of Role Entity
		@type       player: Entity
		@rtype: BOOL
		"""
		return True
		#tasks = player.getQuestTasks( self._id )
		#subQuestID = tasks.query( "subQuestID" )

		#return self._quest_set[subQuestID].reward_( player, rewardIndex )


	def addGroupRewards( self, player, point ):
		"""
		给予组任务完成奖励
		组队完成任务的奖励当遇到玩家背包空位不够，或金钱太多等问题，就不会给予
		@param      player: instance of Role Entity
		@type       player: Entity
		@param point: 任务积分
		@type  point: INT
		"""
		rewardsDict = self.getRewardsDict( point )
		if rewardsDict == {}:
			return

		self.rewards_ = rewardsDict["rewards"]
		self.rewardsFixedItem_ = rewardsDict["rewards_fixed_item"]
		self.rewardsFixedRandItem_ = rewardsDict["rewards_fixed_random_item"]
		Quest.reward_( self, player )
		r = Quest.getRewardsDetail( self, player )

		#player.client.addGroupRewardsInfo( self._id, r )#这里要改为让client弹出最终奖励窗口


	def getRewardsDict( self, point ):
		"""
		获得适合这个任务积分的组任务奖励实例
		@rtype:		QTReward
		"""
		for e in self._group_reward_set.itervalues():
			if e["point_min"] <= point and e["point_max"] >= point:
				return e
			else:
				return {}
		return {}

	def abandoned( self, player, flags ):
		"""
		放弃任务
		重置单组任务记录
		"""
		tasks = player.getQuestTasks( self._id )
		giveItems = tasks.query( "giveItemIDs", [] )
		for itemID in giveItems:
			item = player.findItemFromNKCK_( itemID )
			if item is not None:
				player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_ABANDONEDQUESTRANDOM )
		return Quest.abandoned( self, player, flags )

	def getGroupTotalCount( self ):
		"""
		获得一组随机任务的需要完家完成的次数
		"""
		return self._group_count


	def newTasks_( self, player ):
		"""
		开始新任务。返回一个任务实例。从这个随机任务子任务列表中生成适合玩家的任务id临时列表，从这临时id列表随机抽取一个返回。
		@rtype: QuestDataType
		"""
		temp_set = []
		giveItemIDs = []
		for key in self._quest_set:
			if self._quest_set[key].fitPlayer( player ):	#找到一组任务中适合玩家的那些任务
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


	def complete( self, player, rewardIndex, codeStr = "" ):
		"""
		交任务
		"""
		if player.getNormalKitbagFreeOrderCount( ) < 2:
			player.statusMessage( csstatus.ROLE_QUEST_NEED_TWO_FREE_BLANK )
			return

		tasks = player.getQuestTasks( self._id )
		subQuestID = tasks.query( "subQuestID" )

		if not self._quest_set[subQuestID].complete( player, rewardIndex, codeStr ):
			return

		if player.getSubQuestCount( self._id ) == self._deposit_count:	#当完成任务的次数等于退还押金次数时，退还押金
			if not player.returnDeposit( self._id ):
				player.statusMessage( csstatus.CIB_MONEY_OVERFLOW )
				return

		if not self.reward_( player ):
			return

		self.doFixedCountRandomReward( player, player.getSubQuestCount( self._id ) ) #进行固定次数奖励处理

		if player.getSubQuestCount( self._id ) >= self.getGroupTotalCount():	#玩家完成的次数是否达到一组的次数判断
			point =player.takeGroupPoint( self._id )
			self.addGroupRewards( player, point )							#最终奖励
			player.addGroupQuestCount( self._id )							#增加组完成次数
			player.resetSingleGroupQuest( self._id )						#重置单组记录数据
			#player.delRandomQuestRecord( self._id )

		player.onQuestComplete( self.getID() )		#使用组ID

		# 统计模块新增任务完成次数
		g_Statistic.addQuestDayStat( player, self._id )

	def doFixedCountRandomReward( self, player, count ):
		"""
		"""
		self.rewards_ = []
		self.rewardsFixedItem_ = None
		self.rewardsFixedRandItem_ = None
		for e in self._count_rewards_set.itervalues():
			if count == e["count"]:
				if e["rewards"]:
					self.rewards_.extend( e["rewards"] )
				if e["rewards_fixed_item"]:
					self.rewardsFixedItem_ =  e["rewards_fixed_item"]
				if e["rewards_fixed_random_item"]:
					self.rewardsFixedRandItem_ = e["rewards_fixed_random_item"]
				break

		if len( self.rewards_ ) == 0 and self.rewardsFixedItem_ == None and self.rewardsFixedRandItem_ == None:
			return
		Quest.reward_( self, player )

		r = Quest.getRewardsDetail( self, player )

	def gossipDetail( self, player, issuer = None ):
		"""
		任务故事内容描述对白；
		显示此对白后就可以点“accept”接任务了；
		如果issuer为None则表示任务可能是从物品触发或player共享得来
		"""
		if issuer:	targetID = issuer.id
		else:		targetID = 0
		if not player.has_quest( self._id ):		#还没有获得随机任务之前，具体任务的描述，奖励将不可确定。
			player.sendQuestRewards( self._id, [] )
			player.sendQuestDetail( self._id, 111, targetID )
			return
		tasks = player.getQuestTasks( self._id )
		subQuestID = tasks.query( "subQuestID" )
		patternType = self._quest_set[subQuestID].getPatternType()

		msg_objective = self.getPatternObjectiveMsg( patternType, self._quest_set[subQuestID].getParamsDict() )
		msg_detail = self.getPatternDetailMsg( patternType, self._quest_set[subQuestID].getParamsDict() )
		level = self._quest_set[subQuestID].getLevel()
		#title = self._quest_set[subQuestID].getCountTitle(player)

		player.sendQuestRewards( self._id, self.getRewardsDetail( player ) )
		player.sendQuestDetail( self._id, level, targetID )


	def addChild( self, questID, quest ):
		"""
		加一个随机任务到随机任务集合中
		"""
		self._quest_set[questID] = quest

	def getPatternDetailMsg( self, type, paramsDict ):
		"""
		取得一个模式的故事描述内容对白
		@param type: 任务模式类型
		@type type: int
		"""
		return self._pattern_set[type]["msg_detail"].safe_substitute( paramsDict )


	def getPatternIncompleteMsg( self, type, paramsDict ):
		"""
		取得一个模式的任务未完成对白
		"""
		return self._pattern_set[type]["msg_incomplete"].safe_substitute( paramsDict )


	def getPatternPrecompleteMsg( self, type, paramsDict ):
		"""
		取得一个模式的任务已完成对白
		"""
		return self._pattern_set[type]["msg_precomplete"].safe_substitute( paramsDict )


	def getPatternQuestLogMsg( self, type, paramsDict ):
		"""
		取得一个模式的发送任务日志
		"""
		return self._pattern_set[type]["msg_log_detail"].safe_substitute( paramsDict )


	def getPatternCompleteMsg( self, type, paramsDict ):
		"""
		取得一个模式的交任务对白
		"""
		return self._pattern_set[type]["msg_complete"].safe_substitute( paramsDict )


	def getPatternObjectiveMsg( self, type, paramsDict ):
		"""
		取得一个模式的任务目标对白
		"""
		return self._pattern_set[type]["msg_objective"].safe_substitute( paramsDict )


	def gossipIncomplete( self, player, issuer ):
		"""
		任务目标未完成对白；
		"""
		tasks = player.getQuestTasks( self._id )
		subQuestID = tasks.query( "subQuestID" )

		patternType = self._quest_set[subQuestID].getPatternType()
		msg_incomplete = self.getPatternIncompleteMsg( patternType, self._quest_set[subQuestID].getParamsDict() )
		level = self._quest_set[subQuestID].getLevel()
		#title = self._quest_set[subQuestID].getCountTitle(player)

		if issuer:	targetID = issuer.id
		else:		targetID = 0

		player.sendQuestIncomplete(  self._id, self.getCountTitle(player), level, msg_incomplete, targetID )
		player.statusMessage( csstatus.ROLE_QUEST_INCOMPLETE )

	def gossipPrecomplete( self, player, issuer ):
		"""
		任务目标已完成对白
		"""
		tasks = player.getQuestTasks( self._id )
		subQuestID = tasks.query( "subQuestID" )

		patternType = self._quest_set[subQuestID].getPatternType()

		msg_precomplete = self.getPatternPrecompleteMsg( patternType, self._quest_set[subQuestID].getParamsDict() )
		msg_log_detail = self.getPatternQuestLogMsg( patternType, self._quest_set[subQuestID].getParamsDict() )

		level = self._quest_set[subQuestID].getLevel()
		#title = self._quest_set[subQuestID].getCountTitle(player)

		if issuer:	targetID = issuer.id
		else:		targetID = 0
		#player.sendObjectiveDetail( self._id, self._quest_set[subQuestID].getObjectiveDetail( player ) )
		player.sendObjectiveDetail( self._id, player.questsTable[self._id].getObjectiveDetail( player ) )
		player.sendQuestRewards( self._id, self.getRewardsDetail( player ) )
		player.sendQuestSubmitBlank( self._id, self._quest_set[subQuestID].getSubmitDetail( player ) )
		if len( msg_precomplete ):
			msg = msg_precomplete
		else:
			msg = msg_log_detail
		player.sendQuestPrecomplete( self._id, self.getCountTitle(player), level, msg, targetID )


	def gossipComplete( self, player, issuer ):
		"""
		交任务后对白
		"""
		tasks = player.getQuestTasks( self._id )
		subQuestID = tasks.query( "subQuestID" )

		patternType = self._quest_set[subQuestID].getPatternType()

		msg_complete = self.getPatternCompleteMsg( patternType, self._quest_set[subQuestID].getParamsDict() )
		level = self._quest_set[subQuestID].getLevel()
		#title = self._quest_set[subQuestID].getCountTitle(player)

		if issuer:	targetID = issuer.id
		else:		targetID = 0
		if len( self._msg_complete ) > 0:
			player.sendQuestComplete( self._id, self.getCountTitle(player), level, msg_complete, targetID )


	def sendQuestLog( self, player, questLog ):
		"""
		发送任务日志
		@param questLog: 任务日志; instance of QuestDataType
		"""
		tasks = player.getQuestTasks( self._id )
		subQuestID = tasks.query( "subQuestID" )
		patternType = self._quest_set[subQuestID].getPatternType()
		msg_log_detail = self.getPatternQuestLogMsg( patternType, self._quest_set[subQuestID].getParamsDict() )
		msg_objective = self.getPatternObjectiveMsg( patternType, self._quest_set[subQuestID].getParamsDict() )
		level = self.getLevel()
		player.client.onQuestLogAdd( self._id, self._can_share, self._completeRuleType, questLog, level, self.getRewardsDetail(player) )


	def isTasksOk( self, player ):
		"""
		检查任务目标是否有效
		"""
		tasks = player.getQuestTasks( self._id )
		subQuestID = tasks.query( "subQuestID" )

		return self._quest_set.has_key( subQuestID )


	def onComplete( self, player ):
		"""
		任务提交完成通知
		"""
		if not player.checkStartGroupTime( self._id ) and not player.isGroupQuestRecorded( self._id ):
			# 环任务重置
			player.resetGroupQuest( self._id )
		return
		#count = player.getSubQuestCount( self.getID() ) #任务次数
		#if count <= self._group_count:
		#	self.accept( player )


	def loadTasks_( self, player, subQuestID ):
		"""
		开始新任务。返回一个任务实例。从这个随机任务子任务列表中生成适合玩家的任务id临时列表，从这临时id列表随机抽取一个返回。
		@rtype: QuestDataType
		"""
		giveItemIDs = []
		for script in self._quest_set[subQuestID].beforeAccept_:
			if not script.query( player ):
				return None

		for script in self._quest_set[subQuestID].beforeAccept_:
			if isinstance( script, QTSGiveItems ):
				giveItems = script._items
				for i in giveItems:
					giveItemIDs.append( i[0] )
			script.do( player )

		tasks = self._quest_set[subQuestID].newTasks_( player )	#取得子任务的目标
		tasks.setQuestID( self._id )							#使用父任务的ID
		tasks.set( "subQuestID", subQuestID )					#子任务的ID存储在扩展数据中
		tasks.set( "style", self._style )						#任务样式存储
		tasks.set( "type", self._type )							#任务类型存储
		tasks.set( "giveItemIDs", giveItemIDs )					#接任务给物品的ID

		return tasks

	def loadQuest( self, player, subQuestID ):
		"""
		virtual method.
		执行任务实际处理
		"""
		tasks = self.loadTasks_( player, subQuestID )
		if tasks is None:
			# 如果出了问题，可以给玩家任务，但是要给一个新的任务
			self.accept( player )
			ERROR_MSG( "生成保存的环任务时出错，任务ID为%s，子任务ID为%s" % ( self._id, subQuestID ) )
			return
		for script in self.beforeAccept_:
			script.do( player, tasks )

		player.questAdd( self, tasks )


# $Log: not supported by cvs2svn $
# Revision 1.40  2008/08/07 08:58:24  zhangyuxing
# 修改提交任务的参数处理。newTaskBegin 增加任务tasks作为参数
#
# Revision 1.39  2008/07/31 09:24:50  zhangyuxing
# 去掉混杂的环任务逻辑，另外一个类单独处理
#
# Revision 1.38  2008/07/31 04:01:26  zhangyuxing
# 模式匹配错误处理
#
# Revision 1.37  2008/07/31 03:13:02  zhangyuxing
# 修改模板通配符 由 $ 改为 $p
#
# Revision 1.36  2008/07/30 07:30:42  zhangyuxing
# delQuestsRandomLog 改名字为 ： delRandomQuestRecord
#
# Revision 1.35  2008/07/30 05:54:36  zhangyuxing
# getGroupQuestDegree 改名为： getGroupCount
# getGroupQuestCount  改名为： getSubQuestCount
#
# Revision 1.34  2008/07/28 06:34:02  zhangyuxing
# 修改任务标题名字
#
# Revision 1.33  2008/07/28 01:11:43  zhangyuxing
# 组奖励的部分处理
#
# Revision 1.32  2008/07/19 08:15:28  zhangyuxing
# 修改 self.questID 使用错误
#
# Revision 1.31  2008/07/19 08:02:08  zhangyuxing
# 给isTasksOk 家一个参数
#
# Revision 1.30  2008/07/19 07:05:29  zhangyuxing
# 修正 self.freeCount 的BUG
#
# Revision 1.29  2008/07/19 01:37:26  zhangyuxing
# 修改背包满而导致接任务失败的BUG
#
# Revision 1.28  2008/07/14 04:35:35  zhangyuxing
# 加入等级变化，任务完成查询
#
# Revision 1.27  2008/07/09 04:13:35  wangshufeng
# 如果玩家不满足接任务条件，对应不同的状态值输出不同的提示信息。
#
# Revision 1.26  2008/07/09 03:18:02  zhangyuxing
# 增加isTasksOk，判断任务是否有效。
#
# Revision 1.25  2008/07/08 08:57:52  zhangyuxing
# 组队奖励BUG修改
#
# Revision 1.24  2008/06/27 01:14:00  zhangyuxing
# no message
#
# Revision 1.23  2008/06/18 04:01:56  zhangyuxing
# no message
#
# Revision 1.22  2008/06/03 02:43:20  zhangyuxing
# 修改 参数填写错误。
#
# Revision 1.21  2008/05/06 02:47:51  zhangyuxing
# 加入先判断奖品是否为NONE，在往列表中插入的判断
#
# Revision 1.20  2008/04/02 09:32:49  zhangyuxing
# 修改了次数奖励引起错误的BUG
#
# Revision 1.19  2008/04/01 05:22:01  zhangyuxing
# 加入取消任务flags
#
# Revision 1.18  2008/03/28 03:47:21  zhangyuxing
# 修改放弃任务的放弃方式
#
# Revision 1.17  2008/03/28 03:40:42  zhangyuxing
# 修改放弃任务的放弃方式
#
# Revision 1.16  2008/02/13 02:37:04  zhangyuxing
# 修改简单错误
#
# Revision 1.15  2008/02/01 04:01:07  zhangyuxing
# 修改简单BUG
#
# Revision 1.14  2008/01/30 02:51:01  zhangyuxing
# 修改简单BUG
#
# Revision 1.13  2008/01/25 07:29:35  zhangyuxing
# 增加子任务标题描述
#
# Revision 1.12  2008/01/18 06:34:12  zhangyuxing
# 增加：加入固定次数奖励处理
#
# Revision 1.11  2008/01/11 06:52:10  zhangyuxing
# 增加任务样式 self._style
#
# Revision 1.10  2008/01/09 03:23:30  zhangyuxing
# 从新处理了随机组任务的所有方法和功能。
#
# Revision 1.9  2007/11/02 03:56:48  phw
# QuestTasksDataType -> QuestDataType
# method removed: gossipPrebegin()
#
# Revision 1.8  2007/06/19 08:46:46  huangyongwei
# 任务状态的定义由原来的 csstatus 中转换到 csdefine 中
#
# Revision 1.7  2007/06/14 10:18:31  huangyongwei
# 重新整理了宏定义
#
# Revision 1.6  2007/06/14 10:03:28  huangyongwei
# 重新整理了宏定义
#
# Revision 1.5  2007/06/11 08:53:15  kebiao
# 		self. _id = id
#
# To：
# 		self._id = id
#
# Revision 1.4  2007/05/05 08:19:32  phw
# whrandom -> random
#
# Revision 1.3  2007/02/07 07:05:54  kebiao
# 去掉发送多选一奖励部分
#
# Revision 1.2  2006/08/02 08:13:35  phw
# 接口更名：
# 	reward() --> reward_()
#
# Revision 1.1  2006/03/27 07:39:26  phw
# no message
#
#