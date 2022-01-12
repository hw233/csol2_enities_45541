# -*- coding: gb18030 -*-
#
# XiaotianMonster类 2009-10-08 SongPeifang
#

from WXMonster import WXMonster
import cschannel_msgs
import ShareTexts as ST



class XiaotianMonster( WXMonster ):
	"""
	啸天大将脚本
	"""
	def __init__( self ):
		"""
		"""
		WXMonster.__init__( self )
		self.bornNPC = False
		self.callMonsterID		= "20722011"
		self.callMonsterCount = 8
		self.dieSay				= cschannel_msgs.NIU_MO_WANG_VOICE_10
		self.dieNotifyText		= cschannel_msgs.BCT_JBXTDJ_DIE
		self.dieDelKey			= "XiaoTianDaJiangAlive"