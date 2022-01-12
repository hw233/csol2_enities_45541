# -*- coding: gb18030 -*-
#
# $Id $

"""
�������ģ��
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
		self._style = csdefine.QUEST_STYLE_LOOP_GROUP	# ��������ʽ
		self._sExpData = {}								# �뾭����Ϣ

	def init( self, section ):
		"""
		"""
		QuestRandomGroup.init( self, section )
		self.loadSexpDatas( "config/quest/QuestLoopDatas/QuestLoopDatas.xml" )
		#�������ʱ��
		self._finishTime = section.readInt("eachtime") * 60

		#�������齱��
		param1 = self._sExpData
		param2 = section.readString("relationRate")	# ˫����������
		if len( param2 ) != 0:
			self._expReward = QTReward.createReward( "QTRewardRelationExp" )
			#self._rateExp_times = float(rateList[0])						#��������
			#self._rateExp_groups = float(rateList[1])						#��������
			#self._rateExp_level = float(rateList[2])						#�ȼ�����
			#self._rateExp_baseExp = int(rateList[3])						#��������
			#self._rateExp_doubleGroups = int(rateList[4])					#˫����������
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
		���ص���������Ϣ�ܱ�
		"""
		section = Language.openConfigSection( configPath )
		assert section is not None, "open %s false." % configPath
		for node in section.values():
			questLevel = node.readInt( "level" )
			questSecondExp = node.readFloat( "sExp" )
			self._sExpData[ questLevel ] = questSecondExp

		# �������
		Language.purgeConfig( configPath )

	def getRewardsDetail( self, player ):
		"""
		��ý�������ϸ�ڣ�������
		@param      player: instance of Role Entity
		@type       player: Entity
		"""
		tempList = QuestRandomGroup.getRewardsDetail( self, player )

		#�������鴦��
		if self._expReward:
			r = self._expReward.transferForClient( player, self._id )
			tempList.append( r )
		if self._expPetReward:
			r = self._expPetReward.transferForClient( player, self._id )
			tempList.append( r )
		return tempList


	def reward_( self, player, rewardIndex = 0 ):
		"""
		����������ɽ�����������
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
		��������
		���õ��������¼
		"""
		#if flags != csdefine.QUEST_REMOVE_FLAG_NPC_CHOOSE:
		#	player.statusMessage( csstatus.ROLE_QUEST_RANDOM_GROUP_ABANDON_ERROR )
		#	return
		player.setGroupQuestRecorded( self._id, False )
		if not player.checkStartGroupTime( self._id ):
			# �������ÿ�������
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
		��һ���������������񼯺���
		"""
		self._quest_set[questID] = quest
		if self._finishTime != 0:
			instance = QTTask.QTTaskTime( questID % 10000,self._finishTime )
			quest.tasks_[instance.index] =  instance

	def onComplete( self, player ):
		"""
		�����ύ���֪ͨ
		"""
		if not player.checkStartGroupTime( self._id ) and not player.isGroupQuestRecorded( self._id ):
			# �������ÿ�������(��ͬ������ and ���Ƕ�ȡ�Ļ������¼)
			player.resetGroupQuest( self._id )

		count = player.getSubQuestCount( self.getID() ) #�������
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
		ִ�н��������ж�
		"""
		#if not player.groupQuestSavedAndFailedProcess( self._id ):
		#	return False


		if not player.checkStartGroupTime( self._id ) and not player.isGroupQuestRecorded( self._id ):		# �������ÿ�������
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
				if not player.checkStartGroupTime( self._id ):						#�������ÿ�������
					player.resetGroupQuest( self._id )
				else:
					player.statusMessage( csstatus.ROLE_QUEST_GROUP_ENOUGH )
					return False

		if player.getSubQuestCount( self._id ) == 0:								#����ֻص���һ��ĵ�һ��������񣨽���Ѻ����
			if player.money < self._deposit:										#Ѻ���ж�
				player.statusMessage( csstatus.ROLE_QUEST_DEPOSIT_NOT_ENOUGH )
				return False
			player.payQuestDeposit( self._id, self._deposit )


		return True



	def onAccept( self, player, tasks ):
		"""
		virtual method.
		ִ������ʵ�ʴ���
		"""
		if not player.has_randomQuestGroup( self._id ): 						#������������¼�ж�
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
				# ��������½�ȡ�Ļ�����Ҫ��Ǯ
				money = int( ( player.level * 300 * ( player.getGroupQuestCount( self._id ) + 1 ) ) ** 1.2 )
				player.payMoney( money, csdefine.CHANGE_MONEY_REACCEPTLOOPQUEST )
				player.failedGroupQuestList.remove( i )		# ������ȡ������󣬰Ѹ�����ӵ���ʧ�ܵĻ������б������

		player.setRandomLogsTaskType( self._id, taskType )

		QuestRandomGroup.onAccept( self, player, tasks )


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

		sameType_temp_set = []  #��ǰһ������Ŀ�겻ͬ������
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

		tasks = self._quest_set[key].newTasks_( player )	#ȡ���������Ŀ��
		tasks.setQuestID( self._id )						#ʹ�ø������ID
		tasks.set( "subQuestID", key )						#�������ID�洢����չ������
		tasks.set( "style", self._style )			#������ʽ�洢
		tasks.set( "type", self._type )				#�������ʹ洢
		tasks.set( "giveItemIDs", giveItemIDs )		#���������Ʒ��ID

		return tasks


	def gossipDetail( self, player, issuer = None ):
		"""
		����������������԰ף�
		��ʾ�˶԰׺�Ϳ��Ե㡰accept���������ˣ�
		���issuerΪNone���ʾ��������Ǵ���Ʒ������player�������
		"""
		if issuer:	targetID = issuer.id
		else:		targetID = 0

		player.questAccept( player.id, self._id, issuer.id )
		player.endGossip( issuer )

	def getLevel( self, player = None ):
		"""
		ȡ������ȼ�
		"""
		if player == None:
			return self._level
		return player.level

	def checkRequirement( self, player ):
		"""
		virtual method.
		�ж���ҵ������Ƿ��㹻�ӵ�ǰ����
		@return: ����ﲻ���������Ҫ���򷵻�False��
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
		������
		����������Ҫ������������λ
		"""
		if player.getNormalKitbagFreeOrderCount() < 2:
			player.statusMessage( csstatus.ROLE_QUEST_GIVE_FREE_BLANK )
			return

		QuestRandomGroup.complete( self, player, rewardIndex, codeStr )
	
	def isTimeOut( self, player, questID ):
		"""
		�������Ƿ�ʱ
		"""
		tasks = player.getQuestTasks( questID ).getTasks()
		timeTask = None
		for task in tasks.values():
			if task.getType() == csdefine.QUEST_OBJECTIVE_TIME:
				timeTask = task
				break
		
		return not( timeTask and timeTask.isCompleted( None ) )
