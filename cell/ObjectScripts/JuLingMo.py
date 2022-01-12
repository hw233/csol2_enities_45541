# -*- coding: gb18030 -*-
#
# JuLingMo类 2009-05-25 SongPeifang
#

from WXMonster import WXMonster
import cschannel_msgs
import ShareTexts as ST


class JuLingMo( WXMonster ):
	"""
	巨灵魔脚本
	"""
	def __init__( self ):
		"""
		"""
		WXMonster.__init__( self )
		self.bornNPC = False
		self.callMonsterID		= "20712013"
		self.callMonsterCount = 8
		self.dieSay				= cschannel_msgs.NIU_MO_WANG_VOICE_10
		self.dieNotifyText		= cschannel_msgs.BCT_FYJLM_JULINGMO_DIE
		self.dieDelKey			= "JuLingMoAlive"