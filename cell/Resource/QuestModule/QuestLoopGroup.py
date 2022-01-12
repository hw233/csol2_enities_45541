# -*- coding: gb18030 -*-
#
# $Id $

"""
随机任务模块
"""

import csdefine
import cschannel_msgs
import ShareTexts as ST
import csstatus
import Language
from QuestRandomGroup import *
from QuestDataType import QuestDataType
from QuestRandomRecordType import QuestRandomRecordType
import random
from string import Template
import QTReward
import QTTask
import ECBExtend
import time


class QuestLoopGroup( QuestRandomGroup ):
	def __init__( self ):
		QuestRandomGroup.__init__( self )
		self._style = csdefine.QUEST_STYLE_LOOP_GROUP	# 环任务样式
		self._sExpData = {}								# 秒经验信息

	def init( self, section ):
		"""
		"""
		QuestRandomGroup.init( self, section )
		self.loadSexpDatas( "config/quest/QuestLoopDatas/QuestLoopDatas.xml" )
		#单次完成时间
		self._finishTime = section.readInt("eachtime") * 60

		#环任务经验奖励
		param1 = self._sExpData
		param2 = section.readString("relationRate")	# 双倍经验组数
		if len( param2 ) != 0:
			self._expReward = QTReward.createReward( "QTRewardRelationExp" )
			#self._rateExp_times = float(rateList[0])						#次数比例
			#self._rateExp_groups = float(rateList[1])						#组数比例
			#self._rateExp_level = float(rateList[2])						#等级比例
			#self._rateExp_baseExp = int(rateList[3])						#基础经验
			#self._rateExp_doubleGroups = int(rateList[4])					#双倍经验组数
			self._expReward.init( param1, int( param2 ) )
			self._expPetReward = QTReward.createReward( "QTRewardRelationPetExp" )
			self._expPetReward.init( param1, int( param2 ) )
		else:
			self._expReward = None
			self._expPetReward = None

	def getCountTitle( self, player ):
		count = player.getSubQuestCount( self._id )
		groupCount = player.getGroupQuestCount( self._id )
		return cschannel_msgs.QUEST_INFO_44%(groupCount+1, count+1)

	def loadSexpDatas( self, configPath ):
		"""
		加载掉落数量信息总表
		"""
		section = Language.openConfigSection( configPath )
		assert section is not None, "open %s false." % configPath
		for node in section.values():
			questLevel = node.readInt( "level" )
			questSecondExp = node.readFloat( "sExp" )
			self._sExpData[ questLevel ] = questSecondExp

		# 清除缓冲
		Language.purgeConfig( configPath )

	def getRewardsDetail( self, player ):
		"""
		获得奖励描述细节（子任务）
		@param      player: instance of Role Entity
		@type       player: Entity
		"""
		tempList = QuestRandomGroup.getRewardsDetail( self, player )

		#环任务经验处理
		if self._expReward:
			r = self._expReward.transferForClient( player, self._id )
			tempList.append( r )
		if self._expPetReward:
			r = self._expPetReward.transferForClient( player, self._id )
			tempList.append( r )
		return tempList


	def reward_( self, player, rewardIndex = 0 ):
		"""
		给予任务完成奖励（子任务）
		@param      player: instance of Role Entity
		@type       player: Entity
		@rtype: BOOL
		"""
		if self._expReward:
			self._expReward.do( player, self._id )
		if self._expPetReward:
			self._expPetReward.do( player, self._id )
		return QuestRandomGroup.reward_( self, player, rewardIndex )


	def abandoned( self, player, flags ):
		"""
		放弃任务
		重置单组任务记录
		"""
		#if flags != csdefine.QUEST_REMOVE_FLAG_NPC_CHOOSE:
		#	player.statusMessage( csstatus.ROLE_QUEST_RANDOM_GROUP_ABANDON_ERROR )
		#	return
		player.setGroupQuestRecorded( self._id, False )
		if not player.checkStartGroupTime( self._id ):
			# 随机任务每天的重置
			player.resetGroupQuest( self._id )
		else:
			player.addFailedGroupQuest( self._id )

		tasks = player.getQuestTasks( self._id )
		giveItems = tasks.query( "giveItemIDs", [] )
		for itemID in giveItems:
			item = player.findItemFromNKCK_( itemID )
			if item is not None:
				player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_ABANDONEDQUESTLOOP )
		return Quest.abandoned( self, player, flags )

	def addChild( self, questID, quest ):
		"""
		加一个随机任务到随机任务集合中
		"""
		self._quest_set[questID] = quest
		if self._finishTime != 0:
			instance = QTTask.QTTaskTime( questID % 10000,self._finishTime )
			quest.tasks_[instance.index] =  instance

	def onComplete( self, player ):
		"""
		任务提交完成通知
		"""
		if not player.checkStartGroupTime( self._id ) and not player.isGroupQuestRecorded( self._id ):
			# 随机任务每天的重置(不同的日期 and 不是读取的环任务记录)
			player.resetGroupQuest( self._id )

		count = player.getSubQuestCount( self.getID() ) #任务次数
		if count <= self._group_count:
			#self.accept( player )
			player.setTemp( "newQuestAddID", self.getID() )
			player.addTimer( 0.5, 0.0, ECBExtend.ADD_NEW_QUEST_CBID )

	def getRepeatMoney( self ):
		"""
		"""
		return 0


	def beforeGroupAccept( self, player ):
		"""
		virtual method.
		执行接组任务判断
		"""
		#if not player.groupQuestSavedAndFailedProcess( self._id ):
		#	return False


		if not player.checkStartGroupTime( self._id ) and not player.isGroupQuestRecorded( self._id ):		# 随机任务每天的重置
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
				if not player.checkStartGroupTime( self._id ):						#随机任务每天的重置
					player.resetGroupQuest( self._id )
				else:
					player.statusMessage( csstatus.ROLE_QUEST_GROUP_ENOUGH )
					return False

		if player.getSubQuestCount( self._id ) == 0:								#如果又回到了一组的第一个随机任务（进行押金处理）
			if player.money < self._deposit:										#押金判断
				player.statusMessage( csstatus.ROLE_QUEST_DEPOSIT_NOT_ENOUGH )
				return False
			player.payQuestDeposit( self._id, self._deposit )


		return True



	def onAccept( self, player, tasks ):
		"""
		virtual method.
		执行任务实际处理
		"""
		if not player.has_randomQuestGroup( self._id ): 						#增加随机任务记录判断
			record = QuestRandomRecordType()
			record.init( self._id )
			record.reset()
			player.addRandomLogs( self._id, record )

		taskType = 0
		for i in tasks.getTasks().itervalues():
			if i.getType() != csdefine.QUEST_OBJECTIVE_TIME:
				taskType = i.getType()
				break

		for i in player.failedGroupQuestList:
			if str( self._id ) == i.split(':')[1] and i.split(':')[0] == str( time.localtime()[2] ):
				# 如果是重新接取的环任务，要扣钱
				money = int( ( player.level * 300 * ( player.getGroupQuestCount( self._id ) + 1 ) ) ** 1.2 )
				player.payMoney( money, csdefine.CHANGE_MONEY_REACCEPTLOOPQUEST )
				player.failedGroupQuestList.remove( i )		# 重新领取环任务后，把该任务从当天失败的环任务列表中清除

		player.setRandomLogsTaskType( self._id, taskType )

		QuestRandomGroup.onAccept( self, player, tasks )


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

		sameType_temp_set = []  #与前一个任务目标不同的任务
		if player.has_randomQuestGroup( self.getID() ):
			taskType = player.getRandomLogsTaskType( self.getID() )
			if taskType != 0:
				for i in temp_set:
					for e in player.getQuest(i).tasks_:
						if player.getQuest(i).tasks_[e].getType() == taskType:
							sameType_temp_set.append( i )

		if len(sameType_temp_set) != len(temp_set):
			for i in sameType_temp_set:
				temp_set.remove(i)

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


	def gossipDetail( self, player, issuer = None ):
		"""
		任务故事内容描述对白；
		显示此对白后就可以点“accept”接任务了；
		如果issuer为None则表示任务可能是从物品触发或player共享得来
		"""
		if issuer:	targetID = issuer.id
		else:		targetID = 0

		player.questAccept( player.id, self._id, issuer.id )
		player.endGossip( issuer )

	def getLevel( self, player = None ):
		"""
		取得任务等级
		"""
		if player == None:
			return self._level
		return player.level

	def checkRequirement( self, player ):
		"""
		virtual method.
		判断玩家的条件是否足够接当前任务。
		@return: 如果达不到接任务的要求则返回False。
		@rtype:  BOOL
		"""
		reAcceptValid = False
		alreadyStored = player.recordQuestsRandomLog.has_randomQuestGroup( self._id )
		for i in player.failedGroupQuestList:
			if str( self._id ) == i.split(':')[1] and i.split(':')[0] == str( time.localtime()[2] ):
				reAcceptValid = True

		return ( not reAcceptValid ) and QuestRandomGroup.checkRequirement( self, player ) and not alreadyStored


	def complete( self, player, rewardIndex, codeStr = "" ):
		"""
		交任务
		交环任务需要背包有两个空位
		"""
		if player.getNormalKitbagFreeOrderCount() < 2:
			player.statusMessage( csstatus.ROLE_QUEST_GIVE_FREE_BLANK )
			return

		QuestRandomGroup.complete( self, player, rewardIndex, codeStr )
	
	def isTimeOut( self, player, questID ):
		"""
		环任务是否超时
		"""
		tasks = player.getQuestTasks( questID ).getTasks()
		timeTask = None
		for task in tasks.values():
			if task.getType() == csdefine.QUEST_OBJECTIVE_TIME:
				timeTask = task
				break
		
		return not( timeTask and timeTask.isCompleted( None ) )
