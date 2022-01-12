# -*- coding: gb18030 -*-
#
# $Id: LoopQuestTypeImpl.py,v 1.1 2007-11-02 03:32:39 phw Exp $

"""
任务目标管理器，一个实例就对应一个任务目标。
实现自定义数据类型接口，解决传输问题。
"""

import Language
from bwdebug import *
import time

class LoopQuestTypeImpl:
	def __init__( self ):
		self._questID = 0	# 任务唯一编号，用于区分当前数据是属于哪个任务的
		self._startTime = 0	# 格式：20071013；任务开始时间，用于判断是否在同一天（真实时间的一天）
		self._degree = 0	# 当前完成次数

	
	def setQuestID( self, questID ):
		"""
		"""
		self._questID = questID
	
	def getQuestID( self ):
		"""
		"""
		return self._questID
		
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
		self._startTime = year * 10000 + month * 100 + day
		self._degree = 0
	
	def checkStartTime( self ):
		"""
		检查接任务时间与当前时间是否是同一天
		@return: bool
		"""
		year, month, day = time.localtime()[:3]
		curr = year * 10000 + month * 100 + day
		return curr == self._startTime

	##################################################################
	# BigWorld User Defined Type 的接口                              #
	##################################################################
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		return { "questID":obj._questID, "startTime":obj._startTime, "degree":obj._degree }

	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = LoopQuestTypeImpl()
		obj._questID = dict["questID"]
		obj._startTime = dict["startTime"]
		obj._degree = dict["degree"]
		return obj

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, LoopQuestTypeImpl )

instance = LoopQuestTypeImpl()


#
# $Log: not supported by cvs2svn $
#
