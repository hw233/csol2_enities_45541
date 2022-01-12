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
	ʵ��cell���ݵ�ai���ݴ�������ԭ
	"""
	def __init__( self ):
		self.defaultValue = { "id" : -1, "param" : None }	# ������ʾû��ai��Ĭ��ֵ
		
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.
		
		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		# ���objΪNone�����ʾ��û�и���ai��Ϊ��ʹFIXED_DICT���������棨����б�Ҫ�������Ƿ���idֵΪ0���ֵ�
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
		# ���aiIDΪ0����������Ϊ��û�и���ai�����ֱ�ӷ���None
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


# �Զ�������ʵ��ʵ��
instance = AIObjImpl()


# AIObjImpl.py
