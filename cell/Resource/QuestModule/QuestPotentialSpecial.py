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
	Ǳ�ܸ����������񣬴�����ĵȼ���������������NPC�������ҽ�����ʱ�����е�Ǳ������һ�£�	������������Ǳ�ܸ�������
	"""
	def __init__( self ):
		"""
		"""
		Quest.__init__( self )
		self._style = csdefine.QUEST_STYLE_POTENTIAL
		self._reward_lv = {}	# ��Ӧ�ȼ��Ľ���
		
	def init( self, section ):
		Quest.init( self, section )
		pDataInfos = g_questRewardFromTable.get( str( self.getID() ) )	# ��ʼ������
		for key, value in pDataInfos.iteritems():
			instance = QTReward.createReward( "QTRewardPotential" )
			instance._potential = value["potential"]
			self._reward_lv[ key] = instance
			
	def newTasks_( self, player ):
		"""
		virtual method. call by accept() method.
		��ʼ�����񣬲���һ������ҵ�ǰ�����е�Ǳ������һ�µ�����Ŀ��ʵ��
		������Task����������������Ŀ�꣬���������������񣬵��ۡ�
		
		@return: instance of QuestDataType or derive it���������Ŀ�����ʧ������뷵��None
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
		potentialQDT.set( "specialPtQuestID", self.getID() )	# ��������Ҫ�����е�Ǳ����������Ǳ���������ʱ������ҲҪ���
		
		ptQuest = g_quests[ questID ]
		if random.randint(1, 100) <= ptQuest.rewardsItemRate:
			itemIDs = ptQuest.rewardsItemList.keys()
			specialPtQuest.set( "rewardItemID", itemIDs[ random.randint( 0, len( itemIDs ) - 1 ) ] )
		return specialPtQuest
		
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
		specialPtQuest = player.questsTable[self.getID()]
		lv = specialPtQuest.query( "qLevel", 0 )
		potentialQuset = g_quests[specialPtQuest.query( "potentialQusetID" )]	# ���Ǳ�ܸ�������
		
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
		��ý�������ϸ��
		
		�������������Ǳ�ܸ�����������ڵģ����û��Ǳ�ܸ������񣬽����������û�κ�����ġ�
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
		��ѯ��Ҷ�ĳһ������Ľ���״̬��

		@return: ����ֵ������鿴common���QUEST_STATE_*
		@rtype:  UINT8
		"""
		questID = self.getID()
		if player.questIsCompleted( questID ):
			return csdefine.QUEST_STATE_COMPLETE						# ������������
		if player.has_quest( questID ):
			# �ѽ��˸�����
			if player.questTaskIsCompleted( questID ):
				return csdefine.QUEST_STATE_FINISH						# ����Ŀ�������
			else:
				return csdefine.QUEST_STATE_NOT_FINISH					# ����Ŀ��δ���
		else:
			# û�нӸ�����
			if self.checkRequirement( player ):
				questIDs = player.findQuestByType( csdefine.QUEST_TYPE_POTENTIAL )
				if len( questIDs ) == 0:
					printStackTrace()
					INFO_MSG( "player( %s ) have no potential quest." % player.getName() )
					return csdefine.QUEST_STATE_NOT_ALLOW
				if g_quests[questIDs[ 0 ]].getObjectIdsOfFinish() == self.getObjectIdsOfFinish():
					return csdefine.QUEST_STATE_NOT_HAVE			# ���Խӵ���δ�Ӹ�����
			return csdefine.QUEST_STATE_NOT_ALLOW					# ���������Ӹ�����