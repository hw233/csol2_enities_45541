# -*- coding: gb18030 -*-

"""
��¼һ���ܹ�����ĳ�ֻ�Ĵ���
"""

import Language
from bwdebug import *
import time

class DailyRecord:
	def __init__( self ):
		self._lastTime = 0	# ��ʽ��20071013����¼���һ�λʱ��
		self._degree = 0	# ��ǰ��ɴ���
		
	def getDegree( self ):
		"""
		ȡ��������ɴ���
		@return: INT
		"""
		return self._degree
	
	def incrDegree( self ):
		"""
		��������
		"""
		self._degree += 1
		
	def reset( self ):
		"""
		�������ݣ����ÿ�ʼʱ��Ϊ���죬���õ�ǰ��ɴ���Ϊ0
		"""
		year, month, day = time.localtime()[:3]
		self._lastTime = year * 10000 + month * 100 + day
		self._degree = 0
	
	def checklastTime( self ):
		"""
		��������ʱ���뵱ǰʱ���Ƿ���ͬһ��
		@return: bool
		"""
		year, month, day = time.localtime()[:3]
		curr = year * 10000 + month * 100 + day
		return curr == self._lastTime

	##################################################################
	# BigWorld User Defined Type �Ľӿ�                              #
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
