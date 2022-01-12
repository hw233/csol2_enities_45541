# -*- coding: gb18030 -*-
#
"""
任务系统 for Role 部份
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

# 经测试，0.1秒会导致数据在一个tick里发给服务器，从而使服务器在一个tick里仍然产生大量的消息
TIME_TO_GET_ONE_TASKS_LOG = 0.3

def isMainQuest( questID ):
	return questID / 100000 == 201

class RoleQuestInterface:
	"""
	玩家任务接口
	"""
	def __init__( self ):
		#self.questIDList = []					# 注释掉，放到资源加载中请求，因此不需要预先接收这个( by hyw -- 2008.06.10 )
		self.currentDoingQuestIDList = []
		self.completedQuestIDList = []			#已经完成的任务
		self.learnSkillQuestIDList = []			# 学习技能目标任务
		self.soundPriority		= csdefine.GOSSIP_PLAY_VOICE_PRIORITY_DEFAULT		#播放语音级别，由低到高分别为0、1、2
		self.gossipVoices = 0																#对话语音数


	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		# self is BigWorld.player() 这个判断是必须的
		# 这部份代码是否应该在onBecomePlayer()里做会比较好,有待研究.
		if self is BigWorld.player() and not GUIFacade.questLogIsInit():
			GUIFacade.initQuestLog()
			#self.cell.initTasksTable()
			#self.cell.requestCompletedQuest()  # 注释掉，放到资源加载中请求( by hyw -- 2008.06.10 )


#	def requestQuestLog( self ):				# 注释掉，改为服务器分包定期发送( by hyw -- 2008.06.09 )
#		"""
#		获取一条任务日志
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
		进入一个新的地图（包括位面）
		"""
		BigWorld.callback( 1.0, self.cell.onEnterSpaceAutoNextQuest )
		
	# ---------------------------------->
	# 已声明的方法
	# ---------------------------------->
	def onQuestLogAdd( self, questID, canShare, completeRuleType, tasks, level, reward ):
		"""
		Define method.
		@param      questID: 任务ID
		@type       questID: UINT32
		@param	   canShare: 是否允许共享
		@type      canShare: INT8
		@param	   completeRuleType: 完成规则
		@param	   completeRuleType: INT8
		@param        tasks: 任务目标实例
		@type         tasks: QUESTDATA
		@param msgObjective: 任务目标描述
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
			if e.getType() == csdefine.QUEST_OBJECTIVE_SKILL_LEARNED:	# 学习技能目标任务
				if isMainQuest( questID ) and questID not in self.learnSkillQuestIDList:
					self.learnSkillQuestIDList.append( questID )

		if questID not in self.currentDoingQuestIDList:
			self.currentDoingQuestIDList.append( questID )
		# 更新周围NPC的显示状态
		self.refurbishAroundQuestStatus()
		# 通知新手指引管理器，添加了一个任务
		ECenter.fireEvent("EVT_ON_ADD_QUEST_SIGN",questID )
		
		rds.opIndicator.onPlayerAddedQuest( questID )

	def onShowQuestLog( self, questID ) :
		"""
		Define method.
		@param      questID: 任务ID
		@type       questID: UINT32
		打开任务日志界面，并定位到指定的任务
		"""
		#if not GUIFacade.hasQuestLog( questID ): return		# 不管有没有该任务，都打开任务日志界面
		GUIFacade.setQuestLogSelect( questID )
		ECenter.fireEvent( "EVT_ON_SHOW_QUEST_WINDOW" )
		ECenter.fireEvent( "EVT_ON_PLAY_QUEST_EFFECT", questID )

