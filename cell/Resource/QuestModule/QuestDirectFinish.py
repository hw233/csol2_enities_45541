# -*- coding: gb18030 -*-
#
# $Id: QuestDirectFinish.py,v 1.8 2008-08-14 06:14:09 zhangyuxing Exp $


"""
"""

import csdefine
import csstatus
from bwdebug import *
from Quest import Quest

class QuestDirectFinish( Quest ):
	"""
	一个不需要接的任务模块,该任务在显示时显示的仍然是未接该任务,
	但只要达到交任务条件（且达到了接任务的条件）,
	点该任务时出现的是交任务的界面,而非接任务界面；

	此模块主要用于一些拿物品换物品的任务（如：拿泉水换食物）
	"""
	def __init__( self ):
		Quest.__init__( self )
		self._style = csdefine.QUEST_STYLE_DIRECT_FINISH	# 任务样式

	def init( self, section ):
		"""
		virtual method.
		@param section: 任务配置文件section
		@type  section: pyDataSection
		"""
		Quest.init( self, section )

	def _query_tasks( self, player ):
		"""
		查询玩家是否达成交任务的任务目标。
		@return: 返回值类型请查看common里的QUEST_STATE_*
		@rtype:  UINT8
		"""

		for i in self.tasks_:
			if not self.tasks_[i].isCompletedForNoStart( player ):
				return csdefine.QUEST_STATE_NOT_FINISH		# 任务目标未完成
		return csdefine.QUEST_STATE_FINISH					# 任务目标已完成


	def _get_tasksDetail( self, player ):
		"""
		"""
		return [ task.getDetail( player ) for task in self.tasks_.itervalues() ]


	def _complete_tasks( self, player ):
		"""
		"""
		for i in self.tasks_:
			self.tasks_[i].complete( player )


	def gossipDetail( self, playerEntity, issuer = None ):
		"""
		"""
		state = self._query_tasks( playerEntity )
		if state == csdefine.QUEST_STATE_NOT_FINISH:	# 任务目标未完成
			playerEntity.sendQuestRewards( self._id, self.getRewardsDetail( playerEntity ) )
			playerEntity.sendObjectiveDetail( self._id, self._get_tasksDetail( playerEntity ) )
			self.gossipIncomplete( playerEntity, issuer )
		elif state == csdefine.QUEST_STATE_FINISH:		# 任务目标已完成
			self.gossipPrecomplete( playerEntity, issuer )
		else:
			assert "UNKNOWN ERROR!!!"


	def gossipPrecomplete( self, playerEntity, issuer ):
		"""
		任务目标已完成对白
		"""
		if issuer:	targetID = issuer.id
		else:		targetID = 0
		playerEntity.sendQuestRewards( self._id, self.getRewardsDetail( playerEntity ) )
		playerEntity.sendObjectiveDetail( self._id, self._get_tasksDetail( playerEntity ) )

		playerEntity.sendQuestSubmitBlank( self._id, self.getSubmitDetail( playerEntity ) )
		if len( self._msg_precomplete ):
			msg = self._msg_precomplete
		else:
			msg = self._msg_log_detail
		playerEntity.sendQuestPrecomplete( self._id, self._title, self._level, msg, targetID )


	def query( self, playerEntity ):
		"""
		"""
		tempState = Quest.query( self, playerEntity)

		if tempState == csdefine.QUEST_STATE_COMPLETE:
			return csdefine.QUEST_STATE_COMPLETE

		elif tempState == csdefine.QUEST_STATE_NOT_ALLOW:
			return csdefine.QUEST_STATE_NOT_ALLOW

		else:
			return csdefine.QUEST_STATE_DIRECT_FINISH


	def complete( self, player, rewardIndex, codeStr = "" ):
		"""
		virtual method.
		交任务。

		@param player: instance of Role Entity
		@type  player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		#player.setTemp( "questKitTote", kitTote )
		#player.setTemp( "questOrder", order )
		self.setDecodeTemp( player, codeStr )
		player.setTemp( "questTeam", True)

		if not self.query( player ) == csdefine.QUEST_STATE_DIRECT_FINISH:
			#player.removeTemp( "questKitTote" )
			#player.removeTemp( "questOrder" )
			self.removeDecodeTemp( player , codeStr)
			player.removeTemp( "questTeam" )
			return False

		if not self._isTasksCompleted( player):
			#player.removeTemp( "questKitTote" )
			#player.removeTemp( "questOrder" )
			self.removeDecodeTemp( player, codeStr )
			player.removeTemp( "questTeam" )
			return False

		player.setTemp( "RewardItemChoose" , rewardIndex )
		if not self.reward_( player, rewardIndex ):
			player.removeTemp( "RewardItemChoose" )
			#player.removeTemp( "questKitTote" )
			#player.removeTemp( "questOrder" )
			self.removeDecodeTemp( player, codeStr )
			player.removeTemp( "questTeam" )
			return False
		if not self.repeatable_:				# 只保存不可重复完成的任务
			player.recordQuestLog( self._id )	# 记录任务日志

		# after complete
		for e in self.afterComplete_:
			e.do( player )

		self._complete_tasks( player )
		player.questFinishQuest( self._id )
		player.client.onQuestLogRemove( 0, False ) #仅仅用于通知客户端更新周围NPC

		player.removeTemp( "RewardItemChoose" )
		#player.removeTemp( "questKitTote" )
		#player.removeTemp( "questOrder" )
		self.removeDecodeTemp( player, codeStr )
		player.removeTemp( "questTeam" )
		player.statusMessage( csstatus.ROLE_QUEST_COMPLETE, self._title )

		return True


	def _isTasksCompleted( self, playerEntity ):
		"""
		"""
		tasks = self.newTasks_( playerEntity )
		return tasks.isCompletedForNoStart( playerEntity )



#
# $Log: not supported by cvs2svn $
# Revision 1.7  2008/08/07 08:56:20  zhangyuxing
# 修改任务提交 参数的处理，使用字符串作为任务目标需要内容，又任务目标
# 自行解析。
#
# Revision 1.6  2008/07/31 09:23:49  zhangyuxing
# 修改一处命名错误
#
# Revision 1.5  2008/07/28 01:10:42  zhangyuxing
# 增加任务完成通知
#
# Revision 1.4  2008/01/30 02:50:25  zhangyuxing
# 增加：把直接可交的任务类型做的比较独立， 增加了相应的一些方法
#
# Revision 1.3  2008/01/11 06:50:51  zhangyuxing
# 增加任务样式 self._style
#
# Revision 1.2  2007/12/04 03:04:21  zhangyuxing
# 达成任务目标 tasks_ 数据存储方式由列表改为 字典,所以相应的访问方式也做
# 改变
#
# Revision 1.1  2007/11/02 03:57:27  phw
# no message
#
#