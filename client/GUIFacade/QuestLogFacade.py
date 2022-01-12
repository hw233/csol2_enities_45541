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
		QuestLogFacade.quests = {}									# 所有任务日志都在这里, key is questID, value is tasks
		QuestLogFacade.log_selected = C_QUEST_LOG_NO_SELECT			# 记录任务日志中当前选择的是哪一个任务
		QuestLogFacade.last_abandon_quest = {}						# 最后一个被删除的任务日志
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
	取得所有任务的日志字典

	@return: dict
	"""
	return QuestLogFacade.quests

def questIsCompleted( questID ):
	"""
	任务是否已经完成可交
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
	获取完成的任务目标数
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
	判断任务中某个目标是否完成
	"""
	quest = getQuestLogs().get( questID )
	if quest is None :
		ERROR_MSG( "no such quest.", questID )
		return False
	task = quest["tasks"].getTasks().get( taskIndex )
	return task is not None and task.isCompleted()
	
def getCompleteRuleType( questID ):
	"""
	获取任务的完成规则
	"""
	completeRuleType = 0
	quest = getQuestLogs().get( questID )
	if quest is not None :
		completeRuleType = quest["completeRuleType"]
	return completeRuleType

def onAddQuestLog( questID, canShare, completeRuleType, tasks, title, level, objectiveText, detailText, rewards ):
	"""
	增加一个任务日志
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
	删除一个任务，这种情况一般是出现在任务完成后删除任务日志用。
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
	放弃一个任务，这种情况出现在玩家主动要求放弃一个任务上面。
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
	#任务失败则不提示add by wuxo
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
	取得最后一个被放弃的任务名称

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
	"""提交随机触发任务，提交此类任务不需要与NPC对话"""
	bw.player().cell.questSingleReward( questId )

def hasQuestLog( questID ):
	"""
	返回是否存在指定的任务日志

	@rtype: BOOL
	"""
	return QuestLogFacade.quests.has_key( questID )

def hasQuestTaskType( questID, type ):
	"""
	返回任务是否有type的task
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
	查询是否接取了某个类型的任务
	"""
	for quest in QuestLogFacade.quests.itervalues() :
		if quest["tasks"].getType() == questType :
			return True
	return False

def questLogCanShare():
	"""
	判断当前被选择的任务是否可以共享

	@return: BOOL
	@rtype:  BOOL
	"""
	questID = getQuestLogSelection()
	if questID == C_QUEST_LOG_NO_SELECT:
		return False
	return bool( getQuestLogs()[questID]["canShare"] )

def shareQuestLog( ):
	"""
	共享当前被选择的任务
	"""
	if not questLogCanShare():
		ERROR_MSG( "quest can't share." )
		return
	questID = getQuestLogSelection()
	bw.player().cell.questShare( questID )

def getQuestLogTitle( questID ):
	"""
	取得任务日志头

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
	取得当前被选择的任务的奖励

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
	获取任务目标详细描述

	@return: list of tuple, tuple like as: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", False, False)
	"""
	try:
 		quest = getQuestLogs()[questID]
 	except KeyError:
 		ERROR_MSG( "no such quest.", questID )
 		return []

 	return [ task.getDetail() for task in quest["tasks"].getTasks().itervalues() ]
 	
def getTaskFromIndex( questID, index ):
	"""
	获取任务的某个任务目标
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
	获得任务目标的类型列表

	rturn type: array of int,比如[ csdefine.QUEST_OBJECTIVE_NONE, csdefine.QUEST_OBJECTIVE_DELIVER ]
	"""
	try:
 		quest = getQuestLogs()[ questID ]
 	except KeyError:
 		ERROR_MSG( "no such quest.", questID )
 		return []

	return [ task.getType() for task in quest[ "tasks" ].getTasks().itervalues() ]


#def getObjectiveTime( self, questID ):
#	"""
#	取得某个任务的剩余时间(如果有)
#
#	@return: 剩余时间或None(没有此值)
#	"""
#	try:
#		#quest = getQuestLogs()[questID]
#		ERROR_MSG( "What?" )
#	except KeyError:
#		return None
#	return time.time() - t

def getQuestLogSelection():
	"""
	获取当前被选择的任务

	@rtype: Long/None
	"""
	return QuestLogFacade.log_selected

def setQuestLogSelect( questID, isTraceSelect = False ):
	"""
	请求选择一个任务
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
