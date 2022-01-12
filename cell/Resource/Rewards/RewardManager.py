# -*- coding: gb18030 -*-


#游戏内容奖励管理

import csdefine
from Reward_TeamCompetition import g_TCRExp
from Reward_TeamCompetition import g_TCRItems
from Reward_RaceHorse import g_RH
from Reward_RaceHorse import g_RH_Items
from Reward_RabbitRun import g_RR


g_rewards = {
	csdefine.REWARD_TEAMCOMPETITION_EXP 	: g_TCRExp,
	csdefine.REWARD_TEAMCOMPETITION_ITEMS	: g_TCRItems,
	csdefine.REWARD_RACE_HORSE				: g_RH,
	csdefine.REWARD_RACE_HORSE_ITEMS		: g_RH_Items,
	csdefine.REWARD_RABBIT_RUN				: g_RR,
	}

class RewardManager:
	"""
	"""
	def __init__( self ):
		"""
		"""
		pass
	
	
	def rewards( self, playerEntity, rewardType ):
		"""
		"""
		return g_rewards[rewardType].do( playerEntity )


g_rewardMgr = RewardManager()