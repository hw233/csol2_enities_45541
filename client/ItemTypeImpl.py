# -*- coding: gb18030 -*-
#
# $Id: ItemTypeImpl.py,v 1.3 2008-08-09 01:54:01 wangshufeng Exp $

"""
client部份的ItemTypeImpl实现模块.
"""
from items.CItemBase import CItemBase
import items
import cPickle

g_items = items.instance()

class ItemTypeImpl:
	"""
	"""
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		if obj is None:
			# extra/tmpExtra 默认值为 {}
			temp = cPickle.dumps( {} )
			return { "uid" : 0, "id" : 0, "amount" : 0, "order" : 0, "extra" : temp, "tmpExtra" : temp }
		return obj.addToDict()

	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		if dict["id"] == 0: return None
		return g_items.createFromDict( dict )

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		if obj is None: return True
		return isinstance( obj, CItemBase )


# 自定义类型实现实例
instance = ItemTypeImpl()

#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/06/23 07:45:17  yangkai
# 客户端物品 None 支持
#
# Revision 1.1  2006/08/09 08:22:20  phw
# no message
#
#