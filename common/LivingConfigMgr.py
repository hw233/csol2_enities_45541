# -*- coding: gb18030 -*-

# $Id: LivingConfigMgr.py,v 1.1 16:58 2009-11-27 jiangyi Exp $

import Language
from bwdebug import *
import csdefine
from config.LivingSkillConfig import Datas as SData
from config.VimConfig import Datas as VData

class LivingConfigMgr:
	"""
	生活系统配置加载器
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert LivingConfigMgr._instance is None
		LivingConfigMgr._instance = self
		self._vDatas = VData
		self._vKeys = self._vDatas.keys()
		self._vKeys.sort()

		self._sDatas = SData
		self._sKeys = {}
		for skillID in self._sDatas:
			sKey = self._sDatas[skillID].keys()
			sKey.sort()
			self._sKeys[skillID] = sKey

	def getMaxVimByLevel( self, level ):
		"""
		通过玩家等级获取最大活力值
		"""
		try:
			return self._vDatas[level]
		except:
			return 0

	def getLivingLevelInfo( self, skillID, oldLevel ):
		"""
		通过已有等级信息获取新等级信息
		"""
		sKeys = self._sKeys[skillID]
		newLevel = oldLevel + 1
		try:
			if newLevel in sKeys:
				oldMaxSleight = self.getSleLastMax( skillID, newLevel )
				if newLevel == 1:
					oldMaxSleight = 0
				return ( oldMaxSleight, newLevel )
			else:
				return ( 0, 1 )
		except:
			return ( 0, 1 )

	def isMaxLevel( self, skillID, level ):
		"""
		返回等级是否已经到顶
		"""
		skillInfo = self._sDatas[skillID]
		sKeys = skillInfo.keys()
		sKeys.sort()
		for k in sKeys:
			if level < k: return False
		return True

	def getReqLevelByLevel( self, skillID, level ):
		"""
		通过技能等级获取所需等级
		"""
		try:
			return self._sDatas[skillID][level]["reqLevel"]
		except:
			return -1

	def getReqMoneyByLevel( self, skillID, level ):
		"""
		通过技能等级获取所需金钱
		"""
		try:
			return self._sDatas[skillID][level]["reqMoney"]
		except:
			return -1

	def getDesByLevel( self, skillID, level ):
		"""
		通过技能等级获取对应描述
		"""
		try:
			return self._sDatas[skillID][level]["description"]
		except:
			return None
	
	def getDes2ByLevel( self, skillID, level ):
		"""
		通过技能等级获取对应描述
		"""
		try:
			return self._sDatas[skillID][level]["description2"]
		except:
			return None

	def getSleLastMax( self, skillID, nowLevel ):
		"""
		通过当前技能等级获取前一级的最大熟练度
		"""
		try:
			if nowLevel > 1:
				return self._sDatas[skillID][nowLevel - 1]["sleightMax"]
			else:
				return self._sDatas[skillID][nowLevel]["sleightMax"]
		except:
			return 0

	def getMaxSleightByLevel( self, skillID, level ):
		"""
		通过等级获取当前最大熟练度
		"""
		try:
			return self._sDatas[skillID][level]["sleightMax"]
		except:
			return -1

	def isLivingSkill( self, skillID ) :
		"""
		根据ID判断是否为生活技能
		"""
		return self._sDatas.has_key( skillID )

	@classmethod
	def instance( SELF ):
		"""
		"""
		if SELF._instance is None:
			SELF._instance = LivingConfigMgr()
		return SELF._instance