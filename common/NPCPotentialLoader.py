# -*- coding: gb18030 -*-

# $Id: NPCPotentialLoader.py,v 1.2 2009-9-23 06:40:31 kebiao Exp $

import Language
from bwdebug import *
from config import npc_potential

class NPCPotentialLoader:
	"""
	怪物潜能配置加载器
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert NPCPotentialLoader._instance is None
		# key == 对应的怪物等级
		# value == 在该等级下玩家能获得的经验
		self._datas = npc_potential.Datas
		NPCPotentialLoader._instance = self

	def get( self, level ):
		"""
		根据等取得对应的经验值
		
		@return: INT
		"""
		try:
			return self._datas[level]
		except KeyError:
			if level != 0:
				printStackTrace()
				ERROR_MSG( "level %i has not in table." % level )
			return 0

	@staticmethod
	def instance():
		"""
		"""
		if NPCPotentialLoader._instance is None:
			NPCPotentialLoader._instance = NPCPotentialLoader()
		return NPCPotentialLoader._instance


