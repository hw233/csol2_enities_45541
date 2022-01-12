# -*- coding: gb18030 -*-
#
# $Id: Quest.py,v 1.90 2008-08-18 01:38:35 zhangyuxing Exp $


"""
��ͨ����ģ��
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
		self.requirements_ = []						# list of QTRequirement; ����������
		self.beforeAccept_ = []						# list of scripts; ������ʱִ��һЩ�ű�
		self.afterComplete_ = []					# list of scripts; �������ʱִ��һЩ�ű�
		self.taskComplete_ = {}						# dict of scripts; ����Ŀ�����ʱ��������
		self.tasks_ = {}							# dict of QTTask; ������Ŀ��
		self.rewards_ = []							# list of QTReward; ������
		self.rewardsFixedItem_ = None				# �̶���Ʒ����
		self.rewardsRoleLevelItem_ = None				# �仯�ȼ���Ʒ����
		self.rewardsChooseItem_ = None				# ����Ʒѡһ����
		self.rewardsRandItem_ = None				# �����Ʒ����
		self.rewardsFixedRandItem_ = None			# �̶������Ʒ����
		self.rewardsQuestPartCompleted_ = None
		self.rewardsFixedItemFromClass_ = None		# �������ְҵ���費ͬ����Ʒ����

		self._id = 0								# questID��uint16 1 - 65535
		self.repeatable_ = False					# �����Ƿ�����ظ����
		self._start_objids = []						# ����Ŀ�ʼ���б��ʶ��ע���˱�ʾ����npcһ���entityID�������ʾ������ƷID������ֻ����һ����
		self._start_itemID = ""						# ����Ŀ�ʼ�߱�ʶ����Ʒ��
		self._finish_objids = []					# ����Ľ������б��ʶ
		self._questBoxsDict = {}					# ���������ֵ�
		self._level = 0								# ����ȼ�
		self._can_share = 0							# �Ƿ��ܹ���
		self._next_quest = 0						# ��ʾ��ǰ������ɺ���Ա��������һ������
		self._type =  csdefine.QUEST_TYPE_NONE		# �������ͨ����self._acceptMaxCount�����������ĳһ������Ľ�������
		self._acceptMaxCount = 0					# �������self._type������������� ����(�������questsTable���� �����������_acceptMaxCount�� )
		self._style = csdefine.QUEST_STYLE_NORMAL	# ������ʽ

		self._msg_prebegin		= ""
		self._msg_prebegin_menu = None
		
		self._completeRule = None					# ������ɹ���ʵ��
		self._completeRuleType = 0

	def init( self, section ):
		"""
		virtual method.
		@param section: ���������ļ�section
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
		self._can_share = section.readInt( "can_share" )	# �Ƿ��ܹ���

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
			instance = QTCompleteRule.createRule( section.readInt( "complete_rule" ) )		# ����Ĭ��Ϊ0
			self._completeRule = instance
			self._completeRuleType = section.readInt( "complete_rule" )
		else:	# û�����õ����
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
		ȡ������ID��(questID)
		"""
		return self._id

	def getTitle( self ):
		return self._title

	def getLevel( self, player = None ):
		"""
		ȡ������ȼ�
		"""
		return self._level

	def getType( self ):
		"""
		ȡ���������
		"""
		return self._type

	def setType( self, maxAcceptCount, questType ):
		"""
		�ṩ����ӿ����������������ȷҪ�����������ձ����͸���
		@param questType:		# �������
		@param maxAcceptCount:	# �������self._type������������� ����(�������questsTable���� �����������_acceptMaxCount�� ) Ĭ��Ϊ0
		"""
		self._type			 =  questType
		self._acceptMaxCount = maxAcceptCount

	def getObjectIdsOfFinish( self ):
		"""
		ȡ��������ɵ�Ŀ���ʶ
		"""
		return self._finish_objids

	def getObjectIdsOfStart( self ):
		"""
		ȡ������ʼ��Ŀ���ʶ
		"""
		return self._start_objids

	def getQuestBoxsDict( self ):
		"""
		ȡ�û��������Ʒ������
		"""
		return self._questBoxsDict


	def getNextQuest( self, player ):
		"""
		ȡ����һ�������ID( if has )
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
		elif self._next_quest[ 0 ] != "" :		#��ΪreadStringʱΪ�յĻ��᷵��""����split����[""]
			return int( self._next_quest[ 0 ] )
		else:
			return 0

	def getRewardsDetail( self, player ):
		"""
		��ý�������ϸ��
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
		# �߻�˵�����������ʾ��������ҿ�����Ϊ��ֹ�Ժ���ҪҪ����ʾ������Ҫ����
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
		����ύ������Ʒ������
		"""
		for task in self.tasks_.itervalues():
			if task.getType() in csconst.QUEST_OBJECTIVE_SUBMIT_TYPES or task.getType() == csdefine.QUEST_OBJECTIVE_SUBMIT_PICTURE or task.getType() == csdefine.QUEST_OBJECTIVE_SUBMIT_CHANGE_BODY or task.getType() == csdefine.QUEST_OBJECTIVE_SUBMIT_DANCE:
					return task.getSubmitInfo()
		return {}

	def canShare( self ):
		"""
		�жϵ�ǰ�����Ƿ��ܹ���

		@rtype: BOOL
		"""
		return bool( self._can_share )

	def sendCompleteMsg( self , player, rewardStrList ):
		"""
		�������֪ͨ
		@param      player: instance of Role Entity
		@type       player: Entity
		@param rewardStrList: ���н�������Ŀ�����б�
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
		��������ɽ�����

		@param      player: instance of Role Entity
		@type       player: Entity
		@param rewardIndex: ѡ������
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
			
		if self.rewardsQuestPartCompleted_:				# �������͵Ľ����Ǹ������͵ģ�����ֻ������Ʒ���������Ի�Ҫdoһ�¡�
			rewardInfoList.extend( self.rewardsQuestPartCompleted_.do( player, self.getID() ) )

		#self.sendCompleteMsg( player , rewardInfoList )
		return True

	def checkRequirement( self, player ):
		"""
		virtual method.
		�ж���ҵ������Ƿ��㹻�ӵ�ǰ����
		@return: ����ﲻ���������Ҫ���򷵻�False��
		@rtype:  BOOL
		"""
		for requirement in self.requirements_:
			if not requirement.query( player ):
				return False
		return True
		
	def checkComplete( self, player ):
		"""
		�ж�����Ƿ��������
		"""
		if self._completeRule:
			return self._completeRule.checkComplete( player, self.getID() )
		return False

	def accept( self, player ):
		"""
		virtual method.
		���������������ʧ�����򷵻�False��������ұ������˷Ų���������ߣ���

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
		���������������ʧ�����򷵻�False��������ұ������˷Ų���������ߣ���

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
		ִ�н�������ж�
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
		ִ������ʵ�ʴ���
		"""
		for script in self.beforeAccept_:
			script.do( player, tasks )

		player.questAdd( self, tasks )

	def onTaskCompleted( self, player, taskIndex ):
		"""
		virtual method.
		ĳ������Ŀ����߶������Ŀ�����
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
		������

		@param player: instance of Role Entity
		@type  player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		#player.setTemp( "questKitTote", kitTote )
		#player.setTemp( "questOrder", order )

		if player.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
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
		if not self.repeatable_:				# ֻ���治���ظ���ɵ�����
			player.recordQuestLog( self._id )	# ��¼������־

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

		# ͳ��ģ������������ɴ���
		g_Statistic.addQuestDayStat( player, self._id )
		return True

	def setDecodeTemp( self, player, codeStr ):
		"""
		���ñ����ַ�����ʱ����
		"""
		for task in player.getQuest(self.getID()).tasks_.itervalues():
			task.setPlayerTemp( player, codeStr )


	def removeDecodeTemp( self, player, codeStr ):
		"""
		ɾ�������ַ�����ʱ����
		"""
		for task in player.getQuest(self.getID()).tasks_.itervalues():
			task.removePlayerTemp( player )

	def abandoned( self, player, flags ):
		"""
		virtual method.
		���񱻷��������������ʲô���顣

		@param player: instance of Role Entity
		@type  player: Entity
		@param flags : ��������
		@return: None
		"""
		for e in self.afterComplete_:
			e.onAbandoned( player, player.questsTable[self.getID()] )

		# to do, ��������������������Ʒ��,�������ƺ���ʵ��������ô����Ƚ��鷳�Ĳ���,�����ʱû��ʵ��
		return True

	def newTasks_( self, player ):
		"""
		virtual method. call by accept() method.
		��ʼ�����񣬲���һ���뵱ǰ������ص�����Ŀ��ʵ��

		@return: instance of QuestDataType or derive it���������Ŀ�����ʧ������뷵��None
		@rtype:  QuestDataType/None
		"""
		tasks = QuestDataType()
		tasks.setQuestID( self._id )
		tasks.set( "style", self._style )			#������ʽ�洢
		tasks.set( "type", self._type )				#�������ʹ洢

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
		��ѯ��Ҷ�ĳһ������Ľ���״̬��

		@return: ����ֵ������鿴common���QUEST_STATE_*
		@rtype:  UINT8
		"""
		questID = self.getID()
		if player.questIsCompleted( questID ):
			return csdefine.QUEST_STATE_COMPLETE						# ������������
		if player.has_quest( questID ):
			# �ѽ��˸�����
			if self.checkComplete( player ):
				return csdefine.QUEST_STATE_FINISH						# ����Ŀ�������
			else:
				return csdefine.QUEST_STATE_NOT_FINISH					# ����Ŀ��δ���
		else:
			# û�нӸ�����
			if self.checkRequirement( player ):
				return csdefine.QUEST_STATE_NOT_HAVE					# ���Խӵ���δ�Ӹ�����
			else:
				return csdefine.QUEST_STATE_NOT_ALLOW					# ���������Ӹ�����

	def addToQuestBox( self ):
		"""
		������������
		"""
		QuestBoxsDict = self.getQuestBoxsDict()
		for QuestBoxID in QuestBoxsDict:
			QuestBoxNpc = g_objFactory.getObject( QuestBoxID )
			if not QuestBoxNpc:
				ERROR_MSG( self.getID(), "QuestBox not found.", QuestBoxID )
			else:
				assert QuestBoxNpc.getEntityType() != "NPCObject","Wrong QuestBoxID is %s" % QuestBoxID #��ʱ�޸ģ��ҳ����߻�����ΪQuestBox���±����NPCObject��grl
				index = QuestBoxsDict[ QuestBoxID ]
				QuestBoxNpc.addQuestTask( self.getID(), index )


	def gossipDetail( self, playerEntity, issuer = None ):
		"""
		����������������԰ף�
		��ʾ�˶԰׺�Ϳ��Ե㡰accept���������ˣ�
		���issuerΪNone���ʾ��������Ǵ���Ʒ������player�������
		"""
		if issuer:	targetID = issuer.id
		else:		targetID = 0
		playerEntity.sendQuestRewards( self._id, self.getRewardsDetail( playerEntity ) )
		playerEntity.sendQuestDetail( self._id,  self.getLevel( playerEntity ), targetID )

	def gossipIncomplete( self, playerEntity, issuer ):
		"""
		����Ŀ��δ��ɶ԰�
		"""
		if issuer:	targetID = issuer.id
		else:		targetID = 0
		playerEntity.sendQuestIncomplete(  self._id, self.getLevel( playerEntity ), targetID )
		playerEntity.statusMessage( csstatus.ROLE_QUEST_INCOMPLETE )

	def gossipPrecomplete( self, playerEntity, issuer ):
		"""
		����Ŀ������ɶ԰�
		"""
		if issuer:	targetID = issuer.id
		else:		targetID = 0
		playerEntity.sendQuestRewards( self._id, self.getRewardsDetail( playerEntity ) )
		playerEntity.sendObjectiveDetail( self._id, playerEntity.questsTable[self._id].getObjectiveDetail( playerEntity ) )
		playerEntity.sendQuestSubmitBlank( self._id, self.getSubmitDetail( playerEntity ) )
		playerEntity.sendQuestPrecomplete( self._id, self.getLevel( playerEntity ), targetID )

	def gossipComplete( self, playerEntity, issuer ):
		"""
		�������԰�
		"""
		if issuer:
			targetID = issuer.id
		else:
			targetID = 0
		playerEntity.sendQuestComplete( self._id, self.getLevel( playerEntity ), targetID )

	def sendQuestLog( self, playerEntity, questLog ):
		"""
		����������־

		@param questLog: ������־; instance of QuestDataType
		"""
		playerEntity.client.onQuestLogAdd( self._id, self._can_share, self._completeRuleType, questLog, self.getLevel( playerEntity ), self.getRewardsDetail(playerEntity) )

	def startGossip( self, player, issuer, dlgKey ):
		"""
		virtual method.
		����Ի�

		@param player: ���entity
		@param issuer: entity
		@param dlgKey: String; �Ի��ؼ���
		"""
		pass

	def finishGossip( self, player, issuer, dlgKey ):
		"""
		virtual method.
		����Ի�

		@param player: ���entity
		@param issuer: entity
		@param dlgKey: String; �Ի��ؼ���
		"""
		pass

	def onPlayerLevelUp( self, player ):
		"""
		"""
		player.questAdd( self, self.newTasks_( player ) )

		QuestsTrigger.SendQuestMsg( player, self._id )

	def isTasksOk( self, playerEntity ):
		"""
		�������Ŀ���Ƿ���Ч
		"""
		return True

	def onComplete( self, player ):
		"""
		�����ύ���֪ͨ
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
		�����������������ϸ��
		"""
		r = []
		for reward in self.rewards_:
			if reward.type() == csdefine.QUEST_REWARD_MONEY_FROM_REWARD_QUEST_QUALITY or reward.type() == csdefine.QUEST_REWARD_EXP_FROM_REWARD_QUEST_QUALITY:
				r.append( reward.transferForClient( player, self.getID() ) )
		return r

	def acceptRewardQuest( self, player ):
		"""
		������������
		"""
		"""
		virtual method.
		���������������ʧ�����򷵻�False��������ұ������˷Ų���������ߣ���

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
		ִ������ʵ�ʴ���
		"""
		for script in self.beforeAccept_:
			script.do( player, tasks )

		player.rewardQuestAdd( self, tasks )
		player.statusMessage( csstatus.ROLE_QUEST_QUEST_ACCEPTED,self._title )

