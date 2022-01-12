# -*- coding: gb18030 -*-

"""
������ݣ���Ʒ������
"""

import BigWorld
import csconst
from bwdebug import *
import csdefine

from config import TongItems
from config import TongSkills

class TongItemData:
	_instance = None
	def __init__( self ):
		"""
		���캯����
		"""
		assert TongItemData._instance is None		# ���������������ϵ�ʵ��
		self._datas = TongItems.serverDatas
		self._clientDatas = TongItems.Datas

	@staticmethod
	def instance():
		"""
		ͨ�� action id ��ȡactionʵ��
		"""
		if TongItemData._instance is None:
			TongItemData._instance = TongItemData()
		return TongItemData._instance

	def getDatas( self ):
		return self._datas

	def getClientDatas( self ):
		"""
		��ȡ�ͻ�������
		"""
		return self._clientDatas

class TongSkillData:
	_instance = None
	def __init__( self ):
		"""
		���캯����
		"""
		assert TongSkillData._instance is None		# ���������������ϵ�ʵ��
		self._datas = TongSkills.Datas

	@staticmethod
	def instance():
		"""
		ͨ�� action id ��ȡactionʵ��
		"""
		if TongSkillData._instance is None:
			TongSkillData._instance = TongSkillData()
		return TongSkillData._instance

	def getDatas( self ):
		return self._datas
		
	def getDatasByType( self, skillType ):
		return self._datas[ skillType]

	def getSkillTypes( self ):
		"""
		��ȡ��Ἴ�ܵ�����
		"""
		skillType = []
		for skill in self.getDatas().keys():
			if skill / 1000 not in skillType:
				skillType.append( skill / 1000 )
		return skillType

def tongItem_instance():
	return TongItemData.instance()

def tongSkill_instance():
	return TongSkillData.instance()