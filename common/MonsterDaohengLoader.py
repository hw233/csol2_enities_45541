# -*- coding: gb18030 -*-

# $Id: MonsterDaohengLoader.py 

import Language
from bwdebug import *
from config import MonsterDaoheng 

class MonsterDaohengLoader:
	"""
	怪物击杀奖励道行配置加载器
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert MonsterDaohengLoader._instance is None
		# key == 对应的怪物等级
		# value == 在该等级下玩家能获得的道行
		self._datas = MonsterDaoheng.Datas
		MonsterDaohengLoader._instance = self

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