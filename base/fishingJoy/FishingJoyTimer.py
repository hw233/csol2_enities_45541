# -*- coding:gb18030 -*-

"""
8:58 2013-11-6 by wsf
ͨ������FishingJoyMgrʹ�ò���entity��FishingJoy����Ҳ���Ծ���timer����
"""

from bwdebug import *


class TimerCB:
	def __init__( self, callback, usrArg ):
		self.callback = callback
		self.usrArg = usrArg
		
	def __call__( self ):
		self.callback( usrArg )
		
class FishingJoyTimer:
	def __init__( self ):
		self.fishingJoyMgr = self.getAttachEntity()	# ֻ����������Ӧʵ����addFishingJoyTimer���Ƶ�entity
		
	def addTimer( self, delay, callback ):
		if delay <= 0:
			DEBUG_MSG( "no delay:", callback )
		return self.fishingJoyMgr.addFishingJoyTimer( delay, callback )
		
	def getAttachEntity( self ):
		# virtual method.
		# ��ȡ������entity��Ĭ��ȡ��ǰ�������Ĳ���ȫ�ֹ�����
		return BigWorld.entities[BigWorld.globalData["FishingJoyMgr"].id]
		
	def cancel( self, timerID ):
		self.fishingJoyMgr.cancelFishingJoyTimer( timerID )
		
	def destroy( self ):
		self.fishingJoyMgr = None
		DEBUG_MSG( self.number )
		