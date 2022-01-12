# -*- coding: gb18030 -*-
#

"""
"""
from Function import Function
import BigWorld
import csdefine
import time
import Language
import csstatus
from Resource.Rewards.RewardManager import g_rewardMgr

class FuncTeamCompetitionReward( Function ):
	"""
	领取组队竞赛奖励
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		
		player.endGossip( talkEntity )
		
		if not g_rewardMgr.rewards( player, csdefine.REWARD_TEAMCOMPETITION_ITEMS ):
			player.client.onStatusMessage( csstatus.KITBAG_IS_FULL, "" )
			return
		#player.addItem( player.createDynamicItem( self._itemID ) )
		player.setRoleRecord( "teamCompetitionWiner", "0" )
		

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用
		@return: True/False
		@rtype:	bool
		"""
		return False

