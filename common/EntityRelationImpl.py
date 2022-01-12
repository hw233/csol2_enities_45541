# -*- coding: gb18030 -*-
#
# $Id: EntityRelationImpl.py,v 1.1 2008-05-09 03:14:51 kebiao Exp $

"""
主要封装的是 战斗列表 治疗列表 和 伤害列表的实现
"""
from bwdebug import *

class FightMarkImpl( dict ):
	"""
	"""
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.
		
		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		info = obj.items()[0]
		return { "entityID" : info[ 0 ], "time" : info[ 1 ] }
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = FightMarkImpl()
		obj[ dict[ "entityID" ] ] = dict[ "time" ]
		return obj
		
	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.
		
		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, FightMarkImpl )

class FightMarkImpl1( dict ):
	"""
	"""
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.
		
		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		info = obj.items()[0]
		return { "entityID" : info[ 0 ], "value" : info[ 1 ] }
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = FightMarkImpl1()
		obj[ dict[ "entityID" ] ] = dict[ "value" ]
		return obj
		
	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.
		
		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, FightMarkImpl1 )
		
class FightListImpl( dict ):
	"""
	"""
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.
		
		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		items = []
		d = { "items" : items }
		for entityID, time in obj.iteritems():
			c = FightMarkImpl()
			c[ entityID ] = time
			items.append( c )
		return d
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = FightListImpl()
		for d in dict[ "items" ]:
			obj.update( d )
		return obj
		
	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.
		
		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, FightListImpl )

class FightRecordImpl( dict ):
	"""
	"""
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.
		
		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		items = []
		d = { "items" : items }
		for entityID, value in obj.iteritems():
			c = FightMarkImpl1()
			c[ entityID ] = value
			items.append( c )
		return d
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = FightRecordImpl()
		for d in dict[ "items" ]:
			obj.update( d )
		return obj
		
	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.
		
		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, FightRecordImpl )
		
# 自定义类型实现实例
instance = FightMarkImpl()
instance1 = FightMarkImpl1()
instance2 = FightListImpl()
instance3 = FightRecordImpl()

#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/04/16 02:17:05  kebiao
# FightTable改名 EntityRelationTable
#
# Revision 1.1  2008/04/11 07:23:53  kebiao
# no message
#
# 
