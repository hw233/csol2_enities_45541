# -*- coding: gb18030 -*-
#
# $Id: SkillTypeImpl.py,v 1.1 2007-06-27 02:05:01 phw Exp $

"""
���˼·��
	1.cell/base/client/db�и��Ե�SkillTypeImpl.pyģ�飬��ģ��ΪFIXED_DICT SKILL��ʵ��ģ�飻
	2.��ģ�����ʵ����Ҫȥʵ�� getDictFromObj()��createObjFromDict()��getDictFromObj() ������
	3.��ģ��ʵ��ʱ���뿼�������ڸ������д���ʱ��һ���ԣ���ִ��cell -> base��db -> base�ȴ���ʱ���ܱ�֤���ݵĻ�ԭ��
"""
from bwdebug import *
import skills

class SkillTypeImpl:
	"""
	ʵ��cell���ݵ�skill���ݴ�������ԭ
	"""
	def __init__( self ):
		self.defaultValue = { "id" : 0, "uid" : 0, "param" : None }	# ������ʾû�м��ܵ�Ĭ��ֵ
		
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.
		
		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		# ���objΪNone�����ʾ��û�и���skill��Ϊ��ʹFIXED_DICT���������棨����б�Ҫ�������Ƿ���idֵΪ0���ֵ�
		if obj is None:
			return self.defaultValue
		return obj.addToDict()
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		# ���skillIDΪ0����������Ϊ��û�и���skill�����ֱ�ӷ���None
		if dict["id"] == 0:
			return None
			
		try:
			sk = skills.getSkill( dict["id"] )
		except KeyError:
			ERROR_MSG( "skill %i not found." % dict["id"] )
			return None
		
		skill = sk.createFromDict( dict )
		if dict["uid"] > 0: 
			skill.setUID( dict["uid"] ) 
						
		return skill
		
	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.
		
		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		# �Ҽ��裨��Ҳֻ�����������ֻ���ڷ������������ݹ�����ʱ��ŵ��ã�
		# ����Ϊ������������һ������ȷ�ģ������ֱ�ӷ���True
		return True


# �Զ�������ʵ��ʵ��
instance = SkillTypeImpl()


# SkillTypeImpl.py
