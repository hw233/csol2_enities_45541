# -*- coding: gb18030 -*-
#
# 帮会跑商任务
#

"""
"""

from bwdebug import *
from QuestFixedLoop import QuestFixedLoop
import csdefine

MERCHANT_TITLE	= 23		#跑商称号

class QuestMerchant( QuestFixedLoop ):
	"""
	帮会跑商任务
	"""
	def __init__( self ):
		QuestFixedLoop.__init__( self )
		self._type =  csdefine.QUEST_TYPE_RUN_MERCHANT

	def accept( self, player ):
		"""
		virtual method.
		接任务，如果接任务失败了则返回False（例如玩家背包满了放不下任务道具）。

		@param     player: instance of Role Entity
		@type      player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		
		tongMB = player.tong_getSelfTongEntity()
		# 获得玩家已完成任务次数
		lpLog = player.getLoopQuestLog( self.getID(), True )
		count = lpLog.getDegree()

		tongMB.queryMerchantCount( player.base, self.getID(), count )

	def onRemoved( self, player ):
		"""
		"""
		player.removeMerchantQuestFlag()
		#player.removeTitle( MERCHANT_TITLE )

	def checkRequirement( self, player ):
		"""
		virtual method.
		判断玩家的条件是否足够接当前任务。
		@return: 如果达不到接任务的要求则返回False。
		@rtype:  BOOL
		"""
		return QuestFixedLoop.checkRequirement( self, player ) and not player.isInMerchantQuest()

	def sendQuestLog( self, player, questLog ):
		"""
		"""
		player.showMerchantQuestFlag()
		QuestFixedLoop.sendQuestLog( self, player, questLog )
	

