# -*- coding: gb18030 -*-
#
# $Id: QuestFacade.py,v 1.38 2008-09-02 00:59:52 songpeifang Exp $


import BigWorld as bw
import csdefine
import Const
import StringFormat
from QuestModule import QuestReward
from bwdebug import *
from event.EventCenter import *
import QuestLogFacade
from gbref import rds

class QuestFacade:

	submitInfo = None
	objectiveDetail = []
	currQuestID = None

	@staticmethod
	def reset():
		QuestFacade.target = None				# 任务相关的entity
		QuestFacade.id = -1						# 任务ID
		QuestFacade.level = 0					# 任务等级
		QuestFacade.title = ""
		QuestFacade.story_text = ""
		QuestFacade.objective_text = ""
		QuestFacade.incomplete_text = ""
		QuestFacade.precomplete_text = ""
		QuestFacade.complete_text = ""


# ------------------------->
# call by server
# ------------------------->
def _reset( targetEntity, questID ):
	# 做此判断避免任务目标或任务ID不匹配问题
	if getQuestTarget() is not targetEntity or QuestFacade.id != questID:
		QuestFacade.reset()
		QuestFacade.target = targetEntity
		QuestFacade.id = questID

def onQuestDetail( targetEntity, questID, title, level, storyText, objectiveText, voicefile ):
	"""
	显示某个可以接的任务的详细内容
	"""
	_reset( targetEntity, questID )
	QuestFacade.submitInfo = None
	QuestFacade.objectiveDetail = []
	QuestFacade.title = StringFormat.format( title )
	QuestFacade.level = level
	QuestFacade.story_text = StringFormat.format( storyText )
	QuestFacade.objective_text = StringFormat.format( objectiveText )
	fireEvent( "EVT_QUEST_SHOW_DETAIL_TEXT" )
	playVoice( voicefile, targetEntity.id, questID )

def onQuestIncomplete( targetEntity, questID, title, level, incompleteText, voicefile ):
	"""
	显示某个未完成的任务对话
	"""
	_reset( targetEntity, questID )
	QuestFacade.title = StringFormat.format( title )
	QuestFacade.level = level
	QuestFacade.incomplete_text = StringFormat.format( incompleteText )
	fireEvent( "EVT_QUEST_SHOW_INCOMPLETE_TEXT" )
	playVoice( voicefile, targetEntity.id, questID )

def onQuestPrecomplete( targetEntity, questID, title, level, precompleteText, voicefile ):
	"""
	游戏目标已达成对话(等待交任务)
	"""
	_reset( targetEntity, questID )
	#QuestFacade.submitInfo = getSubmitInfoFromServer()
	QuestFacade.title = StringFormat.format( title )
	QuestFacade.level = level
	QuestFacade.precomplete_text = StringFormat.format( precompleteText )
	fireEvent( "EVT_QUEST_SHOW_PRECOMPLETE_TEXT" )
	
	playVoice( voicefile, targetEntity.id, questID )

def onQuestComplete( targetEntity, questID, title, level, completeText, voicefile ):
	"""
	任务完成（已交）后的对话
	"""
	_reset( targetEntity, questID )
	QuestFacade.title = StringFormat.format( title )
	QuestFacade.level = level
	QuestFacade.complete_text = StringFormat.format( completeText )
	fireEvent( "EVT_QUEST_SHOW_COMPLETE_TEXT" )
	playVoice( voicefile, targetEntity.id, questID )

def playVoice( voicePath, targetID, questID ):
	QuestFacade.currQuestID = questID
	player = BigWorld.player()
	if "|" in voicePath:
		if  player.getGender() == csdefine.GENDER_MALE:
			voicePath = voicePath.split("|")[0]
		elif player.getGender() == csdefine.GENDER_FEMALE:
			voicePath = voicePath.split("|")[1]
	player.playSound( voicePath,2, targetID, csdefine.GOSSIP_PLAY_VOICE_PRIORITY_QUEST )
	
def clearVoiceBuff():
	QuestFacade.currQuestID = None
	gossipSound = rds.soundMgr.getGossipSound()
	if gossipSound:
		gossipSound.stop()

