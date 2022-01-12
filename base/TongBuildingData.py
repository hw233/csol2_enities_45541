# -*- coding: gb18030 -*-
#
# $Id: TongBuildingData.py,v 1.12 2008-07-15 04:21:55 kebiao Exp $

"""
帮会建筑资源加载部分。
"""

import BigWorld
import Language
import csconst
import csdefine
from bwdebug import *
import Function
import time
from config import TongBuilding
from config import TongBuildingLevel

TONTG_KEY_TO_TYPE_DICT = {
				csdefine.TONG_BUILDING_TYPE_YSDT 	: "ysdt_level" ,	# 议事大厅
				csdefine.TONG_BUILDING_TYPE_JK 		: "jk_level" ,		# 金库
				csdefine.TONG_BUILDING_TYPE_SSD 	: "ssd_level" ,		# 神兽殿
				csdefine.TONG_BUILDING_TYPE_CK 		: "ck_level" ,		# 仓库
				csdefine.TONG_BUILDING_TYPE_TJP 	: "tjp_level" ,		# 铁匠铺
				csdefine.TONG_BUILDING_TYPE_SD 		: "sd_level" ,		# 商店
				csdefine.TONG_BUILDING_TYPE_YJY 	: "yjy_level" ,		# 研究院
}

class TongBuildingData:
	_instance = None
	def __init__( self ):
		"""
		构造函数。
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

class TongBuildingLevelData:
	_instance = None
	def __init__( self ):
		"""
		构造函数。
		"""
		assert TongBuildingLevelData._instance is None		# 不允许有两个以上的实例
		self._datas = TongBuildingLevel.Datas
		TongBuildingLevelData._instance = self

	@staticmethod
	def instance():
		"""
		通过 action id 获取action实例
		"""
		if TongBuildingLevelData._instance is None:
			TongBuildingLevelData._instance = TongBuildingLevelData()
		return TongBuildingLevelData._instance

	def __getitem__( self, level, key ):
		return self._datas[ level ][ key ]
	
	def getBuildingLevel( self, level, key ):
		"""
		取的建筑物等级
		"""
		levelKey = TONTG_KEY_TO_TYPE_DICT[ key ]
		return self._datas[ level ][ levelKey ]

def instance():
	return TongBuildingData.instance()

def tbl_instance():
	return TongBuildingLevelData.instance()

#
# $Log: not supported by cvs2svn $
#
#
