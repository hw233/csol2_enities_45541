# -*- coding: gb18030 -*-
#
# $Id: AIDataPacketImpl.py,v 1.2 2008-04-21 00:58:31 kebiao Exp $

"""
"""
from bwdebug import *

class AIDataImpl( dict ):
	"""
	实现cell部份的ai数据创建、还原
	"""
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.
		
		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		return obj
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = AIDataImpl()
		obj.update( dict )
		return obj
		
	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.
		
		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, AIDataImpl )
		
class AIDictDataImpl( dict ):
	"""
	实现cell部份的ai数据创建、还原
	"""
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.
		
		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		aiData = []
		d = { "aiData" : aiData }
		for lv, aiList in obj.iteritems():
			for ai in aiList:
				x = AIDataImpl()
				x[ "lv" ] = lv
				x[ "ai" ] = ai
				aiData.append( x )
		return d
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = AIDictDataImpl()
		for aidata in dict["aiData"]:
			if obj.has_key( aidata[ "lv" ] ):
				obj[ aidata[ "lv" ] ].append( aidata[ "ai" ] )
			else:
				obj[ aidata[ "lv" ] ] = [ aidata[ "ai" ] ]
		return obj
		
	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.
		
		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, AIDictDataImpl )

class AIEventDictDataImpl( dict ):
	"""
	实现cell部份的ai数据创建、还原
	"""
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.
		
		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		event, aiDatas = obj.items()[0]
		t = AIDictDataImpl()
		t.update( aiDatas )
		return { "event" : event, "aiDatas" : t }
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = AIEventDictDataImpl()
		obj[ dict[ "event" ] ] = dict["aiDatas"]
		return obj
		
	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.
		
		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, AIEventDictDataImpl )

class AIEventDictPacketImpl( dict ):
	"""
	实现cell部份的ai数据创建、还原
	"""
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.
		
		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		items = []
		d = { "items" : items }
		for event, aiDatas in obj.iteritems():
			c = AIEventDictDataImpl()
			c[ event ] = aiDatas
			items.append( c )
		return d
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = AIEventDictPacketImpl()
		for d in dict[ "items" ]:
			obj.update( d )
		return obj
		
	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.
		
		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, AIEventDictPacketImpl )
		
# 自定义类型实现实例
instance = AIDictDataImpl()
instance1 = AIEventDictDataImpl()
instance2 = AIEventDictPacketImpl()
instance3 = AIDataImpl()

#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/04/07 08:57:42  kebiao
# no message
#
# 
# 