def getCurrQuestID():
	return QuestFacade.currQuestID

def setCurrQuestID( value ):
	QuestFacade.currQuestID = value

def onQuestRewards( targetEntity, questID, rewards ):
	"""
	接收任务奖励描述
	"""
	_reset( targetEntity, questID )
	QuestFacade.reward_choose_items = None
	QuestFacade.reward_rnd_items = None
	QuestFacade.reward_fixed_items = None
	QuestFacade.rewards_fixed_rnd_items = None
	QuestFacade.rewards_quest_part_completed = None
	QuestFacade.rewards_fixed_items_from_class = None
	QuestFacade.reward_others = []
	QuestFacade.reward_skills = []
	QuestFacade.reward_useSlots = False

	for reward in rewards:
		qr = QuestReward.createByStream( reward )
		if qr.type() in [ csdefine.QUEST_REWARD_CHOOSE_ITEMS, csdefine.QUEST_REWARD_CHOOSE_ITEMS_AND_BIND ]:
			QuestFacade.reward_choose_items = qr
		elif qr.type() == csdefine.QUEST_REWARD_RANDOM_ITEMS:
			QuestFacade.reward_rnd_items = qr
		elif qr.type() in [csdefine.QUEST_REWARD_ITEMS, csdefine.QUEST_REWARD_FUBI_ITEMS, csdefine.QUEST_REWARD_ITEMS_FROM_ROLE_LEVEL ]:
			QuestFacade.reward_fixed_items = qr
		elif qr.type() == csdefine.QUEST_REWARD_FIXED_RANDOM_ITEMS:
			QuestFacade.rewards_fixed_rnd_items = qr
		elif qr.type() == csdefine.QUEST_REWARD_RATE_QUEST_PART_COMPLETED:
			QuestFacade.rewards_quest_part_completed = qr
		elif qr.type() == csdefine.QUEST_REWARD_ITEMS_FROM_CLASS:
			QuestFacade.rewards_fixed_items_from_class = qr
		elif qr.type() in [ csdefine.QUEST_REWARD_SKILL, csdefine.QUEST_REWARD_SKILL_FROM_CLASS ]:
			QuestFacade.reward_skills.append( qr )
		elif qr.type() in Const.QUEST_REWARD_SLOTS_TYPE:
			#如果有使用老虎机的奖励类型
			QuestFacade.reward_others.append( qr )
			if not QuestFacade.reward_useSlots:
				QuestFacade.reward_useSlots = True
		else:
			QuestFacade.reward_others.append( qr )

def onObjectiveDetail( targetEntity, questID, objectiveDetail ):
	"""
	"""
	_reset( targetEntity, questID )
	QuestFacade.objectiveDetail = objectiveDetail

def getObjectiveDetailFromServer():
	"""
	"""
	return QuestFacade.objectiveDetail

def onSubmitBlank( targetEntity, questID, submitInfo ):
	"""
	"""
	_reset( targetEntity, questID )
	QuestFacade.submitInfo = submitInfo

def getSubmitInfoFromServer():
	"""
	"""
	return QuestFacade.submitInfo
# ------------------------------>
# call by GUI
# ------------------------------>
def getQuestTarget():
	return QuestFacade.target

def getQuestID():
	return QuestFacade.id

def getQuestTitle():
	"""
	取得当前被选择的任务标题、等级和难度等级
	return: (title, level)
	"""
	return ( QuestFacade.title, QuestFacade.level )

def getQuestObjectiveText():
	return QuestFacade.objective_text

def getQuestIncompleteText():
	return QuestFacade.incomplete_text

def getQuestPrecompleteText():
	return QuestFacade.precomplete_text

def getQuestCompleteText():
	return QuestFacade.complete_text

def getQuestDetail():
	return (QuestFacade.story_text, QuestFacade.objective_text)

# -----------------------------------------------------
def getOtherRewards():

	return QuestFacade.reward_others

def getFixedRewardItems() :
	"""
	获取固定奖励列表( hyw )
	"""
	return QuestFacade.reward_fixed_items

