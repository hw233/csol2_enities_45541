# -*- coding: gb18030 -*-
#
# JishiMonster类 2009-10-08 SongPeifang
#

from WXMonster import WXMonster
import cschannel_msgs
import ShareTexts as ST


class JishiMonster( WXMonster ):
	"""
	疯狂祭师脚本
	"""
	def __init__( self ):
		"""
		"""
		WXMonster.__init__( self )
		self.bornNPC = False
		self.callMonsterID		= "20212004"
		self.callMonsterCount = 8
		self.dieSay				= cschannel_msgs.NIU_MO_WANG_VOICE_10
		self.dieNotifyText		= cschannel_msgs.BCT_PHFKJS_DIE
		self.dieDelKey			= "CrazyJiShiAlive"