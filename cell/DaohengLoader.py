# -*- coding: gb18030 -*-

# $Id: DaohengLoader.py

import Language
from bwdebug import *
from config.server.Daoheng import Datas                  # ��׼����

class DaohengLoader:
	"""
	�������ü�����
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert DaohengLoader._instance is None
		# key == ��Ӧ�Ĺ���ȼ�
		# value == �ڸõȼ�������ܻ�õĵ���
		self._datas = Datas
		DaohengLoader._instance = self

	def get( self, level ):
		"""
		���ݵ�ȡ�ö�Ӧ�ĵ���ֵ
		
		@return: INT
		"""
		try:
			return self._datas[level]
		except KeyError:
			if level != 0:
				ERROR_MSG( "level %i has not in table." % level )
			return 1.0

	@staticmethod
	def instance():
		"""
		"""
		if DaohengLoader._instance is None:
			DaohengLoader._instance = DaohengLoader()
		return DaohengLoader._instance