def getFixedRandomRewardItems():
	return QuestFacade.rewards_fixed_rnd_items
	
def getRewardsQuestPartCompleted():
	return QuestFacade.rewards_quest_part_completed

def getRewardsFixedItemsFromClass():
	return QuestFacade.rewards_fixed_items_from_class

def getRewardSkills():
	"""
	技能奖励
	"""
	return QuestFacade.reward_skills

def getChooseRewardItems() :
	"""
	获取可选奖励列表( hyw )
	"""
	return QuestFacade.reward_choose_items

def getRndRewardItems() :
	"""
	获取随机奖励列表( hyw )
	"""
	return QuestFacade.reward_rnd_items

def getRewardIsUseSlots():
	return QuestFacade.reward_useSlots

# -----------------------------------------------------
def acceptQuest( ):
	"""
	接受任务
	"""
	target = getQuestTarget()
	if target is None:
		bw.player().cell.questAccept( QuestFacade.id, 0 )	# 接最后一次被选择的任务
	else:
		bw.player().cell.questAccept( QuestFacade.id, target.id )

def declineQuest( ):
	"""
	拒绝接受任务
	"""
	target = getQuestTarget()
	if target is None:
		print "decline quest."
		#bw.player().cell.declineSelectedQuest( target.id )
	else:
		print "decline quest, we do nothing."


def completeQuest( rewardIndex, codeStr ):
	"""
	申请完成(交)任务

	@param rewardIndex: 选择奖励索引(如果有)，没有则输入-1
	@type  rewardIndex: INT8
	@param codeStr: 任务目标字符串关联信息
	@type  codeStr: STRING

	"""
	fireEvent( "EVT_END_GOSSIP" )
	if QuestFacade.reward_useSlots:#有使用考虎机奖励类型的，则触发老虎机
		bw.player().triggerQuestRewardSlots( QuestFacade.id, rewardIndex, codeStr, getQuestTarget().id )
	else:
		bw.player().cell.questChooseReward( QuestFacade.id, rewardIndex, codeStr, getQuestTarget().id )

def finishQuest():
	"""
	点击“关闭”按钮
	"""
	print "quest finish, we do nothing."

def confirmAcceptQuest():
	"""
	“你有队员正在进行xxx任务，你是否要开始同样的任务？”这一问题的认证。
	"""
	pass	# 暂时无法实现

def questStatus( entity ):
	entity.cell.questStatus( )

def onAskFamilyDart( questID, questEntityID ):
	"""
	族长邀请你跟他运镖
	@param entityid : 族长的entityid
	@param entityid : INT
	@return			: NONE
	"""
	fireEvent( "EVT_ON_INVITE_FAMILY_DART", questID, questEntityID )

