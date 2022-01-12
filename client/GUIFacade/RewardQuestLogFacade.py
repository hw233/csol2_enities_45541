# -*- coding: gb18030 -*-

from bwdebug import *
from event.EventCenter import *
from QuestModule import QuestReward
import csdefine

class RewardQuestLogFacade:
	@staticmethod
	def reset():
		RewardQuestLogFacade.canAcceptRewardQuestRecord = []	#���е����������б�[rewardQuestTypeImpl,]
		RewardQuestLogFacade.acceptedRewardQuestList = []		#�ѽ����������б�[questID,]
		RewardQuestLogFacade.completedRewardQuestRecord = []	#����ɵ����������б�[questID,]
		RewardQuestLogFacade.nextRefreshTime = 0				#��������ˢ��ʱ��
		RewardQuestLogFacade.degree = 0							#�ѽ��������������
		
def getRewardQuestRecord():
	"""
	��ȡ���е����������б�
	"""
	return RewardQuestLogFacade.canAcceptRewardQuestRecord
	
def getAcceptedRewardQuestList():
	"""
	��ȡ�ѽӵ����������б�
	"""
	return RewardQuestLogFacade.acceptedRewardQuestList
	
def getCompletedRewardQuestRecord():
	"""
	��ȡ��������������б�
	"""
	return RewardQuestLogFacade.completedRewardQuestRecord
	
def getNextReFreshTime():
	"""
	��ȡ���������´�ˢ�µ�ʱ��
	"""
	return RewardQuestLogFacade.nextRefreshTime
	
def getDegree():
	"""
	��ȡ���������ѽӴ���
	"""
	return RewardQuestLogFacade.degree
	
def getQuestStateByID( questID ):
	"""
	��������ID��ȡ����״̬
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
	������������ID��ȡ������
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
	����������������
	"""
	RewardQuestLogFacade.canAcceptRewardQuestRecord = canAcceptRewardQuestRecord
	RewardQuestLogFacade.acceptedRewardQuestList = acceptedRewardQuestList
	RewardQuestLogFacade.completedRewardQuestRecord = completedRewardQuestRecord
	RewardQuestLogFacade.nextRefreshTime = nextRefreshTime
	RewardQuestLogFacade.degree = degree
	
def updateRewardQuestState( questID, state, degree ):
	"""
	����������������
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
	
