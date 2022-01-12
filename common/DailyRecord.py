# -*- coding: gb18030 -*-

"""
记录一天能够进行某种活动的次数
"""

import Language
from bwdebug import *
import time

class DailyRecord:
	def __init__( self ):
		self._lastTime = 0	# 格式：20071013；记录最近一次活动时间
		self._degree = 0	# 当前完成次数
		
	def getDegree( self ):
		"""
		取得任务完成次数
		@return: INT
		"""
		return self._degree
	
	def incrDegree( self ):
		"""
		次数增长
		"""
		self._degree += 1
		
	def reset( self ):
		"""
		重置数据，设置开始时间为今天，设置当前完成次数为0
		"""
		year, month, day = time.localtime()[:3]
		self._lastTime = year * 10000 + month * 100 + day
		self._degree = 0
	
	def checklastTime( self ):
		"""
		检查接任务时间与当前时间是否是同一天
		@return: bool
		"""
		year, month, day = time.localtime()[:3]
		curr = year * 10000 + month * 100 + day
		return curr == self._lastTime

	##################################################################
	# BigWorld User Defined Type 的接口                              #
	##################################################################
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		return { "lastTime":obj._lastTime, "degree":obj._degree }

	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = DailyRecord()
		obj._lastTime = dict["lastTime"]
		obj._degree = dict["degree"]
		return obj

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, DailyRecord )

instance = DailyRecord()


#
# $Log: not supported by cvs2svn $
#
