# -*- coding: gb18030 -*-
#


from bwdebug import *
from Quest import Quest
import BigWorld
import csdefine
import csconst

class QuestCampDaily( Quest ):
	"""
	此类任务每天只能完成一定的个数，用于阵营日常任务
	"""
	def __init__( self ):
		Quest.__init__( self )
		self.repeatable_ = True
		self._type = csdefine.QUEST_TYPE_CAMP_DAILY

	def checkRequirement( self, player ):
		"""
		virtual method.
		判断玩家的条件是否足够接当前任务。
		@return: 如果达不到接任务的要求则返回False。
		@rtype:  BOOL
		"""
		# 在当次阵营活动时间内，只能完成一次本任务
		activityTimeRecord = player.query( "CampDailyTimeRecord_%s" % self.getID(), None )
		if activityTimeRecord:
			if BigWorld.globalData.has_key( "CampActivityEndTime" ) and BigWorld.globalData["CampActivityEndTime"] == activityTimeRecord:
				return False
			else:
				player.remove( "CampDailyTimeRecord_%s" % self.getID() )
				
		# 同类任务一天只能完成固定个数
		count = len( player.findQuestByType( csdefine.QUEST_TYPE_CAMP_DAILY ) )
		for i in player.loopQuestLogs:
			quest = player.getQuest( i.getQuestID() )
			if i.checkStartTime() and quest.getType() == csdefine.QUEST_TYPE_CAMP_DAILY:
				count += i.getDegree()
		if count >= csconst.CAMP_DAILY_REPEAT_LIMIT:
			return False
		
		for requirement in self.requirements_:
			if requirement.__class__.__name__ == "QTRCampActivityCondition":		# 这种类型的条件不做判定,发布任务的NPC脚本有特殊处理:CampLocationQuestNPC
				continue
			if not requirement.query( player ):
				return False
		return True
		
	def onAccept( self, player, tasks ):
		"""
		"""
		buff = player.findBuffsByBuffID( 22133 )
		if len( buff ) <= 0:
			player.systemCastSpell( csconst.CAMP_ACTIVITY_CHECK_SPELL_ID )			# 添加一个监测阵营活动开启情况的buff：Buff_22133
		Quest.onAccept( self, player, tasks )
		
	def complete( self, player, rewardIndex, codeStr = "" ):
		"""
		virtual method.
		交任务。

		@param player: instance of Role Entity
		@type  player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if Quest.complete( self, player, rewardIndex, codeStr ):
			lpLog = player.getLoopQuestLog( self.getID(), True )
			if not lpLog.checkStartTime():
				# 接任务日期与当前时间不是同一天，也就表示需要重置任务状态
				lpLog.reset()
			lpLog.incrDegree()
			if BigWorld.globalData.has_key( "CampActivityEndTime" ):
				player.set( "CampDailyTimeRecord_%s" % self.getID(), BigWorld.globalData["CampActivityEndTime"] )			# 记录阵营活动结束时间
			return True
		return False
