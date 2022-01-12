# -*- coding: gb18030 -*-
#

import BigWorld
from Quest import Quest
import csdefine
import csconst

class QuestCampActivity( Quest ):
	"""
	阵营活动任务类型
	"""
	def __init__( self ):
		Quest.__init__( self )
		self.repeatable_ = True
		self._type = csdefine.QUEST_TYPE_CAMP_ACTIVITY
		
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
				
		return Quest.checkRequirement( self, player )
				
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
			if BigWorld.globalData.has_key( "CampActivityEndTime" ):
				player.set( "CampDailyTimeRecord_%s" % self.getID(), BigWorld.globalData["CampActivityEndTime"] )			# 记录阵营活动结束时间
			return True
		return False
		