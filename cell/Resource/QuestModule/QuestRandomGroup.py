# -*- coding: gb18030 -*-
#
# $Id $

"""
�������ģ��
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
		self._quest_set = {}						# ������񼯺� key is questID, value is instance of Quest
		self._pattern_set = {}						# ��������ģʽ��� key is a type of patterns. value is the msg of a pattern
		self._group_count = 0						# һ������������Ŀ��Ҳ������ɶ�������������ս�����
		self._group_reward_set = {}					#���ս������ϣ����ݻ��ַּ�����Σ�
		self._count_rewards_set ={}					#�̶������������
		self._deposit_count = 0						#�ڼ����˻�Ѻ��
		self._deposit = 0							#�������Ѻ��
		self._repeatTimePerDate = 0					#1�������������
		self._style = csdefine.QUEST_STYLE_RANDOM_GROUP	# ������ʽ

	def init( self, section ):
		"""
		"""
		Quest.init( self, section )

		self._group_count = section.readInt( "group_count" )
		self._deposit_count = section.readInt( "deposit_count" )
		self._deposit = 0 #Ѻ�����ȡ��
		self._repeatNeedMoney = section.readInt( "deposit" )
		self._repeatTimePerDate = section.readInt( "repeat_time_per_date" )
		self.repeatable_ = 1	# �����͵�����ǿ���������ظ���

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
		ִ�н�������ж�
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
		ִ�н��������ж�
		"""
		if not player.has_randomQuestGroup( self._id ): 					#������������¼�ж�
			record = QuestRandomRecordType()
			record.init( self._id )
			record.reset()
			player.addRandomLogs( self._id, record )

		if not player.checkStartGroupTime( self._id ) and not player.isGroupQuestRecorded( self._id ):
			# �������ÿ�������(��ͬ������ and ���Ƕ�ȡ�Ļ������¼)
			player.resetGroupQuest( self._id )

		if self._repeatTimePerDate <= player.getGroupQuestCount( self._id ) and player.isGroupQuestRecorded( self._id ):
			player.resetGroupQuest( self._id )
			player.setGroupQuestRecorded( self._id, False )

		if self._repeatTimePerDate <= player.getGroupQuestCount( self._id ): #�������ÿ�����������
			"""
			������ﵽ������ʱ������Ҫ����������������ǰ�Ĵ浵���񣬻��Ǿ��ǵ���Ļ�����
			����Ǵ浵�����򻹿��Լ��������������
			"""
			if not player.newDataGroupQuest( self._id ):
				player.statusMessage( csstatus.ROLE_QUEST_GROUP_ENOUGH )
				return False

		if player.getSubQuestCount( self._id ) == 0:								#����ֻص���һ��ĵ�һ��������񣨽���Ѻ����
			if player.money < self._deposit:									#Ѻ���ж�
				player.statusMessage( csstatus.ROLE_QUEST_DEPOSIT_NOT_ENOUGH )
				return False
			player.payQuestDeposit( self._id, self._deposit )


		return True



	def onAccept( self, player, tasks ):
		"""
		virtual method.
		ִ������ʵ�ʴ���
		"""
		Quest.onAccept( self, player, tasks )
		player.setGroupCurID( self._id, tasks.query("subQuestID") )


	def getCountTitle( self, player ):
		return self.getTitle()

	def getRewardsDetail( self, player ):
		"""
		��ý�������ϸ�ڣ�������
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
		��ý�������ϸ��
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
		����������ɽ�����������
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
		������������ɽ���
		����������Ľ�����������ұ�����λ���������Ǯ̫������⣬�Ͳ������
		@param      player: instance of Role Entity
		@type       player: Entity
		@param point: �������
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

		#player.client.addGroupRewardsInfo( self._id, r )#����Ҫ��Ϊ��client�������ս�������


	def getRewardsDict( self, point ):
		"""
		����ʺ����������ֵ���������ʵ��
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
		��������
		���õ��������¼
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
		���һ������������Ҫ�����ɵĴ���
		"""
		return self._group_count


	def newTasks_( self, player ):
		"""
		��ʼ�����񡣷���һ������ʵ�����������������������б��������ʺ���ҵ�����id��ʱ�б�������ʱid�б������ȡһ�����ء�
		@rtype: QuestDataType
		"""
		temp_set = []
		giveItemIDs = []
		for key in self._quest_set:
			if self._quest_set[key].fitPlayer( player ):	#�ҵ�һ���������ʺ���ҵ���Щ����
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

		tasks = self._quest_set[key].newTasks_( player )	#ȡ���������Ŀ��
		tasks.setQuestID( self._id )						#ʹ�ø������ID
		tasks.set( "subQuestID", key )						#�������ID�洢����չ������
		tasks.set( "style", self._style )			#������ʽ�洢
		tasks.set( "type", self._type )				#�������ʹ洢
		tasks.set( "giveItemIDs", giveItemIDs )		#���������Ʒ��ID

		return tasks


	def complete( self, player, rewardIndex, codeStr = "" ):
		"""
		������
		"""
		if player.getNormalKitbagFreeOrderCount( ) < 2:
			player.statusMessage( csstatus.ROLE_QUEST_NEED_TWO_FREE_BLANK )
			return

		tasks = player.getQuestTasks( self._id )
		subQuestID = tasks.query( "subQuestID" )

		if not self._quest_set[subQuestID].complete( player, rewardIndex, codeStr ):
			return

		if player.getSubQuestCount( self._id ) == self._deposit_count:	#���������Ĵ��������˻�Ѻ�����ʱ���˻�Ѻ��
			if not player.returnDeposit( self._id ):
				player.statusMessage( csstatus.CIB_MONEY_OVERFLOW )
				return

		if not self.reward_( player ):
			return

		self.doFixedCountRandomReward( player, player.getSubQuestCount( self._id ) ) #���й̶�������������

		if player.getSubQuestCount( self._id ) >= self.getGroupTotalCount():	#�����ɵĴ����Ƿ�ﵽһ��Ĵ����ж�
			point =player.takeGroupPoint( self._id )
			self.addGroupRewards( player, point )							#���ս���
			player.addGroupQuestCount( self._id )							#��������ɴ���
			player.resetSingleGroupQuest( self._id )						#���õ����¼����
			#player.delRandomQuestRecord( self._id )

		player.onQuestComplete( self.getID() )		#ʹ����ID

		# ͳ��ģ������������ɴ���
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
		����������������԰ף�
		��ʾ�˶԰׺�Ϳ��Ե㡰accept���������ˣ�
		���issuerΪNone���ʾ��������Ǵ���Ʒ������player�������
		"""
		if issuer:	targetID = issuer.id
		else:		targetID = 0
		if not player.has_quest( self._id ):		#��û�л���������֮ǰ���������������������������ȷ����
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
		��һ���������������񼯺���
		"""
		self._quest_set[questID] = quest

	def getPatternDetailMsg( self, type, paramsDict ):
		"""
		ȡ��һ��ģʽ�Ĺ����������ݶ԰�
		@param type: ����ģʽ����
		@type type: int
		"""
		return self._pattern_set[type]["msg_detail"].safe_substitute( paramsDict )


	def getPatternIncompleteMsg( self, type, paramsDict ):
		"""
		ȡ��һ��ģʽ������δ��ɶ԰�
		"""
		return self._pattern_set[type]["msg_incomplete"].safe_substitute( paramsDict )


	def getPatternPrecompleteMsg( self, type, paramsDict ):
		"""
		ȡ��һ��ģʽ����������ɶ԰�
		"""
		return self._pattern_set[type]["msg_precomplete"].safe_substitute( paramsDict )


	def getPatternQuestLogMsg( self, type, paramsDict ):
		"""
		ȡ��һ��ģʽ�ķ���������־
		"""
		return self._pattern_set[type]["msg_log_detail"].safe_substitute( paramsDict )


	def getPatternCompleteMsg( self, type, paramsDict ):
		"""
		ȡ��һ��ģʽ�Ľ�����԰�
		"""
		return self._pattern_set[type]["msg_complete"].safe_substitute( paramsDict )


	def getPatternObjectiveMsg( self, type, paramsDict ):
		"""
		ȡ��һ��ģʽ������Ŀ��԰�
		"""
		return self._pattern_set[type]["msg_objective"].safe_substitute( paramsDict )


	def gossipIncomplete( self, player, issuer ):
		"""
		����Ŀ��δ��ɶ԰ף�
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
		����Ŀ������ɶ԰�
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
		�������԰�
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
		����������־
		@param questLog: ������־; instance of QuestDataType
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
		�������Ŀ���Ƿ���Ч
		"""
		tasks = player.getQuestTasks( self._id )
		subQuestID = tasks.query( "subQuestID" )

		return self._quest_set.has_key( subQuestID )


	def onComplete( self, player ):
		"""
		�����ύ���֪ͨ
		"""
		if not player.checkStartGroupTime( self._id ) and not player.isGroupQuestRecorded( self._id ):
			# ����������
			player.resetGroupQuest( self._id )
		return
		#count = player.getSubQuestCount( self.getID() ) #�������
		#if count <= self._group_count:
		#	self.accept( player )


	def loadTasks_( self, player, subQuestID ):
		"""
		��ʼ�����񡣷���һ������ʵ�����������������������б��������ʺ���ҵ�����id��ʱ�б�������ʱid�б������ȡһ�����ء�
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

		tasks = self._quest_set[subQuestID].newTasks_( player )	#ȡ���������Ŀ��
		tasks.setQuestID( self._id )							#ʹ�ø������ID
		tasks.set( "subQuestID", subQuestID )					#�������ID�洢����չ������
		tasks.set( "style", self._style )						#������ʽ�洢
		tasks.set( "type", self._type )							#�������ʹ洢
		tasks.set( "giveItemIDs", giveItemIDs )					#���������Ʒ��ID

		return tasks

	def loadQuest( self, player, subQuestID ):
		"""
		virtual method.
		ִ������ʵ�ʴ���
		"""
		tasks = self.loadTasks_( player, subQuestID )
		if tasks is None:
			# ����������⣬���Ը�������񣬵���Ҫ��һ���µ�����
			self.accept( player )
			ERROR_MSG( "���ɱ���Ļ�����ʱ��������IDΪ%s��������IDΪ%s" % ( self._id, subQuestID ) )
			return
		for script in self.beforeAccept_:
			script.do( player, tasks )

		player.questAdd( self, tasks )


