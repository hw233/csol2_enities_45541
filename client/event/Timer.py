# -*- coding: gb18030 -*-
#
# $Id: Timer.py,v 1.12 2008-06-24 09:17:57 huangyongwei Exp $

"""
implement timer class��
-- 2006/06/10 : by huangyw
"""

import sys
import BigWorld
from bwdebug import *

output_del_info = False								# ��ɾ��ʱ���Ƿ����ɾ����Ϣ

class Timer( object ) :
	def __init__( self, callback = None, *args ) :
		self.__callback = callback
		self.__args = args							# callback �Ļص�����

		self.__interval = 0							# timer ��ʱ����
		self.__callbackID = 0						# ��¼����� callback ID
		self.__isRunning = False					# timer �Ƿ�������״̬

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
		��ʱ���� callback
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
	interval = property( _getInterval, _setInterval, "" )				# ��ȡ/���� timer ���е�ʱ����
	isRunning = property( _getIsRunning, "" )							# �ж� timer �Ƿ���������
