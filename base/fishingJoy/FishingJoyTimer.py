# -*- coding:gb18030 -*-

"""
8:58 2013-11-6 by wsf
通过依附FishingJoyMgr使得不是entity的FishingJoy对象也可以具有timer功能
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
		self.fishingJoyMgr = self.getAttachEntity()	# 只能依附于相应实现了addFishingJoyTimer机制的entity
		
	def addTimer( self, delay, callback ):
		if delay <= 0:
			DEBUG_MSG( "no delay:", callback )
		return self.fishingJoyMgr.addFishingJoyTimer( delay, callback )
		
	def getAttachEntity( self ):
		# virtual method.
		# 获取依附的entity，默认取当前服务器的捕鱼全局管理器
		return BigWorld.entities[BigWorld.globalData["FishingJoyMgr"].id]
		
	def cancel( self, timerID ):
		self.fishingJoyMgr.cancelFishingJoyTimer( timerID )
		
	def destroy( self ):
		self.fishingJoyMgr = None
		DEBUG_MSG( self.number )
		