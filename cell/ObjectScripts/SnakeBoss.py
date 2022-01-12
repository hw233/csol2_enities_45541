# -*- coding: gb18030 -*-
#
# SnakeBoss类 2009-05-25 SongPeifang
#

from WXMonster import WXMonster
import cschannel_msgs
import ShareTexts as ST



class SnakeBoss( WXMonster ):
	"""
	白蛇妖脚本
	"""
	def __init__( self ):
		"""
		"""
		WXMonster.__init__( self )
		self.bornNPC = False
		self.callMonsterID		= "20722008"
		self.callMonsterCount = 8
		self.dieSay				= cschannel_msgs.NIU_MO_WANG_VOICE_10
		self.dieNotifyText		= cschannel_msgs.BCT_FYBSY_SNAKE_DIE
		self.dieDelKey			= "SnakeBossAlive"