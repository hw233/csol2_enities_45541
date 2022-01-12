# -*- coding: gb18030 -*-

# $Id: SkillTeachLoader.py,v 1.2 2007-12-18 02:35:40 kebiao Exp $

import Language
from bwdebug import *
from config.skill import SkillTeachData


class SkillTeachLoader:
	"""
	配置加载类
	"""
	_instance = None
	def __init__( self ):
		assert SkillTeachLoader._instance is None
		self._datas = SkillTeachData.Datas
		SkillTeachLoader._instance = self

	def __getitem__( self, key ):
		"""
		取得实例
		"""
		return self._datas[key]

	def has( self, key ):
		"""
		"""
		return key in self._datas

	@staticmethod
	def instance():
		"""
		"""
		if SkillTeachLoader._instance is None:
			SkillTeachLoader._instance = SkillTeachLoader()
		return SkillTeachLoader._instance

def instance():
	return SkillTeachLoader.instance()
	
g_skillTeachDatas = SkillTeachLoader.instance()


# $Log: not supported by cvs2svn $
# Revision 1.1  2007/12/08 08:05:12  kebiao
# 调整技能学习
#
#