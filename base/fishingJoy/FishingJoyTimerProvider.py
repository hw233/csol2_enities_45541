# -*- coding:gb18030 -*-

from bwdebug import *

FISH_REBORN_TIMER_ID = 1

class FishingJoyTimerProvider:
	def __init__( self ):
		self.fishingJoyTimers = {}		# like as { timerID:callback, ... }，timer回调数据
		
	def onTimer( self, timerID, useArg ):
		if useArg == FISH_REBORN_TIMER_ID:
			self.fishingJoyTimers.pop( timerID )()
			
	def addFishingJoyTimer( self, delay, callback ):
		timerID = self.addTimer( delay, 0, FISH_REBORN_TIMER_ID )
		self.fishingJoyTimers[timerID] = callback
		return timerID
		
	def cancelFishingJoyTimer( self, timerID ):
		if self.fishingJoyTimers.has_key( timerID ):
			self.delTimer( timerID )
			del self.fishingJoyTimers[timerID]
			
	#def addTimer( self, initialOffset, repeatOffset=0, userArg=0 ):
	#	ERROR_MSG( "( %s ) cant use virtual method = 0." % str( self ) )