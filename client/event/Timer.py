# -*- coding: gb18030 -*-
#
# $Id: Timer.py,v 1.12 2008-06-24 09:17:57 huangyongwei Exp $

"""
implement timer class。
-- 2006/06/10 : by huangyw
"""

import sys
import BigWorld
from bwdebug import *

output_del_info = False								# 被删除时，是否输出删除信息

class Timer( object ) :
	def __init__( self, callback = None, *args ) :
		self.__callback = callback
		self.__args = args							# callback 的回调参数

		self.__interval = 0							# timer 的时间间隔
		self.__callbackID = 0						# 记录引擎的 callback ID
		self.__isRunning = False					# timer 是否处于运行状态

	def dispose( self ) :
		self.stop()
		self.__callback = None
		self.__args = ()

	def __del__( self ) :
		if output_del_info :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __notify( self ) :
		"""
		定时触发 callback
		"""
		try :
			self.__callback( *self.__args )
		except Exception, errStr :
			self.stop()
			EXCEHOOK_MSG()
		if self.__isRunning :
			self.__callbackID = BigWorld.callback( self.__interval, self.__notify )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def start( self, *args ) :
		"""
		start timer
		"""
		if self.isRunning : self.stop()
		if self.__interval <= 0 : return
		self.__args = args
		self.__isRunning = True
		self.__notify()

	def stop( self ) :
		"""
		stop timer
		"""
		self.__isRunning = False
		BigWorld.cancelCallback( self.__callbackID )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getInterval( self ) :
		"""
		get trigering interval
		"""
		return self.__interval

	def _setInterval( self, value ) :
		"""
		set trigering interval
		"""
		self.__interval = value
		if value <= 0 : self.stop()

	# ---------------------------------------
	def _getIsRunning( self ) :
		return self.__isRunning


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	interval = property( _getInterval, _setInterval, "" )				# 获取/设置 timer 运行的时间间隔
	isRunning = property( _getIsRunning, "" )							# 判断 timer 是否在运行中
