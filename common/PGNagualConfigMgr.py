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
	�̹��ػ���Ӧ���ݼ�����
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
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
		ͨ���̹��ػ���������Ӧ������ֵ
		"""
		try:
			return self._pDatas[className][realm]["HP"]
		except:
			return -1

	def getAttackType( self, className, realm ):
		"""
		ͨ���̹��ػ������ȡ��ȡ��������
		"""
		try:
			return self._pDatas[className][realm]["attackType"]
		except:
			return -1

	def getDamage( self, className, realm ):
		"""
		ͨ���̹��ػ������ȡ��ȡ������
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