# -*- coding: gb18030 -*-
#
# 
#

from bwdebug import *
from NPC import NPC
import random
import csdefine
import BigWorld
import csstatus
import ECBExtend

class ProtectTongNPC( NPC ):
	"""
	保护帮派NPC
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPC.__init__( self )
		self.addTimer( 5.0, 3.0, ECBExtend.HEARTBEAT_TIMER_CBID )

	def onProtectTongOver( self ):
		"""
		define method.
		活动结束了
		"""
		self.destroy()
	
	def onSpaceCopyMonsterDead( self ):
		"""
		define method.
		副本的怪物都死亡了
		"""
		self.destroy()
		
	def onHeartbeat( self, timerID, cbID ):
		"""
		心跳
		"""
		if not BigWorld.globalData.has_key( "AS_ProtectTong" ):
			self.destroy()
		