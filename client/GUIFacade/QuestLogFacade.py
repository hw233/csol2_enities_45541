# -*- coding: gb18030 -*-
#
# $Id: QuestLogFacade.py,v 1.32 2008-08-09 08:37:41 songpeifang Exp $

from bwdebug import *
import BigWorld as bw
from event.EventCenter import *
import time
import csstatus
import StringFormat
from QuestModule import QuestReward
import csdefine
import GUIFacade
from config.client import QuestTypeDatas
from gbref import rds
C_QUEST_LOG_NO_SELECT = -1

class QuestLogFacade:
	@staticmethod
	def reset():
		QuestLogFacade.isInit = False
		QuestLogFacade.quests = {}									# ����������־��������, key is questID, value is tasks
		QuestLogFacade.log_selected = C_QUEST_LOG_NO_SELECT			# ��¼������־�е�ǰѡ�������һ������
		QuestLogFacade.last_abandon_quest = {}						# ���һ����ɾ����������־
		QuestLogFacade.objectiveDetail = []

# ------------------------->
# call by server
# ------------------------->
def questLogIsInit():
	return QuestLogFacade.isInit

def initQuestLog():
	QuestLogFacade.isInit = True

def getQuestLogs():
	"""
	ȡ�������������־�ֵ�

	@return: dict
	"""
	return QuestLogFacade.quests

def questIsCompleted( questID ):
	"""
	�����Ƿ��Ѿ���ɿɽ�
	"""
	try:
		quest = getQuestLogs()[ questID ]
	except KeyError:
		ERROR_MSG( "no such quest.", questID )
		return False

	for task in quest[ "tasks" ].getTasks().itervalues():
		if not task.isCompleted():
			return False
	return True

def getCompletedTasksNum( questID ) :
	"""
	��ȡ��ɵ�����Ŀ����
	"""
	completedTasksNum = 0
	quest = getQuestLogs().get( questID )
	if quest is not None :		
		for task in quest[ "tasks" ].getTasks().itervalues():
			if task.isCompleted():
				completedTasksNum += 1
	return completedTasksNum

def isTaskCompleted( questID, taskIndex ) :
	"""
	�ж�������ĳ��Ŀ���Ƿ����
	"""
	quest = getQuestLogs().get( questID )
	if quest is None :
		ERROR_MSG( "no such quest.", questID )
		return False
	task = quest["tasks"].getTasks().get( taskIndex )
	return task is not None and task.isCompleted()
	
def getCompleteRuleType( questID ):
	"""
	��ȡ�������ɹ���
	"""
	completeRuleType = 0
	quest = getQuestLogs().get( questID )
	if quest is not None :
		completeRuleType = quest["completeRuleType"]
	return completeRuleType

def onAddQuestLog( questID, canShare, completeRuleType, tasks, title, level, objectiveText, detailText, rewards ):
	"""
	����һ��������־
	"""
	questLog = getQuestLogs()
	if questLog.has_key( questID ):
		quest = questLog[questID]
	else:
		quest = { "id" : questID }
		questLog[questID] = quest

	d = {	"canShare"				: canShare,
			"completeRuleType"		: completeRuleType,
			"tasks"					: tasks,
			"title"					: StringFormat.format( title ),
			"level"					: level,
			"objectiveText"			: StringFormat.format( objectiveText ),
			"detailText"			: StringFormat.format( detailText ),
			"rewards_other"			: [],
			"rewards_choose_items"	: None,
			"rewards_fixed_items"	: None,
			"rewards_role_level_items"	: None,
			"rewards_rnd_items"		: None,
			"rewards_fixed_rnd_items"		: None,
			"rewards_quest_part_completed"	: None,
			"rewards_fixed_items_from_class": None,
			"rewards_skills"	: [],
		}
	for reward in rewards:
		qr = QuestReward.createByStream( reward )
		if qr.type() in [ csdefine.QUEST_REWARD_CHOOSE_ITEMS, csdefine.QUEST_REWARD_CHOOSE_ITEMS_AND_BIND ]:
			d["rewards_choose_items"] = qr
		elif qr.type() == csdefine.QUEST_REWARD_RANDOM_ITEMS:
			d["rewards_rnd_items"] =  qr
		elif qr.type() in [ csdefine.QUEST_REWARD_ITEMS, csdefine.QUEST_REWARD_FUBI_ITEMS ]:
			d["rewards_fixed_items"] = qr
		elif qr.type() == csdefine.QUEST_REWARD_ITEMS_FROM_ROLE_LEVEL:
			d["rewards_role_level_items"] = qr
		elif qr.type() == csdefine.QUEST_REWARD_FIXED_RANDOM_ITEMS:
			d["rewards_fixed_rnd_items"] = qr
		elif qr.type() == csdefine.QUEST_REWARD_RATE_QUEST_PART_COMPLETED:
			d["rewards_quest_part_completed"] = qr
		elif qr.type() == csdefine.QUEST_REWARD_ITEMS_FROM_CLASS:
			d["rewards_fixed_items_from_class"] = qr
		elif qr.type() in [ csdefine.QUEST_REWARD_SKILL, csdefine.QUEST_REWARD_SKILL_FROM_CLASS ]:
			d["rewards_skills"].append( qr )
		else:
			d["rewards_other"].append( qr )
	quest.update( d )
	fireEvent( "EVT_ON_QUEST_LOG_ADD", questID )