# $Log: not supported by cvs2svn $
# Revision 1.40  2008/08/07 08:58:24  zhangyuxing
# �޸��ύ����Ĳ�������newTaskBegin ��������tasks��Ϊ����
#
# Revision 1.39  2008/07/31 09:24:50  zhangyuxing
# ȥ�����ӵĻ������߼�������һ���൥������
#
# Revision 1.38  2008/07/31 04:01:26  zhangyuxing
# ģʽƥ�������
#
# Revision 1.37  2008/07/31 03:13:02  zhangyuxing
# �޸�ģ��ͨ��� �� $ ��Ϊ $p
#
# Revision 1.36  2008/07/30 07:30:42  zhangyuxing
# delQuestsRandomLog ������Ϊ �� delRandomQuestRecord
#
# Revision 1.35  2008/07/30 05:54:36  zhangyuxing
# getGroupQuestDegree ����Ϊ�� getGroupCount
# getGroupQuestCount  ����Ϊ�� getSubQuestCount
#
# Revision 1.34  2008/07/28 06:34:02  zhangyuxing
# �޸������������
#
# Revision 1.33  2008/07/28 01:11:43  zhangyuxing
# �齱���Ĳ��ִ���
#
# Revision 1.32  2008/07/19 08:15:28  zhangyuxing
# �޸� self.questID ʹ�ô���
#
# Revision 1.31  2008/07/19 08:02:08  zhangyuxing
# ��isTasksOk ��һ������
#
# Revision 1.30  2008/07/19 07:05:29  zhangyuxing
# ���� self.freeCount ��BUG
#
# Revision 1.29  2008/07/19 01:37:26  zhangyuxing
# �޸ı����������½�����ʧ�ܵ�BUG
#
# Revision 1.28  2008/07/14 04:35:35  zhangyuxing
# ����ȼ��仯��������ɲ�ѯ
#
# Revision 1.27  2008/07/09 04:13:35  wangshufeng
# �����Ҳ������������������Ӧ��ͬ��״ֵ̬�����ͬ����ʾ��Ϣ��
#
# Revision 1.26  2008/07/09 03:18:02  zhangyuxing
# ����isTasksOk���ж������Ƿ���Ч��
#
# Revision 1.25  2008/07/08 08:57:52  zhangyuxing
# ��ӽ���BUG�޸�
#
# Revision 1.24  2008/06/27 01:14:00  zhangyuxing
# no message
#
# Revision 1.23  2008/06/18 04:01:56  zhangyuxing
# no message
#
# Revision 1.22  2008/06/03 02:43:20  zhangyuxing
# �޸� ������д����
#
# Revision 1.21  2008/05/06 02:47:51  zhangyuxing
# �������жϽ�Ʒ�Ƿ�ΪNONE�������б��в�����ж�
#
# Revision 1.20  2008/04/02 09:32:49  zhangyuxing
# �޸��˴���������������BUG
#
# Revision 1.19  2008/04/01 05:22:01  zhangyuxing
# ����ȡ������flags
#
# Revision 1.18  2008/03/28 03:47:21  zhangyuxing
# �޸ķ�������ķ�����ʽ
#
# Revision 1.17  2008/03/28 03:40:42  zhangyuxing
# �޸ķ�������ķ�����ʽ
#
# Revision 1.16  2008/02/13 02:37:04  zhangyuxing
# �޸ļ򵥴���
#
# Revision 1.15  2008/02/01 04:01:07  zhangyuxing
# �޸ļ�BUG
#
# Revision 1.14  2008/01/30 02:51:01  zhangyuxing
# �޸ļ�BUG
#
# Revision 1.13  2008/01/25 07:29:35  zhangyuxing
# �����������������
#
# Revision 1.12  2008/01/18 06:34:12  zhangyuxing
# ���ӣ�����̶�������������
#
# Revision 1.11  2008/01/11 06:52:10  zhangyuxing
# ����������ʽ self._style
#
# Revision 1.10  2008/01/09 03:23:30  zhangyuxing
# ���´������������������з����͹��ܡ�
#
# Revision 1.9  2007/11/02 03:56:48  phw
# QuestTasksDataType -> QuestDataType
# method removed: gossipPrebegin()
#
# Revision 1.8  2007/06/19 08:46:46  huangyongwei
# ����״̬�Ķ�����ԭ���� csstatus ��ת���� csdefine ��
#
# Revision 1.7  2007/06/14 10:18:31  huangyongwei
# ���������˺궨��
#
# Revision 1.6  2007/06/14 10:03:28  huangyongwei
# ���������˺궨��
#
# Revision 1.5  2007/06/11 08:53:15  kebiao
# 		self. _id = id
#
# To��
# 		self._id = id
#
# Revision 1.4  2007/05/05 08:19:32  phw
# whrandom -> random
#
# Revision 1.3  2007/02/07 07:05:54  kebiao
# ȥ�����Ͷ�ѡһ��������
#
# Revision 1.2  2006/08/02 08:13:35  phw
# �ӿڸ�����
# 	reward() --> reward_()
#
# Revision 1.1  2006/03/27 07:39:26  phw
# no message
#
#