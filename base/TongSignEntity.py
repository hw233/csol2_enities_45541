# -*- coding: gb18030 -*-

"""
��������������������Ĵ�ȡ�����µȹ��� by ���� 8:52 2010-1-13
"""

import BigWorld
from bwdebug import *
from Love3 import g_tongSignMgr
import Const

class TongSignEntity( BigWorld.Base ):
	"""
	����������entity
	"""
	_instance = None
	def __init__( self ):
		assert TongSignEntity._instance is None		# ���������������ϵ�ʵ��
		BigWorld.Base.__init__( self )
		self._tongSignSenderTimer = 0
		self.beginTongSignSender()
		INFO_MSG( "TongSignEntity create." )
		
	def beginTongSignSender( self ):
		"""
		��������귢����ʱ
		"""
		self._tongSignSenderTimer = self.addTimer( Const.SEND_TONG_SIGN_TIME_TICK, Const.SEND_TONG_SIGN_TIME_TICK, 0 )
	
	def onSendTongSignStr( self ):
		"""
		���entity����ң���һ���ǰ���Ա�����ͻ��ͼ��string
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