def onRemoveQuestLog( questID ):
	"""
	ɾ��һ�������������һ���ǳ�����������ɺ�ɾ��������־�á�
	"""
	if questID == 0:
		return
	questLog = getQuestLogs()
	del questLog[questID]
	fireEvent( "EVT_ON_QUEST_COMPLETED")
	fireEvent( "EVT_ON_QUEST_LOG_REMOVED", questID )
	if getQuestLogSelection() == questID:
		setQuestLogSelect( C_QUEST_LOG_NO_SELECT )

def onAbandonQuest( questID ):
	"""
	����һ��������������������������Ҫ�����һ���������档
	"""
	questLog = getQuestLogs()
	QuestLogFacade.last_abandon_quest = questLog[questID]
	del questLog[questID]
	fireEvent( "EVT_ON_QUEST_LOG_REMOVED", questID )
	fireEvent( "EVT_ON_QUEST_CAN_ACCEPT_ADD", questID )
	if getQuestLogSelection() == questID:
		setQuestLogSelect( C_QUEST_LOG_NO_SELECT )

def onTaskStateUpdate( questID, taskIndex, taskState ):
	quest = getQuestLogs()[questID]
	quest["tasks"]._tasks[taskIndex].copyFrom( taskState )
#	if getQuestLogSelection() == questID:
	fireEvent( "EVT_ON_QUEST_TASK_STATE_CHANGED", questID, taskIndex )
	#����ʧ������ʾadd by wuxo
	args = GUIFacade.getObjectiveDetail( questID )
	for taskType, index, title, tag, isCollapsed, isComplete, itemID, showOrder, npcID in args:
		if isCollapsed:
			return
	tempMsg = quest["tasks"]._tasks[taskIndex].getMsg()
	if not tempMsg == "":
		bw.player().statusMessage( csstatus.ROLE_QUEST_QUEST_INFO, quest["tasks"]._tasks[taskIndex].getMsg() )
		if questIsCompleted( questID ):
			bw.player().statusMessage( csstatus.ROLE_QUEST_QUEST_FINISHED, quest["title"] )


# ------------------------------>
# call by GUI
# ------------------------------>
def getAbandonQuestName():
	"""
	ȡ�����һ������������������

	@rtype: String
	"""
	return QuestLogFacade.last_abandon_quest["title"]

def abandonQuest( quest=None ):
	questID = C_QUEST_LOG_NO_SELECT
	if quest is None:
		questID = getQuestLogSelection()
	else:
		questID = quest.itemInfo.id
	if questID == C_QUEST_LOG_NO_SELECT:
		ERROR_MSG( "no selected quest." )
		return

	bw.player().cell.abandonQuest( questID )

def commitCasualQuest( questId ) :
	"""�ύ������������ύ����������Ҫ��NPC�Ի�"""
	bw.player().cell.questSingleReward( questId )

def hasQuestLog( questID ):
	"""
	�����Ƿ����ָ����������־

	@rtype: BOOL
	"""
	return QuestLogFacade.quests.has_key( questID )

def hasQuestTaskType( questID, type ):
	"""
	���������Ƿ���type��task
	"""
	if questID == -1:
		return False
	try:
		quest = getQuestLogs()[questID]
	except KeyError:
		ERROR_MSG( "no such quest.", questID )
		return False

	for task in quest["tasks"].getTasks().itervalues():
		if task.getType() == type:
			return True
	return False

def hasQuestType( questType ) :
	"""
	��ѯ�Ƿ��ȡ��ĳ�����͵�����
	"""
	for quest in QuestLogFacade.quests.itervalues() :
		if quest["tasks"].getType() == questType :
			return True
	return False

def questLogCanShare():
	"""
	�жϵ�ǰ��ѡ��������Ƿ���Թ���

	@return: BOOL
	@rtype:  BOOL
	"""
	questID = getQuestLogSelection()
	if questID == C_QUEST_LOG_NO_SELECT:
		return False
	return bool( getQuestLogs()[questID]["canShare"] )

def shareQuestLog( ):
	"""
	����ǰ��ѡ�������
	"""
	if not questLogCanShare():
		ERROR_MSG( "quest can't share." )
		return
	questID = getQuestLogSelection()
	bw.player().cell.questShare( questID )

def getQuestLogTitle( questID ):
	"""
	ȡ��������־ͷ

	@return: (title, level, hardLevel)
	@rtype: tuple of string
	"""
	try:
		quest = getQuestLogs()[questID]
	except KeyError:
		ERROR_MSG( "no such quest.", questID )
		return ""
	return ( quest["title"], quest["level"] )

