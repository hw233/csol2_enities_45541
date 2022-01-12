# -*- coding: gb18030 -*-
#
"""
����ϵͳ for Role ����
"""
# $Id: RoleQuestInterface.py,v 1.37 2008-09-02 01:01:14 songpeifang Exp $

import time
import cPickle
import BigWorld
import csdefine
import event.EventCenter as ECenter # hyw( 2008.02.25 )
import GUIFacade
from bwdebug import *
from gbref import rds
from MessageBox import *
import Const
import random
import csconst
import csstatus
import Define
from config.client.msgboxtexts import Datas as mbmsgs

from love3 import g_questDataInst

# �����ԣ�0.1��ᵼ��������һ��tick�﷢�����������Ӷ�ʹ��������һ��tick����Ȼ������������Ϣ
TIME_TO_GET_ONE_TASKS_LOG = 0.3

def isMainQuest( questID ):
	return questID / 100000 == 201

class RoleQuestInterface:
	"""
	�������ӿ�
	"""
	def __init__( self ):
		#self.questIDList = []					# ע�͵����ŵ���Դ������������˲���ҪԤ�Ƚ������( by hyw -- 2008.06.10 )
		self.currentDoingQuestIDList = []
		self.completedQuestIDList = []			#�Ѿ���ɵ�����
		self.learnSkillQuestIDList = []			# ѧϰ����Ŀ������
		self.soundPriority		= csdefine.GOSSIP_PLAY_VOICE_PRIORITY_DEFAULT		#�������������ɵ͵��߷ֱ�Ϊ0��1��2
		self.gossipVoices = 0																#�Ի�������


	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache�������
		"""
		# self is BigWorld.player() ����ж��Ǳ����
		# �ⲿ�ݴ����Ƿ�Ӧ����onBecomePlayer()������ȽϺ�,�д��о�.
		if self is BigWorld.player() and not GUIFacade.questLogIsInit():
			GUIFacade.initQuestLog()
			#self.cell.initTasksTable()
			#self.cell.requestCompletedQuest()  # ע�͵����ŵ���Դ����������( by hyw -- 2008.06.10 )


#	def requestQuestLog( self ):				# ע�͵�����Ϊ�������ְ����ڷ���( by hyw -- 2008.06.09 )
#		"""
#		��ȡһ��������־
#		"""
#		if len( self.questIDList ) == 0:
#			return
#		id = self.questIDList.pop()
#		self.currentDoingQuestIDList.append( id )
#		self.cell.requestQuestLog( id )
#		BigWorld.callback( TIME_TO_GET_ONE_TASKS_LOG, self.requestQuestLog )
#

	def onEnterSpace_( self ):
		"""
		����һ���µĵ�ͼ������λ�棩
		"""
		BigWorld.callback( 1.0, self.cell.onEnterSpaceAutoNextQuest )
		
	# ---------------------------------->
	# �������ķ���
	# ---------------------------------->
	def onQuestLogAdd( self, questID, canShare, completeRuleType, tasks, level, reward ):
		"""
		Define method.
		@param      questID: ����ID
		@type       questID: UINT32
		@param	   canShare: �Ƿ�������
		@type      canShare: INT8
		@param	   completeRuleType: ��ɹ���
		@param	   completeRuleType: INT8
		@param        tasks: ����Ŀ��ʵ��
		@type         tasks: QUESTDATA
		@param msgObjective: ����Ŀ������
		@type  msgObjective: STRING
		before_accept
		"""
		qData = g_questDataInst.get( questID )
		title = qData.getTitle()
		msgObjective = qData.msg_objective
		msgDetail = qData.msg_log_detail
		
		GUIFacade.onAddQuestLog( questID, canShare, completeRuleType, tasks, title, level, msgObjective, msgDetail, reward )
		
		for e in tasks._tasks.itervalues():
			if e.getType() == csdefine.QUEST_OBJECTIVE_TEAM:
				self.onQuestTeamMemberChange( questID )
			if e.getType() == csdefine.QUEST_OBJECTIVE_SKILL_LEARNED:	# ѧϰ����Ŀ������
				if isMainQuest( questID ) and questID not in self.learnSkillQuestIDList:
					self.learnSkillQuestIDList.append( questID )

		if questID not in self.currentDoingQuestIDList:
			self.currentDoingQuestIDList.append( questID )
		# ������ΧNPC����ʾ״̬
		self.refurbishAroundQuestStatus()
		# ֪ͨ����ָ���������������һ������
		ECenter.fireEvent("EVT_ON_ADD_QUEST_SIGN",questID )
		
		rds.opIndicator.onPlayerAddedQuest( questID )

	def onShowQuestLog( self, questID ) :
		"""
		Define method.
		@param      questID: ����ID
		@type       questID: UINT32
		��������־���棬����λ��ָ��������
		"""
		#if not GUIFacade.hasQuestLog( questID ): return		# ������û�и����񣬶���������־����
		GUIFacade.setQuestLogSelect( questID )
		ECenter.fireEvent( "EVT_ON_SHOW_QUEST_WINDOW" )
		ECenter.fireEvent( "EVT_ON_PLAY_QUEST_EFFECT", questID )