#
# $Log: not supported by cvs2svn $
# Revision 1.37  2008/08/07 08:59:54  zhangyuxing
# 修改提交任务参数处理
#
# Revision 1.36  2008/05/31 03:04:59  yangkai
# 物品获取接口改变
#
# Revision 1.35  2008/04/02 09:43:28  phw
# 修正由物品触发的任务无法接的bug
#
# Revision 1.34  2008/01/30 07:14:40  huangyongwei
# 去掉了函数
# onShowQuestStatus
# onShowTaskStatus
#
# Revision 1.33  2008/01/30 02:54:32  zhangyuxing
# no message
#
# Revision 1.32  2008/01/09 03:51:19  zhangyuxing
# 增加方法 onObjectiveDetail， getObjectiveDetailFromServer，
#  onSubmitBlank， getSubmitInfoFromServer，
# onQuestGroupRewards， 处理任务目标和提交任务信息已经组奖励
#
# Revision 1.31  2007/12/26 09:44:16  phw
# method modified: completeQuest(), 修正调用不存在的target
#
# Revision 1.30  2007/12/26 09:07:32  phw
# function modified: completeQuest(), 调用questChooseReward时加入了targetID参数
#
# Revision 1.29  2007/12/18 02:18:28  zhangyuxing
# 增加：QuestFacade.submitInfo ，用于告诉客户端需要提交物品
#
# Revision 1.28  2007/12/17 02:18:43  zhangyuxing
# 修改接口completeQuest增加参数  kitTote, order
#
# Revision 1.27  2007/12/14 11:24:05  zhangyuxing
# 修改： 修改之前告诉箱子状态变化的烦琐逻辑相关
#
# Revision 1.26  2007/12/13 01:42:28  zhangyuxing
# 增加接口：def onShowTaskStatus( entity, start, incomplete ):
# 作为任务箱子状态变化的客户端相关信息的消息通知
#
# Revision 1.25  2007/12/06 00:43:26  fangpengjun
# 修改了部分接口
#
# Revision 1.24  2007/11/27 07:49:11  zhangyuxing
# 修改：代码中多写了一次关于奖励的初始化
#
# Revision 1.23  2007/11/26 01:54:57  zhangyuxing
# 修改： 把奖励物品的分类改为：
# > 	QuestFacade.reward_choose_items = None
# > 	QuestFacade.reward_rnd_items = None
# > 	QuestFacade.reward_fixed_items = None
# > 	QuestFacade.reward_others = []
#
# 奖励物品的类型也多出了一个 其他类型。
#
# Revision 1.22  2007/11/02 03:47:28  phw
# 任务系统调整，去掉了一些接口中不需要的参数，以及增添/删除了一些接口。
#
# Revision 1.21  2007/09/29 07:20:13  fangpengjun
# 调整了NPC对话的方式，注释掉了一些没有用到的接口
#
# Revision 1.20  2007/06/14 10:36:37  huangyongwei
# 整理了全局定义
#
# Revision 1.19  2007/03/29 00:39:17  huangyongwei
# 在 NPC 的任务状态中发送 EVT_ON_NPC_QUEST_STATE_CHANGED 消息
#
# Revision 1.18  2007/03/27 02:41:43  phw
# method removed: refurbisAllQuestStatus()
#
# Revision 1.17  2007/03/26 02:28:21  phw
# function modified: onShowQuestStatus(), 方法参数变动，增加了incomplete参数
#
# Revision 1.16  2007/03/23 02:38:48  fangpengjun
# 修改了刷新接口
#
# Revision 1.15  2007/03/21 01:36:50  fangpengjun
# 为客户端显示NPC任务标记添加接口questStatus（）
#
# Revision 1.14  2007/03/20 07:19:45  panguankong
# 修改了显示任务输出
#
# Revision 1.13  2007/03/10 05:55:41  panguankong
# 添加了任务状态显示功能接口
#
# Revision 1.12  2007/02/07 07:49:45  kebiao
# 增加getRandomRewards 获取随机奖励列表
#
# Revision 1.11  2007/02/07 06:39:06  kebiao
# 修改了onQuestRewards接口以及实现
#
# Revision 1.10  2006/12/29 07:25:22  huangyongwei
# 添加了获取固定奖励列表函数：
# def getAptoticRewards() :
#
# 添加了获取可选奖励列表函数：
# def getOptionalRewards() :
#
# Revision 1.9  2006/12/20 03:41:58  kebiao
# 修改completeQuest方法交任务后关闭任务窗口
#
# Revision 1.8  2006/03/25 04:49:48  phw
# 修正语法错误:
# from: return prebegin_text
# to: return QuestFacade.prebegin_text
#
# Revision 1.7  2006/03/22 02:17:50  phw
# 对任务相关的接口加放了level和hardLevel参数，并对内容作相应的修改
#
# Revision 1.6  2006/03/10 05:06:13  phw
# 修改了部份判断；增加方法onQuestRewards()和getQuestRewards()
#
# Revision 1.5  2006/03/06 05:06:37  phw
# 处理"$"开头的字符串
#
# Revision 1.4  2006/03/02 10:05:18  phw
# no message
#
# Revision 1.3  2006/02/28 08:01:32  phw
# no message
#
# Revision 1.2  2006/02/27 08:11:40  phw
# no message
#
# Revision 1.1  2006/02/23 09:44:30  phw
# no message
#
#