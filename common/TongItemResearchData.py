# -*- coding: gb18030 -*-
#
# $Id: TongItemResearchData.py,v 1.12 2008-07-15 04:21:55 kebiao Exp $

"""
帮会建筑资源加载部分。
"""

import BigWorld
import Language
import csconst
from bwdebug import *
import Function
import time
from config import TongItemResearch

class TongItemResearchData:
	_instance = None
	def __init__( self, configPath = None ):
		"""
		构造函数。
		@param configPath:	技能配置文件路径
		@type  configPath:	string
		"""
		assert TongItemResearchData._instance is None		# 不允许有两个以上的实例
		self._datas = TongItemResearch.serverDatas	# key is BuffTime::_id and value is instance of BuffTime which derive from it.
		self._clientDatas = TongItemResearch.Datas
		TongItemResearchData._instance = self

		#if configPath is not None:
		#	self.load( configPath )

	@staticmethod
	def instance():
		"""
		通过 action id 获取action实例
		"""
		if TongItemResearchData._instance is None:
			TongItemResearchData._instance = TongItemResearchData()
		return TongItemResearchData._instance

	def __getitem__( self, key ):
		"""
		取得Skill实例
		"""
		return self._datas[ key ]

	def getDatas( self ):
		return self._datas

	def getClientDatas( self ):
		return self._clientDatas

def instance():
	return TongItemResearchData.instance()

#
# $Log: not supported by cvs2svn $
#
#
