# -*- coding: gb18030 -*-

import Language
from bwdebug import *

class TongRobWarRewardLoader:
	"""
	掠夺战奖励，奖励内容为表格配置
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert TongRobWarRewardLoader._instance is None
		self._datas = {}
		TongRobWarRewardLoader._instance = self

	def load( self, configPath ):
		"""
		加载任务奖励表格
		"""
		section = Language.openConfigSection( configPath )
		assert section is not None, "open %s false." % configPath
		
		for node in section.values():
			level = node.readInt( "level" )
			exp = node.readInt( "exp" )
			
			if level not in self._datas:
				self._datas[level] = {}

			if 'exp' not in self._datas[level]:
				self._datas[level]['exp'] = exp
			
		# 清除缓冲
		Language.purgeConfig( configPath )

	def get( self, level ):
		"""
		获取奖励信息
		"""
		try:
			return self._datas[level]
		except KeyError:
			DEBUG_MSG( "level %i has no reward from table." % ( level ) )
			return {}


	@staticmethod
	def instance():
		"""
		"""
		if TongRobWarRewardLoader._instance is None:
			TongRobWarRewardLoader._instance = TongRobWarRewardLoader()
		return TongRobWarRewardLoader._instance
