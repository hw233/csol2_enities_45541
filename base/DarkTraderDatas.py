# -*- coding: gb18030 -*-
#
# 2008-12-26 SongPeifang
#
"""
投机商人数据信息存储器
"""

from bwdebug import *
import Language
import random
from config.item.A_DarkTraderDatas import serverDatas as g_serverDatas

class DarkTraderDatas:
	"""
	投机商人数据信息存储器
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert DarkTraderDatas._instance is None
		self._DarkTraderMaps = []	 	# 投机商人地图信息
		self._DarkTraderPositions = {} 	# 投机商人地点信息
		self._DarkTraderDatas = g_serverDatas	# 投机商人商品信息 string:string(物品ID的字符串:物品名称)
		self._currentGoodID = 0			# 投机商人当前收购的物品ID
		self._currentGoodName = ""		# 投机商人当前收购的物品名称
		self.loadDarkTaderPos( "config/server/DarkTraderPoints.xml" )	# 暂时读取宝藏图的坐标位置
		DarkTraderDatas._instance = self

	@staticmethod
	def instance():
		"""
		"""
		if DarkTraderDatas._instance is None:
			DarkTraderDatas._instance = DarkTraderDatas()
		return DarkTraderDatas._instance
		
	def loadDarkTaderPos( self, configFile ):
		"""
		读取投机商人随机地点配置文件
		"""
		if len( configFile ) <= 0:
			return
		
		sect = Language.openConfigSection( configFile )
		assert sect is not None, "open %s false." % configFile
		for node in sect.values():
			mapName = node["map"].asString
			if not mapName in self._DarkTraderMaps:
				self._DarkTraderMaps.append( mapName )
			if not self._DarkTraderPositions.has_key( mapName ):
				self._DarkTraderPositions[mapName] = []
			self._DarkTraderPositions[mapName].append( node["position"].asVector3 )
		# 读取完毕则关闭打开的文件
		Language.purgeConfig( configFile )


	def genCollectGoodID( self, className, spaceName ):
		"""
		生成投机商人当前收购的物品ID
		当前算法为随即算法
		"""
		if not self._DarkTraderDatas.has_key( className ):
			ERROR_MSG( "投机商人数据错误，不存在ID为%s的投机商人NPC!"%className )
			return 0
		if not self._DarkTraderDatas[className].has_key( spaceName ):
			ERROR_MSG( "投机商人数据错误，没有该地图%s的信息!"%spaceName )
			return 0
		iteIDStr = self._DarkTraderDatas[className][spaceName]
		self._currentGoodID = int( iteIDStr )
		self._currentGoodName = self._DarkTraderDatas[className][iteIDStr]