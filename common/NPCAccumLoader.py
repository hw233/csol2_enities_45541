# -*- coding: gb18030 -*-

# NPCAccumLoader.py, 2012-09-06  added by dqh

import Language
from bwdebug import *
from config import npc_accum

class NPCAccumLoader:
	"""
	怪物气运值配置加载器
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert NPCAccumLoader._instance is None
		# key == 对应的怪物等级
		# value == 在该等级下玩家能获得的气运值
		self._datas = npc_accum.Datas
		NPCAccumLoader._instance = self

	def get( self, level ):
		"""
		根据等级取得对应气运值
		
		@return: INT
		"""
		try:
			return self._datas[level]
		except KeyError:
			if level != 0:
				ERROR_MSG( "Level %i has not in table npc_accum." % level )
			return 0

	@staticmethod
	def instance():
		"""
		"""
		if NPCAccumLoader._instance is None:
			NPCAccumLoader._instance = NPCAccumLoader()
		return NPCAccumLoader._instance
