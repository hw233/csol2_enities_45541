# -*- coding: gb18030 -*-
#
# $Id: TongBuildingData.py,v 1.12 2008-07-15 04:21:55 kebiao Exp $

"""
技能资源加载部分。
"""

import BigWorld
import Language
import csconst
from bwdebug import *
import Function
import time
from config import TongBuilding

class TongBuildingData:
	_instance = None
	def __init__( self ):
		"""
		构造函数。
		@param configPath:	技能配置文件路径
		@type  configPath:	string
		"""
		assert TongBuildingData._instance is None		# 不允许有两个以上的实例
		self._datas = TongBuilding.Datas	# key is BuffTime::_id and value is instance of BuffTime which derive from it.
		TongBuildingData._instance = self

	@staticmethod
	def instance():
		"""
		通过 action id 获取action实例
		"""
		if TongBuildingData._instance is None:
			TongBuildingData._instance = TongBuildingData()
		return TongBuildingData._instance

	def __getitem__( self, key ):
		"""
		取得Skill实例
		"""
		return self._datas[ key ]
		
	
	def getDatas( self ):
		return self._datas

def instance():
	return TongBuildingData.instance()

#
# $Log: not supported by cvs2svn $
#
#
