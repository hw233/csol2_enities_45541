# -*- coding: gb18030 -*-
#
# $Id: MonsterIntensifyPropertyData.py,v 1.12 2008-07-15 04:21:55 kebiao Exp $

"""
帮会建筑资源加载部分。
"""

import BigWorld
import Language
from bwdebug import *
import Function
import time
from   config.server import MonsterIntensifyProperty

class MonsterIntensifyPropertyData:
	_instance = None
	def __init__( self ):
		"""
		构造函数。
		@param configPath:	技能配置文件路径
		@type  configPath:	string
		"""
		assert MonsterIntensifyPropertyData._instance is None		# 不允许有两个以上的实例
		self._datas = MonsterIntensifyProperty.Datas	# key is BuffTime::_id and value is instance of BuffTime which derive from it.
		MonsterIntensifyPropertyData._instance = self

	@staticmethod
	def instance():
		"""
		通过 action id 获取action实例
		"""
		if MonsterIntensifyPropertyData._instance is None:
			MonsterIntensifyPropertyData._instance = MonsterIntensifyPropertyData()
		return MonsterIntensifyPropertyData._instance

	def __getitem__( self, key ):
		"""
		取得Skill实例
		"""
		return self._datas[ key ]

	def getAttrs( self, id, level ):
		if not id in self._datas:
			return None
		onlyLevelList = []	# 唯一等级
		manyLevelList = []	# 等级区间
		for key in self._datas[ id ].keys():
			try:
				levelRange = eval( key )	# 等级区间
				if levelRange[0] == levelRange[1]:
					onlyLevelList.append( key )
				else:
					manyLevelList.append( key )
			except:
				ERROR_MSG( "MonsterIntensifyProperty config is wrong! id(%s),level(%s)" % ( id, key ) )
				continue

		for onlyLevel in onlyLevelList:
			ol = eval( onlyLevel )
			if level >= ol[0] and level <= ol[1]:
				return self._datas[ id ][ onlyLevel ]
		for manyLevel in manyLevelList:
			ml = eval( manyLevel )
			if level >= ml[0] and level <= ml[1]:
				return self._datas[ id ][ manyLevel ]
		return None

	def getAttr( self, id, level, attr ):
		if not id in self._datas:
			return None
		onlyLevelList = []	# 唯一等级
		manyLevelList = []	# 等级区间
		for key in self._datas[ id ].keys():
			try:
				levelRange = eval( key )	# 等级区间
				if levelRange[0] == levelRange[1]:
					onlyLevelList.append( key )
				else:
					manyLevelList.append( key )
			except:
				ERROR_MSG( "MonsterIntensifyProperty config is wrong! id(%s),level(%s)" % ( id, key ) )
				continue

		for onlyLevel in onlyLevelList:
			ol = eval( onlyLevel )
			if level >= ol[0] and level <= ol[1]:
				if attr in self._datas[ id ][ onlyLevel ]:
					return self._datas[ id ][ onlyLevel ][ attr ]
		for manyLevel in manyLevelList:
			ml = eval( manyLevel )
			if level >= ml[0] and level <= ml[1]:
				if attr in self._datas[ id ][ manyLevel ]:
					return self._datas[ id ][ manyLevel ][ attr ]
		return None

def instance():
	return MonsterIntensifyPropertyData.instance()

#
# $Log: not supported by cvs2svn $
#
#
