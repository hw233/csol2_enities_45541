# -*- coding: gb18030 -*-
# 帮会运镖 by 姜毅 12:07 2010-11-8


import BigWorld
from QuestDart import QuestDart
import csstatus
import csdefine

class QuestTongDart( QuestDart ):


	def accept( self, player ):
		"""
		virtual method.
		接任务，如果接任务失败了则返回False（例如玩家背包满了放不下任务道具）。

		@param     player: instance of Role Entity
		@type      player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		QuestDart.accept( self, player )
		"""			CSOL-2118不再限制一天内帮会成员总的接取次数
		tongMB = player.tong_getSelfTongEntity()
		
		if tongMB is None:
			player.statusMessage( csstatus.TONG_DART_NOT_EXIST )
			return
		
		tongMB.queryDartCount( player.base, self.getID() )
		"""

	def onAccept( self, player, tasks ):
		"""
		virtual method.
		执行任务实际处理
		"""
		QuestDart.onAccept( self, player, tasks )
		
		#tongMB = player.tong_getSelfTongEntity()
		
		#tongMB.addDartCount()

	def checkRequirement( self, player ):
		"""
		virtual method.
		判断玩家的条件是否足够接当前任务。
		@return: 如果达不到接任务的要求则返回False。
		@rtype:  BOOL
		"""
		if player.tong_dbID == 0 or not player.tongDartQuestIsOpen:		# 帮主没开运镖就不让接
			return False
		return QuestDart.checkRequirement( self, player )
