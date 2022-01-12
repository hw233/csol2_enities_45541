# -*- coding: gb18030 -*-
# added by dqh

# common global
import Language
from bwdebug import *
import csdefine

# config
from config.PGNagualConfig import Datas as PData

class PGNagualConfigMgr:
	"""
	盘古守护对应数据加载器
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert PGNagualConfigMgr._instance is None
		PGNagualConfigMgr._instance = self

		self._pDatas = PData
		self._pKeys = {}
		for className in self._pDatas:
			pKey = self._pDatas[className].keys()
			pKey.sort()
			self._pKeys[className] = pKey

	def getPGHPMax( self, className, realm ):
		"""
		通过盘古守护境界所对应的生命值
		"""
		try:
			return self._pDatas[className][realm]["HP"]
		except:
			return -1

	def getAttackType( self, className, realm ):
		"""
		通过盘古守护境界获取获取攻击类型
		"""
		try:
			return self._pDatas[className][realm]["attackType"]
		except:
			return -1

	def getDamage( self, className, realm ):
		"""
		通过盘古守护境界获取获取攻击力
		"""
		try:
			return self._pDatas[className][realm]["damage"]
		except:
			return -1

	@classmethod
	def instance( SELF ):
		"""
		"""
		if SELF._instance is None:
			SELF._instance = PGNagualConfigMgr()
		return SELF._instance