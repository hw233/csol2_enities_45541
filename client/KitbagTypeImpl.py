# -*- coding: gb18030 -*-

"""
放在背包集合里的背包基础类

"""

# $Id: KitbagTypeImpl.py,v 1.4 2008-05-30 03:04:21 yangkai Exp $

from bwdebug import *
from KitbagBase import KitbagBase

class KitbagTypeImpl:
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
		return { "items" : obj.getDatas() }
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
 		obj = KitbagBase()

		for item in dict["items"]:
			if item is None: continue	# 如果某个物品为None，就表示它是不存在的，因此直接丢弃
			order = item.getOrder()
			obj._dataList[order] = item
			obj._uid2order[item.uid] = order
		return obj

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, KitbagBase )



# 构造自定义类型的实例
instance = KitbagTypeImpl()

#
# $Log: not supported by cvs2svn $
# Revision 1.3  2007/11/08 09:41:43  phw
# self.freeze -> self.freezeState
# 修正了属性名与方法名同名的bug
#
# Revision 1.2  2006/08/11 02:39:45  phw
# 由于删除了KITEM和KITEMS，作相应改动
#
# Revision 1.1  2006/08/09 08:22:20  phw
# no message
#
#
