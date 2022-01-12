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
		QuestFacade.target = None				# ������ص�entity
		QuestFacade.id = -1						# ����ID
		QuestFacade.level = 0					# ����ȼ�
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
	# �����жϱ�������Ŀ�������ID��ƥ������
	if getQuestTarget() is not targetEntity or QuestFacade.id != questID:
		QuestFacade.reset()
		QuestFacade.target = targetEntity
		QuestFacade.id = questID

def onQuestDetail( targetEntity, questID, title, level, storyText, objectiveText, voicefile ):
	"""
	��ʾĳ�����Խӵ��������ϸ����
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
	��ʾĳ��δ��ɵ�����Ի�
	"""
	_reset( targetEntity, questID )
	QuestFacade.title = StringFormat.format( title )
	QuestFacade.level = level
	QuestFacade.incomplete_text = StringFormat.format( incompleteText )
	fireEvent( "EVT_QUEST_SHOW_INCOMPLETE_TEXT" )
	playVoice( voicefile, targetEntity.id, questID )

def onQuestPrecomplete( targetEntity, questID, title, level, precompleteText, voicefile ):
	"""
	��ϷĿ���Ѵ�ɶԻ�(�ȴ�������)
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
	������ɣ��ѽ�����ĶԻ�
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
	��������������
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
			#�����ʹ���ϻ����Ľ�������
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
	ȡ�õ�ǰ��ѡ���������⡢�ȼ����Ѷȵȼ�
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
	��ȡ�̶������б�( hyw )
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
	���ܽ���
	"""
	return QuestFacade.reward_skills

def getChooseRewardItems() :
	"""
	��ȡ��ѡ�����б�( hyw )
	"""
	return QuestFacade.reward_choose_items

def getRndRewardItems() :
	"""
	��ȡ��������б�( hyw )
	"""
	return QuestFacade.reward_rnd_items

def getRewardIsUseSlots():
	return QuestFacade.reward_useSlots

# -----------------------------------------------------
def acceptQuest( ):
	"""
	��������
	"""
	target = getQuestTarget()
	if target is None:
		bw.player().cell.questAccept( QuestFacade.id, 0 )	# �����һ�α�ѡ�������
	else:
		bw.player().cell.questAccept( QuestFacade.id, target.id )

def declineQuest( ):
	"""
	�ܾ���������
	"""
	target = getQuestTarget()
	if target is None:
		print "decline quest."
		#bw.player().cell.declineSelectedQuest( target.id )
	else:
		print "decline quest, we do nothing."


def completeQuest( rewardIndex, codeStr ):
	"""
	�������(��)����

	@param rewardIndex: ѡ��������(�����)��û��������-1
	@type  rewardIndex: INT8
	@param codeStr: ����Ŀ���ַ���������Ϣ
	@type  codeStr: STRING

	"""
	fireEvent( "EVT_END_GOSSIP" )
	if QuestFacade.reward_useSlots:#��ʹ�ÿ������������͵ģ��򴥷��ϻ���
		bw.player().triggerQuestRewardSlots( QuestFacade.id, rewardIndex, codeStr, getQuestTarget().id )
	else:
		bw.player().cell.questChooseReward( QuestFacade.id, rewardIndex, codeStr, getQuestTarget().id )

def finishQuest():
	"""
	������رա���ť
	"""
	print "quest finish, we do nothing."

def confirmAcceptQuest():
	"""
	�����ж�Ա���ڽ���xxx�������Ƿ�Ҫ��ʼͬ�������񣿡���һ�������֤��
	"""
	pass	# ��ʱ�޷�ʵ��

def questStatus( entity ):
	entity.cell.questStatus( )

def onAskFamilyDart( questID, questEntityID ):
	"""
	�峤�������������
	@param entityid : �峤��entityid
	@param entityid : INT
	@return			: NONE
	"""
	fireEvent( "EVT_ON_INVITE_FAMILY_DART", questID, questEntityID )

