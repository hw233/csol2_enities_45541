# -*- coding: gb18030 -*-

import time
import BigWorld

class Counter( object ) :
	"""��ʱ��"""

	def __init__( self ) :
		self.__cbid = 0
		self.__start_time = 0
		self.__interval = 1.0
		self.__duration = 0
		self.__callback = None

	def setCallback( self, cb ) :
		"""���ûص�"""
		self.__callback = cb

	def setTime( self, time ) :
		"""���ü�ʱʱ��"""
		self.__duration = time

	def setInterval( self, interval ) :
		"""���ûص���������ֵ��Ӱ��ص�ʱ��ľ�ȷ��"""
		self.__interval = interval

	def countdown( self ) :
		"""��ʼ��ʱ"""
		self.stop()
		self.__start_time = time.time()
		self.__count()

	def stop( self ) :
		"""��ֹ��ʱ"""
		BigWorld.cancelCallback( self.__cbid )

	def __count( self ) :
		"""��ʱ�ص�"""
		leave_time = self.__duration + self.__start_time - time.time()
		if leave_time < 0 :
			self.__callback( 0 )
			return
		self.__callback( leave_time )
		interval = min( self.__interval, leave_time )
		self.__cbid = BigWorld.callback( interval, self.__count )