#	def onQuestIDListReceive( self, questIDList ):
#		"""
#		注释掉，改为服务器分包定期发送( hyw -- 2008.06.09 )
#		Define method
#		@param      questID: 任务ID
#		@type       questID: UINT32
#		"""
#		self.questIDList = questIDList
#		if len( self.questIDList ) != 0:
#			self.requestQuestLog()

	def onCompletedQuestIDListReceive( self, questIDList ):
		"""
		Define method
		@param      questID: 任务ID
		@type       questID: UINT32
		"""
		self.completedQuestIDList = questIDList

	def onQuestLogRemove( self, questID, isAbandon ):
		"""
		Define method.
		@param   questID: 任务ID
		@type    questID: UINT32
		@param isAbandon: 是否玩家放弃的
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
			# 通知新手指引管理器
			rds.opIndicator.onPlayerRemovedQuest( questID )
			# 移除学习技能目标任务
			if questID in self.learnSkillQuestIDList:
				self.learnSkillQuestIDList.remove( questID )

		# 更新周围NPC的显示状态
		self.refurbishAroundQuestStatus()
		ECenter.fireEvent("EVT_ON_REMOVE_QUEST_SIGN",questID )

	def onTaskStateUpdate( self, questID, taskState ):
		"""
		Define method.
		@param   questID: 任务ID
		@type    questID: UINT32
		@param taskIndex: 任务目标在任务中的索引(位置)
		@type  taskIndex: UINT8
		@param taskState: 任务目标
		@type  taskState: QUEST_TASK
		注释：
		更新任务目标状态，扩展了任务状态的导致的NPC更新。 两种情况（ 完成-> 未完成 ） （ 未完成->完成 ）
		"""
		update = GUIFacade.getQuestLogs()[questID]["tasks"]._tasks[taskState.index].isCompleted()

		GUIFacade.onTaskStateUpdate( questID, taskState.index, taskState )
		if  update  != taskState.isCompleted():
			self.refurbishAroundQuestStatus()
			ECenter.fireEvent("EVT_ON_REMOVE_QUEST_SIGN",questID )
		if update :
			rds.helper.courseHelper.roleOperate( "jieshourenwu_caozuo" )		# 触发第一次完成任务过程帮助 hyw( 2009.06.13 )
		rds.areaEffectMgr.startSpaceEffect( self )  # 任务状态改变触发场景光效
		rds.opIndicator.onPlayerQuestStateChanged( questID, taskState.index )

	def onSetGossipText( self, gossipText ):
		"""
		Define method.
		@param 		player: ROLE 实例
		@type 		 player: OBJECT_ID
		@param 		text: 设置任务窗口文本
		@type 		 text: str
		@return: 	None
		"""
		GUIFacade.onSetGossipText( gossipText )

	def onAddGossipOption( self, talkID, title, type ):
		"""
		任务系统普通对话
		Define method.
		@param 		player: ROLE 实例
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
		任务系统任务对话
		Define method.
		@param 		player: ROLE 实例
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
		@param 		 player: ROLE 实例
		@type 		 player: OBJECT_ID
		@return: None
		"""
		GUIFacade.onGossipComplete( targetID )
		rds.opIndicator.onPlayerTalkToNPC( targetID )
		if self.gossipVoices > 0:						#有对话语音
			return
		self.playNPCVoice( targetID )							#播放默认语音

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
		csdefine.QUEST_STATE_NOT_HAVE:		# 还没有接该任务
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
		csdefine.QUEST_STATE_NOT_FINISH:	# 还没有完成目标
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
		csdefine.QUEST_STATE_FINISH:		# 已完成目标,但没交任务
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
		@param	rewards: 任务奖励
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
		@param player: ROLE 实例
		@type  player: OBJECT_ID
		@return: None
		"""
		targetEntity = self.targetEntity
		GUIFacade.onEndGossip( targetEntity )
		self.gossipVoices = 0


	def onQuestBoxStateUpdate( self ):
		"""
		Define method.
		@param questBoxID: 任务箱子的ID
		@type  questBoxID: OBJECT_ID
		@param state: 任务箱子的ID
		@type  state: OBJECT_ID
		"""
		for key, entity in BigWorld.entities.items():
			if hasattr( entity, "refurbishTaskStatus" ):
				entity.refurbishTaskStatus()

	def addGroupRewardsInfo( self, questID, rewards ):
		"""
		Define method.
		@param rewards: 任务奖励列表
		@type  rewards: array of string
		"""
		ECenter.fireEvent("EVT_QUEST_SHOW_GROUP_REWARDS_DETAIL", questID, rewards)

	def onQuestObjectiveDetail( self, questID, objectiveDetail ):
		"""
		Define method.
		服务器向client发送的任务目标信息。
		@type	questID: INT32
		@param	objectiveDetail: 任务目标信息
		@type   objectiveDetail:  string
		"""
		GUIFacade.onObjectiveDetail( self, questID, cPickle.loads( objectiveDetail ) )

	def onQuestSubmitBlank( self, questID, submitInfo ):
		"""
		Define method.
		服务器向client发送的提交任务目标信息。
		@type	questID: INT32
		@param	submitInfo: 任务目标信息
		@type   submitInfo:  string
		"""
		GUIFacade.onSubmitBlank( self, questID, cPickle.loads( submitInfo ) )

	def onTeamMemberChange( self ):
		"""
		队伍数据有变化，更新服务器队伍任务数据信息
		"""
		for questID in GUIFacade.getQuestLogs():
			if GUIFacade.hasQuestTaskType( questID, csdefine.QUEST_OBJECTIVE_TEAM ):
				self.onQuestTeamMemberChange( questID )


	def onQuestTeamMemberChange( self, questID ):
		"""
		更新服务器队伍任务数据信息
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
		是否正在进行某学习技能目标任务
		"""
		return questID in self.learnSkillQuestIDList

	def isLearnSkillQuestCompleted( self ):
		"""
		是否有学习技能目标任务完成
		"""
		for questID in self.learnSkillQuestIDList:
			if GUIFacade.questIsCompleted( questID ):
				return True
		return False

	def dartTongInvite( self, questID, questEntityID ):
		"""
		define method.
		邀请帮会玩家参与帮会运镖任务
		当玩家接受邀请后不再会服务器,直接在client做处理了
		@param entityid
		@type  entityid
		"""
		#提示帮主邀请你参与帮会运镖任务
		GUIFacade.onAskFamilyDart( questID, questEntityID )


	def showTrainGem( self ):
		"""
		"""
		pass
		#ECenter.fireEvent("EVT_ON_EXP_GEM_SHOW")

	def isQuestMonster( self, monster ):
		"""
		判断给定的 monster 是否是任务护送 NPC
		"""
		if monster is None : return False
		if monster.__class__.__name__ != "ConvoyMonster"  : return False
		if monster.ownerID != self.id : return False
		return True

	def isDarting( self, player ):
		"""
		玩家是否有运镖任务在身
		"""
		for qID in GUIFacade.getQuestLogs():
			if GUIFacade.getQuestType( qID ) == csdefine.QUEST_TYPE_DART or GUIFacade.getQuestType( qID ) == csdefine.QUEST_TYPE_MEMBER_DART:
				return True
		return False

	def isRobbing( self, player ):
		"""
		玩家是否有劫镖任务在身
		"""
		for qID in GUIFacade.getQuestLogs():
			if GUIFacade.getQuestType( qID ) == csdefine.QUEST_TYPE_ROB:
				return True
		return False

	def openMoneyToYinpiaoWindow( self ):
		"""
		define method
		银票冲值窗口
		"""
		pass

	def playIntonateBar( self, lastTime ):
		"""
		define method.
		播放一个类似于吟唱条一样的进度条，是由服务器触发
		"""
		GUIFacade.onSkillIntonate( lastTime )

	def readRandomQuestRecord( self, questID ):
		"""
		服务器通知客户端是否要读取环任务
		"""
		ECenter.fireEvent("EVT_ON_LOOP_GROUP_READ_RECORD", questID )

	def acceptQuestConfirm( self, questID, msgStr ):
		"""
		define method.
		服务器通知客户端是否要接取某个任务
		questID：任务ID
		msgStr：对话框中的内容，例如“是否要还XX钱重新接取环任务?”
		"""
		ECenter.fireEvent("EVT_ON_ACCEPT_QUEST_CONFIRM", questID, msgStr )


	def showQuestMsg( self, questMsg ):
		"""
		define method
		显示任务情节。
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_SCENARIO_TIPS", questMsg )
	
	def resetsSoundPriority( self ):
		"""
		重置对话优先级
		"""
		self.soundPriority = csdefine.GOSSIP_PLAY_VOICE_PRIORITY_DEFAULT

	def playNPCVoice( self, targetID ):
		"""
		播放NPC默认语音
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
		接收悬赏任务奖励数据
		"""
		GUIFacade.receiveRewardQuestDatas( canAcceptRewardQuestRecord, acceptedRewardQuestList, completedRewardQuestRecord, remainRefreshTime, degree )
		ECenter.fireEvent( "EVT_ON_REWARD_QUESTS_UPDATE" )
		
	def rewardQuestAccept( self, questID ):
		"""
		接受悬赏任务
		"""
		self.cell.rewardQuestAccept( questID )
		pass
		
	def sendRewardQuestState( self, questID, state, degree ):
		"""
		更新悬赏任务数据
		"""
		GUIFacade.updateRewardQuestState( questID, state, degree )
		ECenter.fireEvent("EVT_ON_QUEST_STATE_CHANGED", questID, state )
		
	def useItemRefreshRewardQuest( self ):
		"""
		用物品刷新悬赏任务
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

		# "已领取有悬赏任务，是否继续？"
		msg = mbmsgs[0x10ae]
		showAutoHideMessage( 5, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def triggerQuestRewardSlots( self, questID, rewardIndex, codeStr, questTargetID ):
		"""
		触发老虎机
		"""
		ECenter.fireEvent( "EVT_ON_SLOT_MACHINE_SHOW", questID, rewardIndex, codeStr, questTargetID )
	
	def getQuestRewardSlots( self, questID, rewardIndex, codeStr, questTargetID, useGold ):
		"""
		随机取任务奖励倍数（老虎机）
		"""
		self.cell.getQuestRewardSlots( questID, rewardIndex, codeStr, questTargetID, useGold )
	
	def setQuestRewardSlots( self, questID, multiple ):
		"""
		define method.
		设置任务奖励倍数（老虎机）
		"""
		ECenter.fireEvent( "EVT_ON_SLOT_MACHINE_RECEIVE_MULTIPLE", multiple )

	def getTaskIndexMonsters( self ):
		"""
		获取需要显示名称的任务怪物列表（当前玩家任务列表所有的）
		"""
		taskIndexMonsters = []
		for questID in GUIFacade.getQuestLogs().keys():
			qData = g_questDataInst.get( questID )
			taskIndexs = qData.getTaskIndexs()
			for taskIndex in taskIndexs:
				snMonsters = []
				if not GUIFacade.isTaskCompleted( questID, taskIndex ):	# 任务目标未完成
					snMonsters = qData.getTaskIndexMonsters( taskIndex )
				taskIndexMonsters.extend( snMonsters )
		taskIndexMonsters = list( set( taskIndexMonsters ) )
		return taskIndexMonsters

# RoleQuestInterface.py


