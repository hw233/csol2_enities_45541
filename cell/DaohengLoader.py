# -*- coding: gb18030 -*-

# $Id: DaohengLoader.py

import Language
from bwdebug import *
from config.server.Daoheng import Datas                  # 标准道行

class DaohengLoader:
	"""
	道行配置加载器
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert DaohengLoader._instance is None
		# key == 对应的怪物等级
		# value == 在该等级下玩家能获得的道行
		self._datas = Datas
		DaohengLoader._instance = self

	def get( self, level ):
		"""
		根据等取得对应的道行值
		
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
