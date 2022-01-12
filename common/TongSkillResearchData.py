# -*- coding: gb18030 -*-
#
# $Id: TongSkillResearchData.py,v 1.12 2008-07-15 04:21:55 kebiao Exp $

"""
帮会建筑资源加载部分。
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
		构造函数。
		"""
		assert TongSkillResearchData._instance is None		# 不允许有两个以上的实例
		self._datas = TongSkillResearch.Datas	# key is BuffTime::_id and value is instance of BuffTime which derive from it.
		TongSkillResearchData._instance = self
		self.tongPetSkills = {}
		self.tongSkills = {}
		for skillID, skillData in self._datas.iteritems():		# 根据技能的类型把技能分类，分为一般帮会技能和宠物帮会技能
			for skillValue in skillData.itervalues():
				break
			skillType = skillValue["skillType"]
			if skillType == csdefine.TONG_SKILL_ROLE:
				self.tongSkills[skillID] = skillData
			elif skillType == csdefine.TONG_SKILL_PET:
				self.tongPetSkills[skillID] = skillData
			else:
				ERROR_MSG( "帮会技能( %i )类型( %i )配置错误。" % ( skillID, skillType ) )
		
	@staticmethod
	def instance():
		"""
		通过 action id 获取action实例
		"""
		if TongSkillResearchData._instance is None:
			TongSkillResearchData._instance = TongSkillResearchData()
		return TongSkillResearchData._instance

	def __getitem__( self, key ):
		"""
		取得Skill实例
		"""
		return self._datas[ key ]
	
	def getDatas( self ):
		return self._datas

	def getDatasByType( self, skillType ):
		"""
		根据技能类型获得技能学习数据
		"""
		if skillType == csdefine.TONG_SKILL_ROLE:
			return self.tongSkills
		elif skillType == csdefine.TONG_SKILL_PET:
			return self.tongPetSkills
		elif skillType == csdefine.TONG_SKILL_ALL:
			return self._datas
		else:
			ERROR_MSG( "帮会技能类型( %i )错误。" % ( skillType ) )
			return {}

	def getTypeBySkillID( self, skillID ):
		"""
		根据技能ID获得技能类型
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
