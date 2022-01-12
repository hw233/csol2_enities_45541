# -*- coding: gb18030 -*-
#
# $Id $

"""
劫镖任务模块 spf
"""

from bwdebug import *
from Quest import *
from QuestDataType import QuestDataType
from QuestRandomRecordType import QuestRandomRecordType
from string import Template
from QuestFixedLoop import QuestFixedLoop
import QTReward
import QTTask
import time
import random
import csdefine
import csstatus
import csconst
import ECBExtend


class QuestRob( QuestFixedLoop ):
	def __init__( self ):
		QuestFixedLoop.__init__( self )
		self._finish_count = 1 #默认为1

	def init( self, section ):
		"""
		"""
		QuestFixedLoop.init( self, section )
		self._type = csdefine.QUEST_TYPE_ROB
		self._finish_count = section.readInt( "repeat_upper_limit" )

	def getFaction( self, player, tasks = None ):
		"""
		获得此任务镖局的势力
		"""
		factionID = -1
		if tasks is None:
			tasks = self.newTasks_( player )
		if tasks is None:
			ERROR_MSG( "Faction id should be set into tasks!" )
			return -1
		for task in tasks._tasks.itervalues():
			if task.getType() == csdefine.QUEST_OBJECTIVE_DART_KILL:
				factionID = int( task.str1 )
		if factionID == -1 or factionID == None:
			ERROR_MSG( "Faction id has not been initiate!" )
		if factionID == csconst.FACTION_CP:
			factionID = csconst.FACTION_XL
		elif factionID == csconst.FACTION_XL:
			factionID = csconst.FACTION_CP
		return factionID

	def onAccept( self, player, tasks ):
		"""
		virtual method.
		执行任务实际处理
		"""

		lpLog = player.getLoopQuestLog( self._id, True )
		if lpLog:
			lpLog.incrDegree()
		Quest.onAccept( self, player, tasks )

	def abandoned( self, player, flags ):
		"""
		virtual method.
		劫镖任务只能镖局首领那里放弃
		@param player: instance of Role Entity
		@type  player: Entity
		@return: None
		"""
		#为了便于测试先注释掉
		if  flags != csdefine.QUEST_REMOVE_FLAG_NPC_CHOOSE:
			player.statusMessage( csstatus.ROLE_QUEST_ROB_ABANDONED_FAILED )
			return False
		player.statusMessage( csstatus.ROLE_QUEST_ROB_ABANDONED )
		tasks = self.newTasks_( player )
		factionID = self.getFaction( player, tasks )
		player.client.updateTitlesDartRob( factionID )
		return QuestFixedLoop.abandoned( self, player, flags )

	def onRemoved( self, player ):
		"""
		任务移去时通知玩家去掉头顶标记
		"""
		#player.removeFlag( csdefine.ROLE_FLAG_ROBBING )

		if player.hasFlag( csdefine.ROLE_FLAG_CP_ROBBING ):
			player.removeFlag( csdefine.ROLE_FLAG_CP_ROBBING )
		else:
			player.removeFlag( csdefine.ROLE_FLAG_XL_ROBBING )

		player.cancel( player.queryTemp( "robDart_timerID", 0 ) )
		player.removeTemp( "robDart_timerID" )
		player.remove( "RobEndTime" )


	def query( self, player ):
		"""
		查询玩家对某一个任务的进行状态。
		这里专门对劫镖任务单独处理，因为劫镖任务和其他任务不一样
		策划要求劫镖任务狙杀镖车后，即时规定时间内不交任务，也算完成
		@return: 返回值类型请查看common里的QUEST_STATE_*
		@rtype:  UINT8
		"""
		questID = self.getID()
		if player.questIsCompleted( questID ):
			return csdefine.QUEST_STATE_COMPLETE						# 已做过该任务
		if player.has_quest( questID ):
			# 已接了该任务
			if player.questTaskIsCompleted( questID ):
				return csdefine.QUEST_STATE_FINISH						# 任务目标已完成
			elif self.isCompleted( player ):
				return csdefine.QUEST_STATE_FINISH
			else:
				return csdefine.QUEST_STATE_NOT_FINISH					# 任务目标未完成
		else:
			# 没有接该任务
			if self.checkRequirement( player ):
				return csdefine.QUEST_STATE_NOT_HAVE					# 可以接但还未接该任务
			else:
				return csdefine.QUEST_STATE_NOT_ALLOW					# 不够条件接该任务

	def sendQuestLog( self, player, questLog ):
		"""
		"""
		QuestFixedLoop.sendQuestLog( self, player, questLog )
		self.addPlayerRobFlag( player )

	def addPlayerRobFlag( self, player ):
		"""
		"""
		factionID = self.getFaction( player )
		player.client.updateTitlesDartRob( factionID )
		if not self.isFailed( player ):
			if factionID == csconst.FACTION_CP:
				player.addFlag( csdefine.ROLE_FLAG_CP_ROBBING )
			else:
				player.addFlag( csdefine.ROLE_FLAG_XL_ROBBING )
		t = player.query("RobEndTime", 0) - time.time()
		
		# 由于玩家上线的时候可能劫镖的时间已经过去了，但是劫镖的flag还在玩家身上, 所以删除标志的定时器无论什么时候都要起作用
		if t < 1:
			t = 1
			
		player.setTemp( "robDart_timerID", player.addTimer( t, 0, ECBExtend.REMOVE_ROB_FLAG ) )

	def isCompleted( self, player ):
		"""
		是否完成劫镖任务,根据策划的要求，只要在规定时间内狙杀了镖车就算完成
		狙杀镖车后即时规定时间内不交任务，也不能算失败
		"""
		for t in self.tasks_.itervalues():
			if t.getType() == csdefine.QUEST_OBJECTIVE_DART_KILL:
				index = t.index
				return player.questsTable[self.getID()]._tasks[index].isCompleted( player )
		return False

	def isFailed( self, player ):
		"""
		劫镖任务是否已经失败
		"""
		failed = False
		for t in self.tasks_.itervalues():
			if t.getType() == csdefine.QUEST_OBJECTIVE_DART_KILL:
				# 没有失败
				if player.questsTable[self.getID()]._tasks[t.index].isCompleted( player ):
					return False
			elif t.getType() == csdefine.QUEST_OBJECTIVE_TIME:
				failed = not player.questsTable[self.getID()]._tasks[t.index].isCompleted( player )
		return failed