# -*- coding: gb18030 -*-

import time
import BigWorld

class Counter( object ) :
	"""计时器"""

	def __init__( self ) :
		self.__cbid = 0
		self.__start_time = 0
		self.__interval = 1.0
		self.__duration = 0
		self.__callback = None

	def setCallback( self, cb ) :
		"""设置回调"""
		self.__callback = cb

	def setTime( self, time ) :
		"""设置计时时间"""
		self.__duration = time

	def setInterval( self, interval ) :
		"""设置回调间隔，这个值会影响回调时间的精确度"""
		self.__interval = interval

	def countdown( self ) :
		"""开始计时"""
		self.stop()
		self.__start_time = time.time()
		self.__count()

	def stop( self ) :
		"""终止计时"""
		BigWorld.cancelCallback( self.__cbid )

	def __count( self ) :
		"""计时回调"""
		leave_time = self.__duration + self.__start_time - time.time()
		if leave_time < 0 :
			self.__callback( 0 )
			return
		self.__callback( leave_time )
		interval = min( self.__interval, leave_time )
		self.__cbid = BigWorld.callback( interval, self.__count )
