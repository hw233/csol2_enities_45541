# -*- coding: gb18030 -*-

from bwdebug import *
from event.EventCenter import *
from QuestModule import QuestReward
import csdefine

class RewardQuestLogFacade:
	@staticmethod
	def reset():
		RewardQuestLogFacade.canAcceptRewardQuestRecord = []	#所有的悬赏任务列表[rewardQuestTypeImpl,]
		RewardQuestLogFacade.acceptedRewardQuestList = []		#已接悬赏任务列表[questID,]
		RewardQuestLogFacade.completedRewardQuestRecord = []	#已完成的悬赏任务列表[questID,]
		RewardQuestLogFacade.nextRefreshTime = 0				#悬赏任务刷新时间
		RewardQuestLogFacade.degree = 0							#已接受悬赏任务次数
		
def getRewardQuestRecord():
	"""
	获取所有的悬赏任务列表
	"""
	return RewardQuestLogFacade.canAcceptRewardQuestRecord
	
def getAcceptedRewardQuestList():
	"""
	获取已接的悬赏任务列表
	"""
	return RewardQuestLogFacade.acceptedRewardQuestList
	
def getCompletedRewardQuestRecord():
	"""
	获取已完成悬赏任务列表
	"""
	return RewardQuestLogFacade.completedRewardQuestRecord
	
def getNextReFreshTime():
	"""
	获取悬赏任务下次刷新的时间
	"""
	return RewardQuestLogFacade.nextRefreshTime
	
def getDegree():
	"""
	获取悬赏任务已接次数
	"""
	return RewardQuestLogFacade.degree
	
def getQuestStateByID( questID ):
	"""
	根据任务ID获取任务状态
	"""
	canAcceptRewardQuestIDRecord = [ quest.getQuestID() for quest in RewardQuestLogFacade.canAcceptRewardQuestRecord ]
	assert questID in canAcceptRewardQuestIDRecord,"questID:%s must in %s" % ( questID, canAcceptRewardQuestIDRecord )
	if questID in RewardQuestLogFacade.acceptedRewardQuestList:
		return csdefine.REWARD_QUEST_ACCEPT
	elif questID in RewardQuestLogFacade.completedRewardQuestRecord:
		return csdefine.REWARD_QUEST_COMPLETED
	else:
		return csdefine.REWARD_QUEST_CAN_ACCEPT
		
def getRewardByQuestID( questID ):
	"""
	根据悬赏任务ID获取任务奖励
	"""
	rewardDetails = {}
	for rewardQuest in RewardQuestLogFacade.canAcceptRewardQuestRecord:
		if rewardQuest.getQuestID() == questID:
			rewards = rewardQuest.getRewardsDetail()
			for reward in rewards:
				qr = QuestReward.createByStream( reward )
				if qr.type() == csdefine.QUEST_REWARD_EXP_FROM_REWARD_QUEST_QUALITY:
					rewardDetails["rewards_exp"] = qr
				elif qr.type() == csdefine.QUEST_REWARD_MONEY_FROM_REWARD_QUEST_QUALITY:
					rewardDetails["rewards_money"] = qr
	return rewardDetails
			

#----------------------------------------------	
#call by server
#-----------------------------------------------
def receiveRewardQuestDatas( canAcceptRewardQuestRecord, acceptedRewardQuestList, completedRewardQuestRecord, nextRefreshTime, degree ):
	"""
	接受悬赏任务数据
	"""
	RewardQuestLogFacade.canAcceptRewardQuestRecord = canAcceptRewardQuestRecord
	RewardQuestLogFacade.acceptedRewardQuestList = acceptedRewardQuestList
	RewardQuestLogFacade.completedRewardQuestRecord = completedRewardQuestRecord
	RewardQuestLogFacade.nextRefreshTime = nextRefreshTime
	RewardQuestLogFacade.degree = degree
	
def updateRewardQuestState( questID, state, degree ):
	"""
	更新悬赏任务数据
	"""
	print "updateRewardQuestState----------",questID, state
	for rewardQuest in RewardQuestLogFacade.canAcceptRewardQuestRecord:
		if questID != rewardQuest.getQuestID():continue
		if state == csdefine.REWARD_QUEST_ACCEPT:
			if questID not in RewardQuestLogFacade.acceptedRewardQuestList:		
				RewardQuestLogFacade.acceptedRewardQuestList.append( questID )
				#RewardQuestLogFacade.degree += 1
			if questID in RewardQuestLogFacade.completedRewardQuestRecord:
				RewardQuestLogFacade.completedRewardQuestRecord.remove( questID )
		elif state == csdefine.REWARD_QUEST_COMPLETED:
			if questID not in RewardQuestLogFacade.completedRewardQuestRecord:
				RewardQuestLogFacade.completedRewardQuestRecord.append( questID )
			if questID in RewardQuestLogFacade.acceptedRewardQuestList:
				RewardQuestLogFacade.acceptedRewardQuestList.remove( questID )
		elif state == csdefine.REWARD_QUEST_CAN_ACCEPT:
			if questID in RewardQuestLogFacade.acceptedRewardQuestList:
				RewardQuestLogFacade.acceptedRewardQuestList.remove( questID )
			if questID in RewardQuestLogFacade.completedRewardQuestRecord:
				RewardQuestLogFacade.completedRewardQuestRecord.remove( questID )
		RewardQuestLogFacade.degree = degree
	
