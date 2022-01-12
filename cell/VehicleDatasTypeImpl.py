# -*- coding: gb18030 -*-

"""
骑宠数据
"""

import Language
from bwdebug import *

class VehicleDatasTypeImpl( dict ):
	def __init__( self ):
		return

	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		return { "datas": obj.values() }

	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = VehicleDatasTypeImpl()
		for data in dict["datas"]:
			obj[data["id"]] = data
		return obj

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, VehicleDatasTypeImpl )

instance = VehicleDatasTypeImpl()
