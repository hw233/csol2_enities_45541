# -*- coding: gb18030 -*-

# $Id: NPCExpLoader.py,v 1.2 2007-11-23 06:40:31 phw Exp $

import Language
from bwdebug import *
from config import npc_exp

class NPCExpLoader:
	"""
	怪物经验配置加载器
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert NPCExpLoader._instance is None
		# key == 对应的怪物等级
		# value == 在该等级下玩家能获得的经验
		self._datas = npc_exp.Datas
		NPCExpLoader._instance = self

	def get( self, level ):
		"""
		根据等取得对应的经验值
		
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
		if NPCExpLoader._instance is None:
			NPCExpLoader._instance = NPCExpLoader()
		return NPCExpLoader._instance


#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/11/17 03:10:09  phw
# no message
#
#