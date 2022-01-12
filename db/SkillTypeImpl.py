# -*- coding: gb18030 -*-
#
# $Id: SkillTypeImpl.py,v 1.1 2007-06-27 02:04:47 phw Exp $

"""
设计思路：
	1.cell/base/client/db有各自的SkillTypeImpl.py模块，此模块为FIXED_DICT SKILL的实现模块；
	2.各模块根据实际需要去实现 getDictFromObj()、createObjFromDict()、getDictFromObj() 方法；
	3.各模块实现时必须考虑数据在各部份中传输时的一致性，即执行cell -> base或db -> base等传输时，能保证数据的还原；
"""
from bwdebug import *

class SkillTypeImpl:
	"""
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
		return dict
		
	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.
		
		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return True


# 自定义类型实现实例
instance = SkillTypeImpl()

# SkillTypeImpl.py
