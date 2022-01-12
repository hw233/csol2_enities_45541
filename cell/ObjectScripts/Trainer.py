# -*- coding: gb18030 -*-

"""
ѵ��ʦȫ��ʵ��������
"""
# $Id: Trainer.py,v 1.8 2008-01-31 07:29:12 yangkai Exp $

import Language
from bwdebug import *
import NPC
from Resource.SkillTrainerLoader import SkillTrainerLoader
g_skillTrainerList = SkillTrainerLoader.instance()

class Trainer( NPC.NPC ):
	"""
	ѵ��ʦȫ��ʵ�������� for cell��

	@ivar      attrSkills: �����б�
	@type      attrSkills dict
	"""

	def __init__( self ):
		"""
		"""
		self.attrTrainInfo = set()	# hash set
		NPC.NPC.__init__( self )

	def load( self, confSection ):
		"""
		��ȡ�����б������ļ�

		@param confSection: �����ļ���section
		@type  confSection: Language.PyDataSection
		@return: 		��
		"""
		NPC.NPC.load( self, confSection )	# �ȼ��ػ��������
		self.attrTrainInfo = g_skillTrainerList.get( self.className )

	def validLearn( self, player, skillID ):
		"""
		"""
		return skillID in self.attrTrainInfo


# Trainer.py
