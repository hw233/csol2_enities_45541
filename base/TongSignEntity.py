# -*- coding: gb18030 -*-

"""
帮会会标管理器，负责帮会会标的存取、更新等功能 by 姜毅 8:52 2010-1-13
"""

import BigWorld
from bwdebug import *
from Love3 import g_tongSignMgr
import Const

class TongSignEntity( BigWorld.Base ):
	"""
	帮会会标管理器entity
	"""
	_instance = None
	def __init__( self ):
		assert TongSignEntity._instance is None		# 不允许有两个以上的实例
		BigWorld.Base.__init__( self )
		self._tongSignSenderTimer = 0
		self.beginTongSignSender()
		INFO_MSG( "TongSignEntity create." )
		
	def beginTongSignSender( self ):
		"""
		启动帮会会标发动计时
		"""
		self._tongSignSenderTimer = self.addTimer( Const.SEND_TONG_SIGN_TIME_TICK, Const.SEND_TONG_SIGN_TIME_TICK, 0 )
	
	def onSendTongSignStr( self ):
		"""
		帮会entity给玩家（不一定是帮会成员）发送会标图标string
		"""
		g_tongSignMgr.onSend()
		self.delTimer( self._tongSignSenderTimer )
		self._tongSignSenderTimer = 0
		self.beginTongSignSender()
		
	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		if self._tongSignSenderTimer == timerID:
			self.onSendTongSignStr()