def getQuestLogRewards():
	"""
	ȡ�õ�ǰ��ѡ�������Ľ���

	@return: (rewards, rewards_choose) like as ([reward1, ...], [reward_choose1, ...])
	"""
	questID = getQuestLogSelection()
	if questID == C_QUEST_LOG_NO_SELECT:
		return
	quest = getQuestLogs()[questID]
	try:
		rewards = quest["rewards_other"]
	except KeyError:
		rewards = []

	try:
		rewards_choose_items = quest["rewards_choose_items"]
	except KeyError:
		rewards_choose_items = None

	return (rewards, rewards_choose_items)

def getQuestLogQuestText( questID ):
	"""

	Returns the description and objectives required for the specified quest.
	@return: string of tuple as (questDescription, questObjectives)
	"""
	try:
		quest = getQuestLogs()[questID]
	except KeyError:
		ERROR_MSG( "no such quest.", questID )
		return ("", "")
	return ( quest["detailText"], quest["objectiveText"] )

def getObjectiveDetail( questID ):
	"""
	��ȡ����Ŀ����ϸ����

	@return: list of tuple, tuple like as: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", False, False)
	"""
	try:
 		quest = getQuestLogs()[questID]
 	except KeyError:
 		ERROR_MSG( "no such quest.", questID )
 		return []

 	return [ task.getDetail() for task in quest["tasks"].getTasks().itervalues() ]
 	
def getTaskFromIndex( questID, index ):
	"""
	��ȡ�����ĳ������Ŀ��
	"""
	try:
 		quest = getQuestLogs()[questID]
 	except KeyError:
 		ERROR_MSG( "no such quest.", questID )
 		return None
 		
 	for task in quest["tasks"].getTasks().itervalues():
 		if task.index == index:
 			return task
 	return None

def getTaskGoalType( questID ):	# wsf add
	"""
	�������Ŀ��������б�

	rturn type: array of int,����[ csdefine.QUEST_OBJECTIVE_NONE, csdefine.QUEST_OBJECTIVE_DELIVER ]
	"""
	try:
 		quest = getQuestLogs()[ questID ]
 	except KeyError:
 		ERROR_MSG( "no such quest.", questID )
 		return []

	return [ task.getType() for task in quest[ "tasks" ].getTasks().itervalues() ]


#def getObjectiveTime( self, questID ):
#	"""
#	ȡ��ĳ�������ʣ��ʱ��(�����)
#
#	@return: ʣ��ʱ���None(û�д�ֵ)
#	"""
#	try:
#		#quest = getQuestLogs()[questID]
#		ERROR_MSG( "What?" )
#	except KeyError:
#		return None
#	return time.time() - t

def getQuestLogSelection():
	"""
	��ȡ��ǰ��ѡ�������

	@rtype: Long/None
	"""
	return QuestLogFacade.log_selected

def setQuestLogSelect( questID, isTraceSelect = False ):
	"""
	����ѡ��һ������
	"""
	QuestLogFacade.log_selected = questID
	if questID != C_QUEST_LOG_NO_SELECT and not hasQuestLog( questID ):
		ERROR_MSG( "no such quest.", questID )
		return
	fireEvent( "EVT_ON_QUEST_LOG_SELECTED", questID, isTraceSelect )

# -----------------------------------------------------
def getPreCommonRewards( questID ) :
	return QuestLogFacade.quests[questID]["rewards_other"]

def getPreSingleItemReward( questID ) :
	return QuestLogFacade.quests[questID]["rewards_fixed_items"]

def getPreRandomItemsReward( questID ) :
	return QuestLogFacade.quests[questID]["rewards_rnd_items"]

def getPreOptionalItemReward( questID ) :
	return QuestLogFacade.quests[questID]["rewards_choose_items"]

def getRoleLevelItemReward( questID ):
	return QuestLogFacade.quests[questID]["rewards_role_level_items"]

def getQuestType( questID ) :
	if not QuestLogFacade.quests.has_key( questID ):
		return -1
	return QuestLogFacade.quests[questID]["tasks"].getType()

def getPreFixRandomItemReward( questID ) :
	return QuestLogFacade.quests[questID]["rewards_fixed_rnd_items"]

def getPreRewardsQuestPartCompleted( questID ):
	return QuestLogFacade.quests[questID]["rewards_quest_part_completed"]

def getPreRewardsFixedItemsFromClass( questID ):
	return QuestLogFacade.quests[questID]["rewards_fixed_items_from_class"]

def getQuestLogSkillRewards( questID ):
	return QuestLogFacade.quests[questID]["rewards_skills"]

def getQuestTypeStr( questID ):
	typeDatas = QuestTypeDatas.Datas

	beforeDatas = typeDatas.get( "before" )
	if beforeDatas :
		typeTag = str( questID )[:5]
		for tagStr, string in beforeDatas.iteritems():
			if tagStr == typeTag :
				return int( tagStr ), string

	typeTag = str( questID )[:3]
	for tagStr, string in typeDatas.iteritems():
		if tagStr == typeTag :
			return int( tagStr ), string

	INFO_MSG( "no Quest Type! questID: %s" % questID )
	return 0, ""

# QuestLogFacade.py
