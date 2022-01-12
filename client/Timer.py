# -*- coding: gb18030 -*-
#
# $Id: Timer.py,v 1.2 2009-11-06 06:01:11 aijisong Exp $

"""
usage:
	import Timer
	timerID = Timer.addTimer( start, interval, callback )	# add a timer
	Timer.cancel( timerID )									# remove a timer
"""

import sys
import BigWorld
from bwdebug import *
from Function import Functor

class callbackID:
	
	def __init__(self,start,interval,fun):
		"""
		设置寻路到目标点附近的侦测距离
		@type		start:        float 
		@param		start:       开始时间
		@type		interval:    float   
		@param		interval:    间隔时间
		@type		fun:         fuction   
		@param		fun:         回调函数
		"""
		self.callbackid=0
		self.start=start
		self.interval=interval
		self.callback=fun
		
	def __call__(self):
		if self.start<0 or self.interval<0:
			EXCEHOOK_MSG( "the start time and interval time must bigger than zero")
			return 
		if self.interval>0:
			 self.callbackid=BigWorld.callback(self.start,self.tempfun)
			
		elif self.interval==0:
			self.callbackid=BigWorld.callback(self.start,self.callback)
			
		else:
			pass
			
	def tempfun(self):
		self.callbackid=BigWorld.callback(self.interval,self.tempfun)
		self.callback()
		
	def __del__(self):
		pass
		
		
def addTimer( start, interval, callback ):
	"""
		设置寻路到目标点附近的侦测距离
		@type		start:        float 
		@param		start:       开始时间
		@type		interval:    float   
		@param		interval:    间隔时间
		@type		fun:         fuction   
		@param		fun:         回调函数
	"""
	temp=callbackID(start,interval,callback)
	temp()
	return temp

def cancel( timerID ):
	"""
	取消回调
	@type		timerID:        instance 
	@param		timerID:       callbackID的一个实例
	"""
	if timerID==0:
		return 
	if hasattr(timerID,'callbackid'):
		
		BigWorld.cancelCallback(timerID.callbackid )
	
	
	

#

# 
#
#
