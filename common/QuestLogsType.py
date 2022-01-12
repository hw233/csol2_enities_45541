# -*- coding: gb18030 -*-
#
"""
任务日志类型,用于记录已完成的任务
"""
# $Id: QuestLogsType.py,v 1.6 2008-06-10 09:00:16 huangyongwei Exp $

from bwdebug import *
import struct


C_FIELD_KEY = "questLogs"
C_LEN_HEAD_STR = "=i"
C_LEN_HEAD = struct.calcsize( C_LEN_HEAD_STR )

class QuestLogsType:
	def __init__( self ):
		self._questLogs = set()		# 用set做大量的比较时将会比用list有效率

	def has( self, questID ):
		"""
		@return: BOOL
		@rtype:  BOOL
		"""
		return questID in self._questLogs

	def elements( self ) :
		"""
		获取所有元素( hyw -- 2008.06.10 )
		"""
		return set( self._questLogs )

	def list( self ) :
		"""
		获取所有元素的链表形式
		"""
		return list( self._questLogs )

	def add( self, questID ):
		"""
		@return: 无
		"""
		self._questLogs.add( questID )

	def remove( self, questID ):
		"""
		@return: 无
		"""
		self._questLogs.discard( questID )

	def clear( self ):
		"""
		"""
		self._questLogs.clear()


	##################################################################
	# BigWorld 的接口                                                #
	##################################################################
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		return { "values" : list(obj._questLogs) }

	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = QuestLogsType()
		obj._questLogs = set( dict["values"] )
		return obj

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, QuestLogsType )

instance = QuestLogsType()

#
# $Log: not supported by cvs2svn $
# Revision 1.5  2007/03/07 02:29:58  kebiao
# 修改了使用FIXED_DICT类型
#
# Revision 1.4  2006/03/22 02:34:02  phw
# 适应1.7版的自定义类型，作相应修改
#
# Revision 1.3  2006/03/20 03:18:54  wanhaipeng
# Mark stream.将来要改对！！！
#
# Revision 1.2  2006/03/16 07:09:23  wanhaipeng
# Change bind Format.
#
# Revision 1.1  2006/03/10 05:09:06  phw
# 已完成任务日志记录
#
#
