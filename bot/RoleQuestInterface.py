# -*- coding: utf-8 -*-
from AutoQuestModule import AutoTask
class QuestLog( object ):
	def __init__( self, id, tasks ):
		self.questID = id
		self.tasks = tasks
		
		
class RoleQuestInterface:
	def __init__( self ):
		self.quest_current = None
		self.quest_current_taskIndex = 0
		self.quest_task_handle = None
		self.autoQuestFightTimerID = 0
		self.quests = {}
	
	def onQuestLogAdd( self, questID, canShare, quest, title, level, msgObjective, msgDetail, reward ):
		"""
		Define method.
		@param      questID: 任务ID
		@type       questID: UINT32
		@param	   canShare: 是否允许共享
		@type      canShare: INT8
		@param        tasks: 任务目标实例
		@type         tasks: QUESTDATA
		@param msgObjective: 任务目标描述
		@type  msgObjective: STRING
		"""
		self.quests[ questID ] = quest
		self.autoQuest( quest )
		
	def questAccept( self, questID ):
		# 接爱任务
		self.cell.questAcceptForce( questID, 0 )
	
	def onTaskStateUpdate( self, questID, taskState ):
		# 更新任务目标
		self.quest_current.copyFrom( taskState )
		if self.quest_current._tasks[taskState.index].isCompleted():
			self.quest_task_handle.stop()
			self.quest_task_handle = None
		
		self.autoQuest( self.quest_current )
		
	def autoQuest( self, quest ):
		# 自动做任务
		if quest.isCompleted():
			self.cell.questSingleReward( questID )
		else:
			nextDoTask = None
			nextDoTaskIndex = 0
			for task in quest.getTasks():
				if not task.isCompleted( self ):
					nextDoTask = task
					nextDoTaskIndex = task.getIndex()
					break

			self.quest_current = quest
			self.quest_current_taskIndex = nextDoTaskIndex
			self.quest_task_handle = AutoTask.getHandle( nextDoTask )
			self.quest_task_handle.do( self, nextDoTask )
	
	def autoQuestFight( self ):
		self.autoQuestFightTimerID = self.addTimer(1, self.autoFightLoop, True)
	
	def stopQuestFight( self ):
		self.delTimer(self.autoQuestFightTimerID)