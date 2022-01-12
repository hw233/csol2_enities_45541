# -*- coding: gb18030 -*-
#
# $Id: Quest.py,v 1.90 2008-08-18 01:38:35 zhangyuxing Exp $


"""
普通任务模块
"""

import csdefine
from bwdebug import *
import csstatus
import csconst
from QuestDataType import QuestDataType
from QTReward import *
from QTTask import *
from ObjectScripts.GameObjectFactory import g_objFactory
from Statistic import Statistic
g_Statistic = Statistic.instance()

import QuestTaskDataType
import QTReward
import QTRequirement
import QTCompleteRule
import QTScript
from Resource import QuestsTrigger
import ItemTypeEnum
import sys

class Quest:
	def __init__( self ):
		self._title = ""
		self.requirements_ = []						# list of QTRequirement; 接任务条件
		self.beforeAccept_ = []						# list of scripts; 接任务时执行一些脚本
		self.afterComplete_ = []					# list of scripts; 完成任务时执行一些脚本
		self.taskComplete_ = {}						# dict of scripts; 任务目标完成时做点事情
		self.tasks_ = {}							# dict of QTTask; 任务达成目标
		self.rewards_ = []							# list of QTReward; 任务奖励
		self.rewardsFixedItem_ = None				# 固定物品奖励
		self.rewardsRoleLevelItem_ = None				# 变化等级物品奖励
		self.rewardsChooseItem_ = None				# 多物品选一奖励
		self.rewardsRandItem_ = None				# 随机物品奖励
		self.rewardsFixedRandItem_ = None			# 固定随机物品奖励
		self.rewardsQuestPartCompleted_ = None
		self.rewardsFixedItemFromClass_ = None		# 根据玩家职业给予不同的物品奖励

		self._id = 0								# questID；uint16 1 - 65535
		self.repeatable_ = False					# 任务是否可以重复完成
		self._start_objids = []						# 任务的开始者列表标识；注：此表示的是npc一组的entityID，下面表示的是物品ID，两者只可有一个；
		self._start_itemID = ""						# 任务的开始者标识（物品）
		self._finish_objids = []					# 任务的结束者列表标识
		self._questBoxsDict = {}					# 任务箱子字典
		self._level = 0								# 任务等级
		self._can_share = 0							# 是否能共享
		self._next_quest = 0						# 表示当前任务完成后可以被激活的下一个任务
		self._type =  csdefine.QUEST_TYPE_NONE		# 任务类别，通常与self._acceptMaxCount配合用于限制某一类任务的接受数量
		self._acceptMaxCount = 0					# 允许接受self._type类型任务的上限 比如(允许玩家questsTable存在 宝藏任务最多_acceptMaxCount个 )
		self._style = csdefine.QUEST_STYLE_NORMAL	# 任务样式

		self._msg_prebegin		= ""
		self._msg_prebegin_menu = None
		
		self._completeRule = None					# 任务完成规则实例
		self._completeRuleType = 0

	def init( self, section ):
		"""
		virtual method.
		@param section: 任务配置文件section
		@type  section: pyDataSection
		"""
		formatStr = lambda string : "".join( [ e.strip( "\t " ) for e in string.splitlines(True) ] )

		self._id = section["id"].asInt
		self.repeatable_ = section.readInt( "repeatable" )

		self._title = section.readString( "title" )
		self._level = section.readInt( "level" )

		objIdsStr = section.readString( "start_by" )
		self._start_objids = objIdsStr.split('|')

		self._start_itemID = section.readInt( "start_by_item" )
		objIdsStr = section.readString( "finish_by" )
		self._finish_objids = objIdsStr.split('|')

		#self._next_quest = section.readInt( "next_quest" )
		self._next_quest = section.readString( "next_quest" ).split(";")
		self._can_share = section.readInt( "can_share" )	# 是否能共享

		if section.has_key("quest_box"):
			for sec in section["quest_box"].values():
				self._questBoxsDict[ sec["id"].asString] = sec["index"].asInt

		if section.has_key( "requirements" ):
			for sec in section["requirements"].values():
				instance = QTRequirement.createRequirement( sec.readString( "type" ) )
				instance.init( sec )
				self.requirements_.append( instance )

		if section.has_key( "before_accept" ):
			for sec in section["before_accept"].values():
				if len(sec.readString( "type" )) > 8 and sec.readString('type')[0:8] == 'QTSAfter':
					continue
				instance = QTScript.createScript( sec.readString( "type" ) )
				instance.init( sec )
				self.beforeAccept_.append( instance )

		extSection = section["before_accept_give_items"]
		if extSection and len( extSection ) > 0:
			instance = QTScript.QTSGiveItems()
			instance.init( extSection )
			self.beforeAccept_.append( instance )

		if section.has_key( "tasks" ):
			for sec in section["tasks"].values():
				instance = QuestTaskDataType.createTask( sec.readString( "type" ) )
				instance.init( sec )
				self.tasks_[instance.index] =  instance

		if section.has_key( "task_complete" ):
			for sec in section["task_complete"].values():
				taskIndex = sec.readString( "taskIndex" )
				instance = QTScript.createScript( sec.readString( "type" ) )
				instance.init( sec )
				if taskIndex in self.taskComplete_.keys():
					self.taskComplete_[taskIndex].append( instance )
					continue
				self.taskComplete_[taskIndex]= [instance]

		if section.has_key( "after_complete" ):
			for sec in section["after_complete"].values():
				instance = QTScript.createScript( sec.readString( "type" ) )
				instance.init( sec )
				self.afterComplete_.append( instance )
		
		if section.has_key( "complete_rule" ):
			instance = QTCompleteRule.createRule( section.readInt( "complete_rule" ) )		# 不填默认为0
			self._completeRule = instance
			self._completeRuleType = section.readInt( "complete_rule" )
		else:	# 没有配置的情况
			instance = QTCompleteRule.createRule( 0 )
			self._completeRule = instance

		if section.has_key( "rewards" ):
			for sec in section["rewards"].values():
				typeStr = sec.readString( "type" )
				if typeStr == "QTRewardRelationExp":
					typeStr = "QTRewardExp"
				instance = QTReward.createReward( typeStr )
				instance.init( self, sec )
				self.rewards_.append( instance )

		extSection = section["rewards_fixed_item"]
		if extSection and len( extSection ) > 0:
			self.rewardsFixedItem_ = QTRewardItems()
			self.rewardsFixedItem_.init( self, extSection )

		extSection = section["rewards_role_level_item"]
		if extSection and len( extSection ) > 0:
			self.rewardsRoleLevelItem_ = QTRewardItemsFromRoleLevel()
			self.rewardsRoleLevelItem_.init( self, extSection )

		extSection = section["rewards_choose_item"]
		if extSection and len( extSection ) > 0:
			self.rewardsChooseItem_ = QTRewardChooseItems()
			self.rewardsChooseItem_.init( self, extSection )

		extSection = section["rewards_random_item"]
		if extSection and len( extSection ) > 0:
			self.rewardsRandItem_ = QTRewardRndItems()
			self.rewardsRandItem_.init( self, extSection )
		
		extSection = section["rewards_fixed_random_item"]
		if extSection and len( extSection ) > 0:
			self.rewardsFixedRandItem_ = QTRewardFixedRndItems()
			self.rewardsFixedRandItem_.init( self, extSection )
		
		extSection = section["rewards_quest_part_completed"]
		if extSection and len( extSection ) > 0:
			self.rewardsQuestPartCompleted_ = QTRewardQuestPartCompleted()
			self.rewardsQuestPartCompleted_.init( self, extSection )

		extSection = section["rewards_fixed_item_from_class"]
		if extSection and len( extSection ) > 0:
			self.rewardsFixedItemFromClass_ = QTRewardItemsFromClass()
			self.rewardsFixedItemFromClass_.init( self, extSection )
			
		self.addToQuestBox()

	def getID( self ):
		"""
		取得任务ID号(questID)
		"""
		return self._id

	def getTitle( self ):
		return self._title

	def getLevel( self, player = None ):
		"""
		取得任务等级
		"""
		return self._level

	def getType( self ):
		"""
		取得任务类别
		"""
		return self._type

	def setType( self, maxAcceptCount, questType ):
		"""
		提供这个接口设置任务类别并且明确要求设置最大接收本类型个数
		@param questType:		# 任务类别
		@param maxAcceptCount:	# 允许接受self._type类型任务的上限 比如(允许玩家questsTable存在 宝藏任务最多_acceptMaxCount个 ) 默认为0
		"""
		self._type			 =  questType
		self._acceptMaxCount = maxAcceptCount

	def getObjectIdsOfFinish( self ):
		"""
		取得任务完成的目标标识
		"""
		return self._finish_objids

	def getObjectIdsOfStart( self ):
		"""
		取得任务开始的目标标识
		"""
		return self._start_objids

	def getQuestBoxsDict( self ):
		"""
		取得获得任务物品的箱子
		"""
		return self._questBoxsDict


	def getNextQuest( self, player ):
		"""
		取得下一个任务的ID( if has )
		"""
		#return self._next_quest
		if len( self._next_quest ) > 1:
			if hasattr( player, "getClass" ) and len( self._next_quest ) == 4:
				if player.getClass() == csdefine.CLASS_FIGHTER:
					return int( self._next_quest[ 0 ] )
				elif player.getClass() == csdefine.CLASS_SWORDMAN:
					return int( self._next_quest[ 1 ] )
				elif player.getClass() == csdefine.CLASS_ARCHER:
					return int( self._next_quest[ 2 ] )
				elif player.getClass() == csdefine.CLASS_MAGE:
					return int( self._next_quest[ 3 ] )
			else:
				return int( self._next_quest[ 0 ] )
		elif self._next_quest[ 0 ] != "" :		#因为readString时为空的话会返回""，再split会变成[""]
			return int( self._next_quest[ 0 ] )
		else:
			return 0

	def getRewardsDetail( self, player ):
		"""
		获得奖励描述细节
		"""
		r = []
		for reward in self.rewards_:
			r.append( reward.transferForClient( player, self.getID() ) )
		if self.rewardsFixedItem_:
			r.append( self.rewardsFixedItem_.transferForClient( player, self.getID() ) )
		if self.rewardsRoleLevelItem_:
			r.append( self.rewardsRoleLevelItem_.transferForClient( player, self.getID() ) )
		if self.rewardsChooseItem_:
			r.append( self.rewardsChooseItem_.transferForClient( player, self.getID() ) )
		# 策划说随机奖励不显示出来给玩家看，但为防止以后又要要求显示，所以要保留
		if self.rewardsRandItem_:
			r.append( self.rewardsRandItem_.transferForClient( player, self.getID() ) )
		if self.rewardsFixedRandItem_:
			r.append( self.rewardsFixedRandItem_.transferForClient( player, self.getID() ) )
		if self.rewardsQuestPartCompleted_:
			r.append( self.rewardsQuestPartCompleted_.transferForClient( player, self.getID() ) )
		if self.rewardsFixedItemFromClass_:
			r.append( self.rewardsFixedItemFromClass_.transferForClient( player, self.getID() ) )
		return r

	def getSubmitDetail( self, player ):
		"""
		获得提交任务物品的描述
		"""
		for task in self.tasks_.itervalues():
			if task.getType() in csconst.QUEST_OBJECTIVE_SUBMIT_TYPES or task.getType() == csdefine.QUEST_OBJECTIVE_SUBMIT_PICTURE or task.getType() == csdefine.QUEST_OBJECTIVE_SUBMIT_CHANGE_BODY or task.getType() == csdefine.QUEST_OBJECTIVE_SUBMIT_DANCE:
					return task.getSubmitInfo()
		return {}

	def canShare( self ):
		"""
		判断当前任务是否能共享

		@rtype: BOOL
		"""
		return bool( self._can_share )

	def sendCompleteMsg( self , player, rewardStrList ):
		"""
		完成任务通知
		@param      player: instance of Role Entity
		@type       player: Entity
		@param rewardStrList: 所有奖励的项目名称列表
		@type  rewardStrList: list
		"""
		rewardstring =""
		endsign = "!"
		if rewardStrList != []:
			rewardstring = cschannel_msgs.CELL_QUEST_1
			endsign = "]"

		sendinfo = cschannel_msgs.CELL_QUEST_2 % self._title
		sendinfo += rewardstring
		count = len( rewardStrList )
		for s in rewardStrList:
			sendinfo += s
			count-= 1
			if count > 0:
				sendinfo += ","
		sendinfo += endsign
		player.statusMessage( csstatus.ROLE_QUEST_QUEST_INFO, sendinfo )

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
		if self.rewardsRoleLevelItem_:
			items.extend( self.rewardsRoleLevelItem_.getItems( player, self.getID() ) )
		if self.rewardsChooseItem_:
			items.extend( self.rewardsChooseItem_.getItems( player, self.getID() ) )
		if self.rewardsRandItem_:
			items.extend( self.rewardsRandItem_.getItems( player, self.getID() ) )
		if self.rewardsFixedRandItem_:
			items.extend( self.rewardsFixedRandItem_.getItems( player, self.getID() ) )
		if self.rewardsQuestPartCompleted_:
			items.extend( self.rewardsQuestPartCompleted_.getItems( player, self.getID() ) )
		if self.rewardsFixedItemFromClass_:
			items.extend( self.rewardsFixedItemFromClass_.getItems( player, self.getID() ) )
		if player.checkItemsPlaceIntoNK_( items ) == csdefine.KITBAG_NO_MORE_SPACE:
			player.statusMessage( csstatus.ROLE_QUEST_KITBAG_FULL_FOR_COMPLETE )
			return False
		if player.checkItemsPlaceIntoNK_( items ) == csdefine.KITBAG_ITEM_COUNT_LIMIT:
			player.statusMessage( csstatus.ROLE_QUEST_KITBAG_ITEM_LIMIT_FOR_COMPLETE )
			return False


		for reward in self.rewards_:
			if not reward.check( player, self.getID() ):
				return False

		# give all reward to player except item
		rewardInfoList = []
		for reward in self.rewards_:
			rewardInfoList.extend(reward.do( player, self.getID() ))

		# give item to player
		for item in items:
			tempItem = item.new()
			player.addItemAndRadio( tempItem , ItemTypeEnum.ITEM_GET_QUEST, reason = csdefine.ADD_ITEM_QUEST )
			
		if self.rewardsQuestPartCompleted_:				# 这种类型的奖励是复合类型的，上面只给了物品奖励，所以还要do一下。
			rewardInfoList.extend( self.rewardsQuestPartCompleted_.do( player, self.getID() ) )

		#self.sendCompleteMsg( player , rewardInfoList )
		return True

	def checkRequirement( self, player ):
		"""
		virtual method.
		判断玩家的条件是否足够接当前任务。
		@return: 如果达不到接任务的要求则返回False。
		@rtype:  BOOL
		"""
		for requirement in self.requirements_:
			if not requirement.query( player ):
				return False
		return True
		
	def checkComplete( self, player ):
		"""
		判断玩家是否完成任务
		"""
		if self._completeRule:
			return self._completeRule.checkComplete( player, self.getID() )
		return False

	def accept( self, player ):
		"""
		virtual method.
		接任务，如果接任务失败了则返回False（例如玩家背包满了放不下任务道具）。

		@param     player: instance of Role Entity
		@type      player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		tasks = self.beforeAccept( player )
		if  tasks is None:
			return False

		self.onAccept( player, tasks )
		
		return True

	def baseAccept( self, player ):
		"""
		virtual method.
		接任务，如果接任务失败了则返回False（例如玩家背包满了放不下任务道具）。

		@param     player: instance of Role Entity
		@type      player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		tasks = self.beforeAccept( player )
		if  tasks is None:
			return False

		self.onAccept( player, tasks )

		return True


	def beforeAccept( self, player ):
		"""
		virtual method.
		执行接任务的判断
		"""
		if player.questIsFull():
			player.statusMessage( csstatus.ROLE_QUEST_QUEST_BAG_FULL )
			return None

		if self._acceptMaxCount > 0:
			if len( player.findQuestByType( self._type ) ) > self._acceptMaxCount:
				return None

		for script in self.beforeAccept_:
			if not script.query( player ):
				return None

		return self.newTasks_( player )


	def onAccept( self, player, tasks ):
		"""
		virtual method.
		执行任务实际处理
		"""
		for script in self.beforeAccept_:
			script.do( player, tasks )

		player.questAdd( self, tasks )

	def onTaskCompleted( self, player, taskIndex ):
		"""
		virtual method.
		某个任务目标或者多个任务目标完成
		"""
		questID = self.getID()
		tasks = player.getQuestTasks( questID )
		for indexStr, scripts in self.taskComplete_.iteritems():
			indexList = [int( i ) for i in indexStr.split( ";" )]
			if taskIndex in indexList and player.tasksIsCompleted( questID, indexList ):
				for script in scripts:
					script.do( player, tasks )

	def complete( self, player, rewardIndex, codeStr = "" ):
		"""
		virtual method.
		交任务。

		@param player: instance of Role Entity
		@type  player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		#player.setTemp( "questKitTote", kitTote )
		#player.setTemp( "questOrder", order )

		if player.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
			if player.getState() == csdefine.ENTITY_STATE_DEAD:
				player.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
			return False

		player.setTemp( "questTeam", True)
		self.setDecodeTemp( player, codeStr )
		if not self.query( player ) == csdefine.QUEST_STATE_FINISH:
			#player.removeTemp( "questKitTote" )
			#player.removeTemp( "questOrder" )
			self.removeDecodeTemp( player, codeStr )
			player.removeTemp( "questTeam" )
			return False

		player.setTemp( "RewardItemChoose" , rewardIndex )
		if not self.reward_( player, rewardIndex ):
			player.removeTemp( "RewardItemChoose" )
			#player.removeTemp( "questKitTote" )
			#player.removeTemp( "questOrder" )
			self.removeDecodeTemp( player , codeStr)
			player.removeTemp( "questTeam" )
			return False
		if not self.repeatable_:				# 只保存不可重复完成的任务
			player.recordQuestLog( self._id )	# 记录任务日志

		# after complete
		task = player.getQuestTasks( self.getID() )
		for e in self.afterComplete_:
			e.do( player, task )

		player.removeTemp( "RewardItemChoose" )
		player.removeTemp( "tongDartMembers" )
		#player.removeTemp( "questKitTote" )
		#player.removeTemp( "questOrder" )
		#self.removeDecodeTemp( player )
		player.removeTemp( "questTeam" )
		player.removeQuestSlotsInfo( self._id )
		player.onQuestComplete( self._id )
		player.statusMessage( csstatus.ROLE_QUEST_COMPLETE, self._title )

		# 统计模块新增任务完成次数
		g_Statistic.addQuestDayStat( player, self._id )
		return True

	def setDecodeTemp( self, player, codeStr ):
		"""
		设置编码字符串临时变量
		"""
		for task in player.getQuest(self.getID()).tasks_.itervalues():
			task.setPlayerTemp( player, codeStr )


	def removeDecodeTemp( self, player, codeStr ):
		"""
		删除编码字符串临时变量
		"""
		for task in player.getQuest(self.getID()).tasks_.itervalues():
			task.removePlayerTemp( player )

	def abandoned( self, player, flags ):
		"""
		virtual method.
		任务被放弃，对玩家做点什么事情。

		@param player: instance of Role Entity
		@type  player: Entity
		@param flags : 放弃类型
		@return: None
		"""
		for e in self.afterComplete_:
			e.onAbandoned( player, player.questsTable[self.getID()] )

		# to do, 本来是用来回收任务物品的,但理论似乎和实践有了那么丁点比较麻烦的差异,因此暂时没有实现
		return True

	def newTasks_( self, player ):
		"""
		virtual method. call by accept() method.
		开始新任务，产生一个与当前任务相关的任务目标实例

		@return: instance of QuestDataType or derive it；如果任务目标产生失败则必须返回None
		@rtype:  QuestDataType/None
		"""
		tasks = QuestDataType()
		tasks.setQuestID( self._id )
		tasks.set( "style", self._style )			#任务样式存储
		tasks.set( "type", self._type )				#任务类型存储

		tempTasks = {}
		for e in self.tasks_:
			tempTasks[e] = self.tasks_[e].newTaskBegin(player, tasks )
		tasks.setTasks( tempTasks )
		return tasks

	def getStyle( self ):
		"""
		"""
		return self._style

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
			if self.checkComplete( player ):
				return csdefine.QUEST_STATE_FINISH						# 任务目标已完成
			else:
				return csdefine.QUEST_STATE_NOT_FINISH					# 任务目标未完成
		else:
			# 没有接该任务
			if self.checkRequirement( player ):
				return csdefine.QUEST_STATE_NOT_HAVE					# 可以接但还未接该任务
			else:
				return csdefine.QUEST_STATE_NOT_ALLOW					# 不够条件接该任务

	def addToQuestBox( self ):
		"""
		处理任务箱子
		"""
		QuestBoxsDict = self.getQuestBoxsDict()
		for QuestBoxID in QuestBoxsDict:
			QuestBoxNpc = g_objFactory.getObject( QuestBoxID )
			if not QuestBoxNpc:
				ERROR_MSG( self.getID(), "QuestBox not found.", QuestBoxID )
			else:
				assert QuestBoxNpc.getEntityType() != "NPCObject","Wrong QuestBoxID is %s" % QuestBoxID #临时修改，找出被策划配置为QuestBox导致报错的NPCObject，grl
				index = QuestBoxsDict[ QuestBoxID ]
				QuestBoxNpc.addQuestTask( self.getID(), index )


	def gossipDetail( self, playerEntity, issuer = None ):
		"""
		任务故事内容描述对白；
		显示此对白后就可以点“accept”接任务了；
		如果issuer为None则表示任务可能是从物品触发或player共享得来
		"""
		if issuer:	targetID = issuer.id
		else:		targetID = 0
		playerEntity.sendQuestRewards( self._id, self.getRewardsDetail( playerEntity ) )
		playerEntity.sendQuestDetail( self._id,  self.getLevel( playerEntity ), targetID )

	def gossipIncomplete( self, playerEntity, issuer ):
		"""
		任务目标未完成对白
		"""
		if issuer:	targetID = issuer.id
		else:		targetID = 0
		playerEntity.sendQuestIncomplete(  self._id, self.getLevel( playerEntity ), targetID )
		playerEntity.statusMessage( csstatus.ROLE_QUEST_INCOMPLETE )

	def gossipPrecomplete( self, playerEntity, issuer ):
		"""
		任务目标已完成对白
		"""
		if issuer:	targetID = issuer.id
		else:		targetID = 0
		playerEntity.sendQuestRewards( self._id, self.getRewardsDetail( playerEntity ) )
		playerEntity.sendObjectiveDetail( self._id, playerEntity.questsTable[self._id].getObjectiveDetail( playerEntity ) )
		playerEntity.sendQuestSubmitBlank( self._id, self.getSubmitDetail( playerEntity ) )
		playerEntity.sendQuestPrecomplete( self._id, self.getLevel( playerEntity ), targetID )

	def gossipComplete( self, playerEntity, issuer ):
		"""
		交任务后对白
		"""
		if issuer:
			targetID = issuer.id
		else:
			targetID = 0
		playerEntity.sendQuestComplete( self._id, self.getLevel( playerEntity ), targetID )

	def sendQuestLog( self, playerEntity, questLog ):
		"""
		发送任务日志

		@param questLog: 任务日志; instance of QuestDataType
		"""
		playerEntity.client.onQuestLogAdd( self._id, self._can_share, self._completeRuleType, questLog, self.getLevel( playerEntity ), self.getRewardsDetail(playerEntity) )

	def startGossip( self, player, issuer, dlgKey ):
		"""
		virtual method.
		任务对话

		@param player: 玩家entity
		@param issuer: entity
		@param dlgKey: String; 对话关键字
		"""
		pass

	def finishGossip( self, player, issuer, dlgKey ):
		"""
		virtual method.
		任务对话

		@param player: 玩家entity
		@param issuer: entity
		@param dlgKey: String; 对话关键字
		"""
		pass

	def onPlayerLevelUp( self, player ):
		"""
		"""
		player.questAdd( self, self.newTasks_( player ) )

		QuestsTrigger.SendQuestMsg( player, self._id )

	def isTasksOk( self, playerEntity ):
		"""
		检查任务目标是否有效
		"""
		return True

	def onComplete( self, player ):
		"""
		任务提交完成通知
		"""
		return

	def hasOption( self ):
		"""
		"""
		return True

	def onRemoved( self, playerEntity ):
		"""
		"""
		pass

	def getRewardDetailFromRewardQuest( self, player ):
		"""
		获得悬赏任务奖励描述细节
		"""
		r = []
		for reward in self.rewards_:
			if reward.type() == csdefine.QUEST_REWARD_MONEY_FROM_REWARD_QUEST_QUALITY or reward.type() == csdefine.QUEST_REWARD_EXP_FROM_REWARD_QUEST_QUALITY:
				r.append( reward.transferForClient( player, self.getID() ) )
		return r

	def acceptRewardQuest( self, player ):
		"""
		接受悬赏任务
		"""
		"""
		virtual method.
		接任务，如果接任务失败了则返回False（例如玩家背包满了放不下任务道具）。

		@param     player: instance of Role Entity
		@type      player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		tasks = self.beforeAccept( player )
		if  tasks is None:
			return False

		self.onRewardQuestAccept( player, tasks )
		
		return True

	def onRewardQuestAccept( self, player, tasks ):
		"""
		virtual method.
		执行任务实际处理
		"""
		for script in self.beforeAccept_:
			script.do( player, tasks )

		player.rewardQuestAdd( self, tasks )
		player.statusMessage( csstatus.ROLE_QUEST_QUEST_ACCEPTED,self._title )

