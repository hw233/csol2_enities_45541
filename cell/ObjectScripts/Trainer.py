# -*- coding: gb18030 -*-

"""
训练师全局实例基础类
"""
# $Id: Trainer.py,v 1.8 2008-01-31 07:29:12 yangkai Exp $

import Language
from bwdebug import *
import NPC
from Resource.SkillTrainerLoader import SkillTrainerLoader
g_skillTrainerList = SkillTrainerLoader.instance()

class Trainer( NPC.NPC ):
	"""
	训练师全局实例基础类 for cell。

	@ivar      attrSkills: 技能列表
	@type      attrSkills dict
	"""

	def __init__( self ):
		"""
		"""
		self.attrTrainInfo = set()	# hash set
		NPC.NPC.__init__( self )

	def load( self, confSection ):
		"""
		读取技能列表配置文件

		@param confSection: 配置文件的section
		@type  confSection: Language.PyDataSection
		@return: 		无
		"""
		NPC.NPC.load( self, confSection )	# 先加载基层的配置
		self.attrTrainInfo = g_skillTrainerList.get( self.className )

	def validLearn( self, player, skillID ):
		"""
		"""
		return skillID in self.attrTrainInfo


# Trainer.py
