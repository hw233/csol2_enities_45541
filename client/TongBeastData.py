# -*- coding: gb18030 -*-
#
# $Id: TongBeastData.py

"""
帮会神兽信息加载部分。
"""

import BigWorld
import Language
import csconst
from bwdebug import *
import Function
import time
from config.client import BeastAttr

class TongBeastData:
	_instance = None
	def __init__( self ):
		"""
		构造函数。
		@param configPath:	技能配置文件路径
		@type  configPath:	string
		"""
		assert TongBeastData._instance is None		# 不允许有两个以上的实例
		self._datas = BeastAttr.Datas	# key is BuffTime::_id and value is instance of BuffTime which derive from it.
		TongBeastData._instance = self

	@staticmethod
	def instance():
		"""
		通过 action id 获取action实例
		"""
		if TongBeastData._instance is None:
			TongBeastData._instance = TongBeastData()
		return TongBeastData._instance

	def __getitem__( self, key ):
		"""
		取得实例
		"""
		return self._datas[ key ]
	
	def getDatas( self ):
		return self._datas

def instance():
	return TongBeastData.instance()

#
# $Log: not supported by cvs2svn $
#
#
