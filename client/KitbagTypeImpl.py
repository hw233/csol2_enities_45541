# -*- coding: gb18030 -*-

"""
���ڱ���������ı���������

"""

# $Id: KitbagTypeImpl.py,v 1.4 2008-05-30 03:04:21 yangkai Exp $

from bwdebug import *
from KitbagBase import KitbagBase

class KitbagTypeImpl:
	"""
	���������࣬�Ե���ʵ�����д�ţ��Զ������ͻ����ײ�ͨѶ�Ĳ��ݣ�
	�������ݵı���ͽӿ���KitbagBase���档
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
			if item is None: continue	# ���ĳ����ƷΪNone���ͱ�ʾ���ǲ����ڵģ����ֱ�Ӷ���
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



# �����Զ������͵�ʵ��
instance = KitbagTypeImpl()

#
# $Log: not supported by cvs2svn $
# Revision 1.3  2007/11/08 09:41:43  phw
# self.freeze -> self.freezeState
# �������������뷽����ͬ����bug
#
# Revision 1.2  2006/08/11 02:39:45  phw
# ����ɾ����KITEM��KITEMS������Ӧ�Ķ�
#
# Revision 1.1  2006/08/09 08:22:20  phw
# no message
#
#