#	def onQuestIDListReceive( self, questIDList ):
#		"""
#		ע�͵�����Ϊ�������ְ����ڷ���( hyw -- 2008.06.09 )
#		Define method
#		@param      questID: ����ID
#		@type       questID: UINT32
#		"""
#		self.questIDList = questIDList
#		if len( self.questIDList ) != 0:
#			self.requestQuestLog()

	def onCompletedQuestIDListReceive( self, questIDList ):
		"""
		Define method
		@param      questID: ����ID
		@type       questID: UINT32
		"""
		self.completedQuestIDList = questIDList

	def onQuestLogRemove( self, questID, isAbandon ):
		"""
		Define method.
		@param   questID: ����ID
		@type    questID: UINT32
		@param isAbandon: �Ƿ���ҷ�����
		@type  isAbandon: INT8
		after_complete
		"""
		if questID != 0:
			if isAbandon:
				self.currentDoingQuestIDList.remove( questID )
				GUIFacade.onAbandonQuest( questID )
			else:
				if questID in self.currentDoingQuestIDList:
					self.currentDoingQuestIDList.remove( questID )
					self.completedQuestIDList.append( questID )
				GUIFacade.onRemoveQuestLog( questID )
			# ֪ͨ����ָ��������
			rds.opIndicator.onPlayerRemovedQuest( questID )
			# �Ƴ�ѧϰ����Ŀ������
			if questID in self.learnSkillQuestIDList:
				self.learnSkillQuestIDList.remove( questID )

		# ������ΧNPC����ʾ״̬
		self.refurbishAroundQuestStatus()
		ECenter.fireEvent("EVT_ON_REMOVE_QUEST_SIGN",questID )

	def onTaskStateUpdate( self, questID, taskState ):
		"""
		Define method.
		@param   questID: ����ID
		@type    questID: UINT32
		@param taskIndex: ����Ŀ���������е�����(λ��)
		@type  taskIndex: UINT8
		@param taskState: ����Ŀ��
		@type  taskState: QUEST_TASK
		ע�ͣ�
		��������Ŀ��״̬����չ������״̬�ĵ��µ�NPC���¡� ��������� ���-> δ��� �� �� δ���->��� ��
		"""
		update = GUIFacade.getQuestLogs()[questID]["tasks"]._tasks[taskState.index].isCompleted()

		GUIFacade.onTaskStateUpdate( questID, taskState.index, taskState )
		if  update  != taskState.isCompleted():
			self.refurbishAroundQuestStatus()
			ECenter.fireEvent("EVT_ON_REMOVE_QUEST_SIGN",questID )
		if update :
			rds.helper.courseHelper.roleOperate( "jieshourenwu_caozuo" )		# ������һ�����������̰��� hyw( 2009.06.13 )
		rds.areaEffectMgr.startSpaceEffect( self )  # ����״̬�ı䴥��������Ч
		rds.opIndicator.onPlayerQuestStateChanged( questID, taskState.index )

	def onSetGossipText( self, gossipText ):
		"""
		Define method.
		@param 		player: ROLE ʵ��
		@type 		 player: OBJECT_ID
		@param 		text: �������񴰿��ı�
		@type 		 text: str
		@return: 	None
		"""
		GUIFacade.onSetGossipText( gossipText )

	def onAddGossipOption( self, talkID, title, type ):
		"""
		����ϵͳ��ͨ�Ի�
		Define method.
		@param 		player: ROLE ʵ��
		@type 		 player: OBJECT_ID
		@type 		talkID: string
		@type 		 title: string
		@return:	 None
		"""
		GUIFacade.onAddGossipOption( talkID, title, type )
		target = self.targetEntity
		if target:
			optVoice = rds.gossipVoiceMgr.getOptionVoice( target.className, talkID )
			if optVoice:
				self.gossipVoices += 1

	def onAddGossipQuestOption( self, questID, state, lv  ):
		"""
		����ϵͳ����Ի�
		Define method.
		@param 		player: ROLE ʵ��
		@type  		player: OBJECT_ID
		@type dlgKey: string
		@type   title: string
		"""
		qData = g_questDataInst.get( questID )
		title = qData.getTitle()
		
		GUIFacade.onAddGossipQuestOption( questID, title, state, lv )
		target = self.targetEntity
		if target:
			actState = Const.GOSSIP_QUEST_STATES.get( state, "" )
			questVoice = rds.gossipVoiceMgr.getQuestVoice( questID, actState, target.className )
			if questVoice:
				self.gossipVoices += 1

	def onGossipComplete( self, targetID ):
		"""
		Define method.
		@param 		 player: ROLE ʵ��
		@type 		 player: OBJECT_ID
		@return: None
		"""
		GUIFacade.onGossipComplete( targetID )
		rds.opIndicator.onPlayerTalkToNPC( targetID )
		if self.gossipVoices > 0:						#�жԻ�����
			return
		self.playNPCVoice( targetID )							#����Ĭ������

	def onQuestDetail( self, questID, level, targetID ):
		"""
		Define method.
		@type	questID: INT32
		@type	title: string
		@type	level: INT32
		@type	storyText: str
		@type	objectiveText: str
		@type	targetID: OBJECT_ID
		@return: None
		csdefine.QUEST_STATE_NOT_HAVE:		# ��û�нӸ�����
		"""
		qData = g_questDataInst.get( questID )
		title = qData.getTitle()
		storyText = qData.msg_detail
		objectiveText = qData.msg_objective
		voicefile = qData.voe_detail
		GUIFacade.onQuestDetail( BigWorld.entities.get( targetID ), questID, title, level, storyText, objectiveText, voicefile )
		rds.opIndicator.onPlayerTalkToNPC( targetID )

	def onQuestIncomplete( self, questID, level, targetID ):
		"""
		Define method.
		@type	questID: INT32
		@type	title: string
		@type	level: INT32
		@type	incompleteText: str
		@type	targetID: OBJECT_ID
		@return: None
		csdefine.QUEST_STATE_NOT_FINISH:	# ��û�����Ŀ��
		"""
		qData = g_questDataInst.get( questID )
		title = qData.getTitle()
		incompleteText = qData.msg_incomplete
		voicefile = qData.voe_incomplete
		GUIFacade.onQuestIncomplete( BigWorld.entities.get( targetID ), questID, title, level, incompleteText, voicefile )
		rds.opIndicator.onPlayerTalkToNPC( targetID )

	def onQuestPrecomplete( self, questID, level, targetID ):
		"""
		Define method.
		@type	questID: INT32
		@type	title: string
		@type	level: INT32
		@type	precompleteText: str
		@type	targetID: OBJECT_ID
		@return: None
		csdefine.QUEST_STATE_FINISH:		# �����Ŀ��,��û������
		"""
		qData = g_questDataInst.get( questID )
		title = qData.getTitle()
		precompleteText = qData.msg_precomplete if len( qData.msg_precomplete ) else qData.msg_log_detail
		voicefile = qData.voe_precomplete
		GUIFacade.onQuestPrecomplete( BigWorld.entities.get( targetID ), questID, title, level, precompleteText, voicefile )
		rds.opIndicator.onPlayerTalkToNPC( targetID )

	def onQuestComplete( self, questID, level, targetID, voicefile ):
		"""
		Define method.
		@type	questID: INT32
		@type	title: string
		@type	level:INT32
		@type	completeText:str
		@type	targetID: OBJECT_ID
		@return: None
		"""
		qData = g_questDataInst.get( questID )
		title = qData.getTitle()
		completeText = qData.msg_complete
		voicefile = qData.voe_precomplete
		precompleteText = qData.msg_precomplete if len( qData.msg_precomplete ) else qData.msg_log_detail
		voicefile = qData.voe_precomplete
		GUIFacade.onQuestComplete( BigWorld.entities.get( targetID ), questID, title, level, completeText, voicefile )

	def onQuestRewards( self, questID, rewards ):
		"""
		Define method.
		@type	questID: INT32
		@param	rewards: ������
		@type	rewards: items
		@return: None
		"""
		GUIFacade.onQuestRewards( self, questID, rewards )

	def getLastSelectedQuest( self ):
		"""
		@return: questID
		"""
		return self.lastSelectedQuest

	def onEndGossip( self ) :
		"""
		Define method.
		@param player: ROLE ʵ��
		@type  player: OBJECT_ID
		@return: None
		"""
		targetEntity = self.targetEntity
		GUIFacade.onEndGossip( targetEntity )
		self.gossipVoices = 0


	def onQuestBoxStateUpdate( self ):
		"""
		Define method.
		@param questBoxID: �������ӵ�ID
		@type  questBoxID: OBJECT_ID
		@param state: �������ӵ�ID
		@type  state: OBJECT_ID
		"""
		for key, entity in BigWorld.entities.items():
			if hasattr( entity, "refurbishTaskStatus" ):
				entity.refurbishTaskStatus()

	def addGroupRewardsInfo( self, questID, rewards ):
		"""
		Define method.
		@param rewards: �������б�
		@type  rewards: array of string
		"""
		ECenter.fireEvent("EVT_QUEST_SHOW_GROUP_REWARDS_DETAIL", questID, rewards)

	def onQuestObjectiveDetail( self, questID, objectiveDetail ):
		"""
		Define method.
		��������client���͵�����Ŀ����Ϣ��
		@type	questID: INT32
		@param	objectiveDetail: ����Ŀ����Ϣ
		@type   objectiveDetail:  string
		"""
		GUIFacade.onObjectiveDetail( self, questID, cPickle.loads( objectiveDetail ) )

	def onQuestSubmitBlank( self, questID, submitInfo ):
		"""
		Define method.
		��������client���͵��ύ����Ŀ����Ϣ��
		@type	questID: INT32
		@param	submitInfo: ����Ŀ����Ϣ
		@type   submitInfo:  string
		"""
		GUIFacade.onSubmitBlank( self, questID, cPickle.loads( submitInfo ) )

	def onTeamMemberChange( self ):
		"""
		���������б仯�����·�������������������Ϣ
		"""
		for questID in GUIFacade.getQuestLogs():
			if GUIFacade.hasQuestTaskType( questID, csdefine.QUEST_OBJECTIVE_TEAM ):
				self.onQuestTeamMemberChange( questID )


	def onQuestTeamMemberChange( self, questID ):
		"""
		���·�������������������Ϣ
		"""
		for e in GUIFacade.getQuestLogs()[questID]["tasks"].getTasks().itervalues():
			count = 0
			if not ( e.getType() == csdefine.QUEST_OBJECTIVE_TEAM ):
				continue
			for key in self.teamMember:
				if key == self.id:
					continue
				if (self.teamMember[key].raceclass & csdefine.RCMASK_CLASS) == e.getOccupation():
					count += 1
			self.cell.updateQuestTeamTask( questID , e.index, count )

	def isQuestCompleted( self, questID ):
		"""
		"""
		return questID in self.completedQuestIDList

	def isQuestInDoing( self, questID ):
		"""
		"""
		return questID in self.currentDoingQuestIDList

	def isDoingLearnSkillQuest( self, questID ):
		"""
		�Ƿ����ڽ���ĳѧϰ����Ŀ������
		"""
		return questID in self.learnSkillQuestIDList

	def isLearnSkillQuestCompleted( self ):
		"""
		�Ƿ���ѧϰ����Ŀ���������
		"""
		for questID in self.learnSkillQuestIDList:
			if GUIFacade.questIsCompleted( questID ):
				return True
		return False

	def dartTongInvite( self, questID, questEntityID ):
		"""
		define method.
		��������Ҳ�������������
		����ҽ���������ٻ������,ֱ����client��������
		@param entityid
		@type  entityid
		"""
		#��ʾ�����������������������
		GUIFacade.onAskFamilyDart( questID, questEntityID )


	def showTrainGem( self ):
		"""
		"""
		pass
		#ECenter.fireEvent("EVT_ON_EXP_GEM_SHOW")

	def isQuestMonster( self, monster ):
		"""
		�жϸ����� monster �Ƿ��������� NPC
		"""
		if monster is None : return False
		if monster.__class__.__name__ != "ConvoyMonster"  : return False
		if monster.ownerID != self.id : return False
		return True

	def isDarting( self, player ):
		"""
		����Ƿ���������������
		"""
		for qID in GUIFacade.getQuestLogs():
			if GUIFacade.getQuestType( qID ) == csdefine.QUEST_TYPE_DART or GUIFacade.getQuestType( qID ) == csdefine.QUEST_TYPE_MEMBER_DART:
				return True
		return False

	def isRobbing( self, player ):
		"""
		����Ƿ��н�����������
		"""
		for qID in GUIFacade.getQuestLogs():
			if GUIFacade.getQuestType( qID ) == csdefine.QUEST_TYPE_ROB:
				return True
		return False

	def openMoneyToYinpiaoWindow( self ):
		"""
		define method
		��Ʊ��ֵ����
		"""
		pass

	def playIntonateBar( self, lastTime ):
		"""
		define method.
		����һ��������������һ���Ľ����������ɷ���������
		"""
		GUIFacade.onSkillIntonate( lastTime )

	def readRandomQuestRecord( self, questID ):
		"""
		������֪ͨ�ͻ����Ƿ�Ҫ��ȡ������
		"""
		ECenter.fireEvent("EVT_ON_LOOP_GROUP_READ_RECORD", questID )

	def acceptQuestConfirm( self, questID, msgStr ):
		"""
		define method.
		������֪ͨ�ͻ����Ƿ�Ҫ��ȡĳ������
		questID������ID
		msgStr���Ի����е����ݣ����硰�Ƿ�Ҫ��XXǮ���½�ȡ������?��
		"""
		ECenter.fireEvent("EVT_ON_ACCEPT_QUEST_CONFIRM", questID, msgStr )


	def showQuestMsg( self, questMsg ):
		"""
		define method
		��ʾ������ڡ�
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_SCENARIO_TIPS", questMsg )
	
	def resetsSoundPriority( self ):
		"""
		���öԻ����ȼ�
		"""
		self.soundPriority = csdefine.GOSSIP_PLAY_VOICE_PRIORITY_DEFAULT

	def playNPCVoice( self, targetID ):
		"""
		����NPCĬ������
		"""
		target = BigWorld.entities.get( targetID )
		if target is None:return
		if target.voiceBan:
			return
		model = target.getModel()
		if model is None:
			return
		voices = rds.npcVoice.getClickVoice( int(target.className) )
		if len( voices ) <= 0:
			return
		voice = random.choice( voices )
		rds.soundMgr.playVocality( voice, model )
		try:
			target.setVoiceDelate()
		except:
			return

	def receiveRewardQuestDatas( self, canAcceptRewardQuestRecord, acceptedRewardQuestList, completedRewardQuestRecord, remainRefreshTime, degree ):
		"""
		������������������
		"""
		GUIFacade.receiveRewardQuestDatas( canAcceptRewardQuestRecord, acceptedRewardQuestList, completedRewardQuestRecord, remainRefreshTime, degree )
		ECenter.fireEvent( "EVT_ON_REWARD_QUESTS_UPDATE" )
		
	def rewardQuestAccept( self, questID ):
		"""
		������������
		"""
		self.cell.rewardQuestAccept( questID )
		pass
		
	def sendRewardQuestState( self, questID, state, degree ):
		"""
		����������������
		"""
		GUIFacade.updateRewardQuestState( questID, state, degree )
		ECenter.fireEvent("EVT_ON_QUEST_STATE_CHANGED", questID, state )
		
	def useItemRefreshRewardQuest( self ):
		"""
		����Ʒˢ����������
		"""
		lowItemID  = csconst.REWARD_QUEST_LOW_ITEM
		highItemID  = csconst.REWARD_QUEST_HIGH_ITEM
		lowItems = self.findItemsByIDFromNKCK( lowItemID )
		highItems = self.findItemsByIDFromNKCK( highItemID )
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return
		if len( lowItems ) == 0 and len( highItems ) == 0:
			self.statusMessage( csstatus.HAVE_NOT_REWARD_QUEST_REFRESH_ITEMS )
			return
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().cell.useItemRefreshRewardQuest()

		# "����ȡ�����������Ƿ������"
		msg = mbmsgs[0x10ae]
		showAutoHideMessage( 5, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def triggerQuestRewardSlots( self, questID, rewardIndex, codeStr, questTargetID ):
		"""
		�����ϻ���
		"""
		ECenter.fireEvent( "EVT_ON_SLOT_MACHINE_SHOW", questID, rewardIndex, codeStr, questTargetID )
	
	def getQuestRewardSlots( self, questID, rewardIndex, codeStr, questTargetID, useGold ):
		"""
		���ȡ�������������ϻ�����
		"""
		self.cell.getQuestRewardSlots( questID, rewardIndex, codeStr, questTargetID, useGold )
	
	def setQuestRewardSlots( self, questID, multiple ):
		"""
		define method.
		�����������������ϻ�����
		"""
		ECenter.fireEvent( "EVT_ON_SLOT_MACHINE_RECEIVE_MULTIPLE", multiple )

	def getTaskIndexMonsters( self ):
		"""
		��ȡ��Ҫ��ʾ���Ƶ���������б���ǰ��������б����еģ�
		"""
		taskIndexMonsters = []
		for questID in GUIFacade.getQuestLogs().keys():
			qData = g_questDataInst.get( questID )
			taskIndexs = qData.getTaskIndexs()
			for taskIndex in taskIndexs:
				snMonsters = []
				if not GUIFacade.isTaskCompleted( questID, taskIndex ):	# ����Ŀ��δ���
					snMonsters = qData.getTaskIndexMonsters( taskIndex )
				taskIndexMonsters.extend( snMonsters )
		taskIndexMonsters = list( set( taskIndexMonsters ) )
		return taskIndexMonsters

# RoleQuestInterface.py


