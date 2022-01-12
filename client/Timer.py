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
		����Ѱ·��Ŀ��㸽����������
		@type		start:        float 
		@param		start:       ��ʼʱ��
		@type		interval:    float   
		@param		interval:    ���ʱ��
		@type		fun:         fuction   
		@param		fun:         �ص�����
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
		����Ѱ·��Ŀ��㸽����������
		@type		start:        float 
		@param		start:       ��ʼʱ��
		@type		interval:    float   
		@param		interval:    ���ʱ��
		@type		fun:         fuction   
		@param		fun:         �ص�����
	"""
	temp=callbackID(start,interval,callback)
	temp()
	return temp

def cancel( timerID ):
	"""
	ȡ���ص�
	@type		timerID:        instance 
	@param		timerID:       callbackID��һ��ʵ��
	"""
	if timerID==0:
		return 
	if hasattr(timerID,'callbackid'):
		
		BigWorld.cancelCallback(timerID.callbackid )
	
	
	

#

# 
#
#
