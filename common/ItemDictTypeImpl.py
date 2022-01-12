# -*- coding: gb18030 -*-

"""
背包集合
"""

# $Id: ItemDictTypeImpl.py,v 1.2 2006-08-11 03:15:23 phw Exp $

from bwdebug import *

class ItemDictTypeImpl( dict ):
	"""
	背包基础类，对道具实例进行存放，自定义类型基础底层通讯的部份；
	对于数据的保存和接口在KitbagBase里面。
	"""
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.
		
		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		items = []
		d = { "items":items }
		for k, v in obj.iteritems():
			items.append( { "order": k, "item": v } )
		return d
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = ItemDictTypeImpl()
		for v in dict["items"]:
			obj[v["order"]] = v["item"]
		return obj
		
	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.
		
		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, ItemDictTypeImpl )



# 构造自定义类型的实例
instance = ItemDictTypeImpl()

#
# $Log: not supported by cvs2svn $
# Revision 1.1  2006/08/09 08:21:01  phw
# no message
#
#
