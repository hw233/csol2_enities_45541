# -*- coding: gb18030 -*-

"""
帮会数据：物品、技能
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
		构造函数。
		"""
		assert TongItemData._instance is None		# 不允许有两个以上的实例
		self._datas = TongItems.serverDatas
		self._clientDatas = TongItems.Datas

	@staticmethod
	def instance():
		"""
		通过 action id 获取action实例
		"""
		if TongItemData._instance is None:
			TongItemData._instance = TongItemData()
		return TongItemData._instance

	def getDatas( self ):
		return self._datas

	def getClientDatas( self ):
		"""
		获取客户端数据
		"""
		return self._clientDatas

class TongSkillData:
	_instance = None
	def __init__( self ):
		"""
		构造函数。
		"""
		assert TongSkillData._instance is None		# 不允许有两个以上的实例
		self._datas = TongSkills.Datas

	@staticmethod
	def instance():
		"""
		通过 action id 获取action实例
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
		获取帮会技能的类型
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