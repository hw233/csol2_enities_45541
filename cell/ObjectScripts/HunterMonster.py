# -*- coding: gb18030 -*-
#
# HunterMonster�� 2009-10-08 SongPeifang
#

from WXMonster import WXMonster
import cschannel_msgs
import ShareTexts as ST


class HunterMonster( WXMonster ):
	"""
	�������˽ű�
	"""
	def __init__( self ):
		"""
		"""
		WXMonster.__init__( self )
		self.bornNPC = False
		self.callMonsterID		= "20322023"
		self.callMonsterCount = 8
		self.dieSay				= cschannel_msgs.NIU_MO_WANG_VOICE_10
		self.dieNotifyText		= cschannel_msgs.BCT_DUOLUOLIEREN_DIE
		self.dieDelKey			= "DuoLuoHunterAlive"