#
# $Log: not supported by cvs2svn $
# Revision 1.37  2008/08/07 08:59:54  zhangyuxing
# �޸��ύ�����������
#
# Revision 1.36  2008/05/31 03:04:59  yangkai
# ��Ʒ��ȡ�ӿڸı�
#
# Revision 1.35  2008/04/02 09:43:28  phw
# ��������Ʒ�����������޷��ӵ�bug
#
# Revision 1.34  2008/01/30 07:14:40  huangyongwei
# ȥ���˺���
# onShowQuestStatus
# onShowTaskStatus
#
# Revision 1.33  2008/01/30 02:54:32  zhangyuxing
# no message
#
# Revision 1.32  2008/01/09 03:51:19  zhangyuxing
# ���ӷ��� onObjectiveDetail�� getObjectiveDetailFromServer��
#  onSubmitBlank�� getSubmitInfoFromServer��
# onQuestGroupRewards�� ��������Ŀ����ύ������Ϣ�Ѿ��齱��
#
# Revision 1.31  2007/12/26 09:44:16  phw
# method modified: completeQuest(), �������ò����ڵ�target
#
# Revision 1.30  2007/12/26 09:07:32  phw
# function modified: completeQuest(), ����questChooseRewardʱ������targetID����
#
# Revision 1.29  2007/12/18 02:18:28  zhangyuxing
# ���ӣ�QuestFacade.submitInfo �����ڸ��߿ͻ�����Ҫ�ύ��Ʒ
#
# Revision 1.28  2007/12/17 02:18:43  zhangyuxing
# �޸Ľӿ�completeQuest���Ӳ���  kitTote, order
#
# Revision 1.27  2007/12/14 11:24:05  zhangyuxing
# �޸ģ� �޸�֮ǰ��������״̬�仯�ķ����߼����
#
# Revision 1.26  2007/12/13 01:42:28  zhangyuxing
# ���ӽӿڣ�def onShowTaskStatus( entity, start, incomplete ):
# ��Ϊ��������״̬�仯�Ŀͻ��������Ϣ����Ϣ֪ͨ
#
# Revision 1.25  2007/12/06 00:43:26  fangpengjun
# �޸��˲��ֽӿ�
#
# Revision 1.24  2007/11/27 07:49:11  zhangyuxing
# �޸ģ������ж�д��һ�ι��ڽ����ĳ�ʼ��
#
# Revision 1.23  2007/11/26 01:54:57  zhangyuxing
# �޸ģ� �ѽ�����Ʒ�ķ����Ϊ��
# > 	QuestFacade.reward_choose_items = None
# > 	QuestFacade.reward_rnd_items = None
# > 	QuestFacade.reward_fixed_items = None
# > 	QuestFacade.reward_others = []
#
# ������Ʒ������Ҳ�����һ�� �������͡�
#
# Revision 1.22  2007/11/02 03:47:28  phw
# ����ϵͳ������ȥ����һЩ�ӿ��в���Ҫ�Ĳ������Լ�����/ɾ����һЩ�ӿڡ�
#
# Revision 1.21  2007/09/29 07:20:13  fangpengjun
# ������NPC�Ի��ķ�ʽ��ע�͵���һЩû���õ��Ľӿ�
#
# Revision 1.20  2007/06/14 10:36:37  huangyongwei
# ������ȫ�ֶ���
#
# Revision 1.19  2007/03/29 00:39:17  huangyongwei
# �� NPC ������״̬�з��� EVT_ON_NPC_QUEST_STATE_CHANGED ��Ϣ
#
# Revision 1.18  2007/03/27 02:41:43  phw
# method removed: refurbisAllQuestStatus()
#
# Revision 1.17  2007/03/26 02:28:21  phw
# function modified: onShowQuestStatus(), ���������䶯��������incomplete����
#
# Revision 1.16  2007/03/23 02:38:48  fangpengjun
# �޸���ˢ�½ӿ�
#
# Revision 1.15  2007/03/21 01:36:50  fangpengjun
# Ϊ�ͻ�����ʾNPC��������ӽӿ�questStatus����
#
# Revision 1.14  2007/03/20 07:19:45  panguankong
# �޸�����ʾ�������
#
# Revision 1.13  2007/03/10 05:55:41  panguankong
# ���������״̬��ʾ���ܽӿ�
#
# Revision 1.12  2007/02/07 07:49:45  kebiao
# ����getRandomRewards ��ȡ��������б�
#
# Revision 1.11  2007/02/07 06:39:06  kebiao
# �޸���onQuestRewards�ӿ��Լ�ʵ��
#
# Revision 1.10  2006/12/29 07:25:22  huangyongwei
# ����˻�ȡ�̶������б�����
# def getAptoticRewards() :
#
# ����˻�ȡ��ѡ�����б�����
# def getOptionalRewards() :
#
# Revision 1.9  2006/12/20 03:41:58  kebiao
# �޸�completeQuest�����������ر����񴰿�
#
# Revision 1.8  2006/03/25 04:49:48  phw
# �����﷨����:
# from: return prebegin_text
# to: return QuestFacade.prebegin_text
#
# Revision 1.7  2006/03/22 02:17:50  phw
# ��������صĽӿڼӷ���level��hardLevel������������������Ӧ���޸�
#
# Revision 1.6  2006/03/10 05:06:13  phw
# �޸��˲����жϣ����ӷ���onQuestRewards()��getQuestRewards()
#
# Revision 1.5  2006/03/06 05:06:37  phw
# ����"$"��ͷ���ַ���
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