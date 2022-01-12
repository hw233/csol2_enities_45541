# -*- coding: gb18030 -*-
#
# 变身大赛NPC 2009-01-17 SongPeifang
#

import BigWorld
from bwdebug import *
from NPC import NPC

class BCNPC( NPC ):
	"""
	变身大赛NPC
	"""
	def __init__( self ):
		"""
		初始化
		"""
		NPC.__init__( self )
		BigWorld.globalData["BCGameMgr"].registerBCNPC( self.lineNumber, self )
		
	def getLoginMembers( self, memberCount ):
		"""
		Define Method.
		设置报名的人数
		"""
		BigWorld.globalData["BCGameMgr"].setMemberCount( self.lineNumber, memberCount )