# -*- coding: gb18030 -*-

# $Id: MonsterDaohengLoader.py 

import Language
from bwdebug import *
from config import MonsterDaoheng 

class MonsterDaohengLoader:
	"""
	�����ɱ�����������ü�����
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert MonsterDaohengLoader._instance is None
		# key == ��Ӧ�Ĺ���ȼ�
		# value == �ڸõȼ�������ܻ�õĵ���
		self._datas = MonsterDaoheng.Datas
		MonsterDaohengLoader._instance = self

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
			return 0

	@staticmethod
	def instance():
		"""
		"""
		if MonsterDaohengLoader._instance is None:
			MonsterDaohengLoader._instance = MonsterDaohengLoader()
		return MonsterDaohengLoader._instance


#
# $Log: not supported by cvs2svn $
# no message
#
#