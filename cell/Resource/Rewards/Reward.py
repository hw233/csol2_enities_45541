# -*- coding: gb18030 -*-

import Language
import csdefine
import RewardManager


g_configPaths = { 
	csdefine.REWARD_TEAMCOMPETITION_EXP		:"res/config/server/rewards/Reward_TeamCompetition_Exp.xml",
	csdefine.REWARD_TEAMCOMPETITION_ITEMS	:"res/config/server/rewards/Reward_TeamCompetition_Items.xml",
	csdefine.REWARD_RACE_HORSE		:"",
	csdefine.REWARD_RACE_HORSE_ITEMS		:"",
	}

class Reward:
	"""
	"""
	type = csdefine.REWARD_NONE
	def __init__( self ):
		"""
		"""
		self.section = None
		self.init()
	
	
	def init( self ):
		"""
		"""
		
		self.section = Language.openConfigSection( g_configPaths[self.type] )
	
	
	def do( self, playerEntity ):
		"""
		"""
		pass
		
		
