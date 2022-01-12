# -*- coding: gb18030 -*-
#
# $Id: AIObjImpl.py,v 1.4 2008-05-14 03:51:14 kebiao Exp $

"""
"""
from bwdebug import *
from Resource.AI.AIBase import AIBase
import Resource.AIData
g_aiDatas = Resource.AIData.aiData_instance()

class AIObjImpl:
	"""
	实现cell部份的ai数据创建、还原
	"""
	def __init__( self ):
		self.defaultValue = { "id" : -1, "param" : None }	# 用来表示没有ai的默认值
		
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.
		
		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		# 如果obj为None，则表示其没有附上ai，为了使FIXED_DICT能正常保存（如果有必要），我们返回id值为0的字典
		if obj is None:
			return self.defaultValue
			
		Dict 			= obj.addToDict()
		Dict[ "id" ]    = obj.getID()
		return Dict
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		# 如果aiID为0，则我们认为其没有附上ai，因此直接返回None
		if dict["id"] < 0:
			return None
		
		try:
			ai = g_aiDatas[dict["id"]]
		except KeyError:
			ERROR_MSG( "ai %i not found." % dict["id"] )
			return None
		aiInstance = ai.createFromDict( dict )
		return aiInstance
		
	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.
		
		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return ( obj is None ) or isinstance( obj, AIBase )


# 自定义类型实现实例
instance = AIObjImpl()


# AIObjImpl.py
