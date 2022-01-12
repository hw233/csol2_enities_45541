# -*- coding: gb18030 -*-
#
# $Id: TongSkillResearchData.py,v 1.12 2008-07-15 04:21:55 kebiao Exp $

"""
��Ὠ����Դ���ز��֡�
"""

import BigWorld
import Language
import csconst
from bwdebug import *
import Function
import time
from config import TongSkillResearch
import csdefine

class TongSkillResearchData:
	_instance = None
	def __init__( self ):
		"""
		���캯����
		"""
		assert TongSkillResearchData._instance is None		# ���������������ϵ�ʵ��
		self._datas = TongSkillResearch.Datas	# key is BuffTime::_id and value is instance of BuffTime which derive from it.
		TongSkillResearchData._instance = self
		self.tongPetSkills = {}
		self.tongSkills = {}
		for skillID, skillData in self._datas.iteritems():		# ���ݼ��ܵ����ͰѼ��ܷ��࣬��Ϊһ���Ἴ�ܺͳ����Ἴ��
			for skillValue in skillData.itervalues():
				break
			skillType = skillValue["skillType"]
			if skillType == csdefine.TONG_SKILL_ROLE:
				self.tongSkills[skillID] = skillData
			elif skillType == csdefine.TONG_SKILL_PET:
				self.tongPetSkills[skillID] = skillData
			else:
				ERROR_MSG( "��Ἴ��( %i )����( %i )���ô���" % ( skillID, skillType ) )
		
	@staticmethod
	def instance():
		"""
		ͨ�� action id ��ȡactionʵ��
		"""
		if TongSkillResearchData._instance is None:
			TongSkillResearchData._instance = TongSkillResearchData()
		return TongSkillResearchData._instance

	def __getitem__( self, key ):
		"""
		ȡ��Skillʵ��
		"""
		return self._datas[ key ]
	
	def getDatas( self ):
		return self._datas

	def getDatasByType( self, skillType ):
		"""
		���ݼ������ͻ�ü���ѧϰ����
		"""
		if skillType == csdefine.TONG_SKILL_ROLE:
			return self.tongSkills
		elif skillType == csdefine.TONG_SKILL_PET:
			return self.tongPetSkills
		elif skillType == csdefine.TONG_SKILL_ALL:
			return self._datas
		else:
			ERROR_MSG( "��Ἴ������( %i )����" % ( skillType ) )
			return {}

	def getTypeBySkillID( self, skillID ):
		"""
		���ݼ���ID��ü�������
		"""
		if skillID in self.tongSkills.keys():
			return csdefine.TONG_SKILL_ROLE
		elif skillID in self.tongPetSkills.keys():
			return csdefine.TONG_SKILL_PET
		else:
			return csdefine.TONG_SKILL_ALL

def instance():
	return TongSkillResearchData.instance()

#
# $Log: not supported by cvs2svn $
#
#
