# -*- coding: gb18030 -*-
#
# $Id: SkillTypeImpl.py,v 1.1 2007-06-27 02:04:47 phw Exp $

"""
���˼·��
	1.cell/base/client/db�и��Ե�SkillTypeImpl.pyģ�飬��ģ��ΪFIXED_DICT SKILL��ʵ��ģ�飻
	2.��ģ�����ʵ����Ҫȥʵ�� getDictFromObj()��createObjFromDict()��getDictFromObj() ������
	3.��ģ��ʵ��ʱ���뿼�������ڸ������д���ʱ��һ���ԣ���ִ��cell -> base��db -> base�ȴ���ʱ���ܱ�֤���ݵĻ�ԭ��
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


# �Զ�������ʵ��ʵ��
instance = SkillTypeImpl()

# SkillTypeImpl.py
