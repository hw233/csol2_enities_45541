# -*- coding: gb18030 -*-
#
# $Id: QuestFixedLoop.py,v 1.7 2008-08-07 08:56:36 zhangyuxing Exp $


"""
"""

from bwdebug import *
from Quest import Quest
import csdefine


class QuestCompleteFixCount( Quest ):
	"""
	每天只能完成指定次数的任务
	"""
	def __init__( self ):
		Quest.__init__( self )
		self.repeatable_ = 1	# 此类型的任务强制任务能重复接，否则就没有意义了
		self._finish_count = 1	# 每天最多能接几次，默认为1次
		self._style = csdefine.QUEST_STYLE_FIXED_LOOP	#任务样式


	def init( self, section ):
		"""
		virtual method.
		@param section: 任务配置文件section
		@type  section: pyDataSection
		"""
		Quest.init( self, section )
		self.repeatable_ = 1	# 此类型的任务强制任务能重复接，否则就没有意义了
		self._finish_count = section.readInt( "repeat_upper_limit" )

	def checkRequirement( self, player ):
		"""
		virtual method.
		判断玩家的条件是否足够接当前任务。
		@return: 如果达不到接任务的要求则返回False。
		@rtype:  BOOL
		"""
		lpLog = player.getLoopQuestLog( self.getID(), True )
		if not lpLog.checkStartTime():
			# 接任务日期与当前时间不是同一天，也就表示需要重置任务状态
			lpLog.reset()
		if lpLog.getDegree() >= self._finish_count:
			# 已完成任务次数过多，不可以再接
			return False
		return Quest.checkRequirement( self, player )


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
		return False

