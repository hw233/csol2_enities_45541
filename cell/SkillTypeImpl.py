# -*- coding: gb18030 -*-
#
# $Id: SkillTypeImpl.py,v 1.2 2007-08-23 01:34:36 kebiao Exp $

"""
���˼·��
	1.cell/base/client/db�и��Ե�SkillTypeImpl.pyģ�飬��ģ��ΪFIXED_DICT SKILL��ʵ��ģ�飻
	2.��ģ�����ʵ����Ҫȥʵ�� getDictFromObj()��createObjFromDict()��getDictFromObj() ������
	3.��ģ��ʵ��ʱ���뿼�������ڸ������д���ʱ��һ���ԣ���ִ��cell -> base��db -> base�ȴ���ʱ���ܱ�֤���ݵĻ�ԭ��
"""
from bwdebug import *
from Resource.SkillLoader import g_skills
from Resource.Skills.SpellBase.Skill import Skill



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
			
		skillDict 			= obj.addToDict()
		skillDict[ "id" ]   = obj.getID()
		skillDict[ "uid" ]  = obj.getUID()
		return skillDict
		
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
			sk = g_skills[dict["id"]]
		except KeyError:
			ERROR_MSG( "skill %i not found." % dict["id"] )
			return None	
		return sk.createFromDict( dict )
		
	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.
		
		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return (obj is None) or isinstance( obj, Skill )


# �Զ�������ʵ��ʵ��
instance = SkillTypeImpl()


# SkillTypeImpl.py
