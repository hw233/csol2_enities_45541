# -*- coding: gb18030 -*-
"""
宝藏数据数据管理 spf
"""

from bwdebug import *
import Language

class TreasurePositions:
	"""
	宝藏数据数据管理
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert TreasurePositions._instance is None
		self._treasurePositions = {} 	# 宝藏随机地点坐标
		self.loadTreasurePos( "config/server/Treasure/TreasureSpawnPoints.xml" )
		TreasurePositions._instance = self

	@staticmethod
	def instance():
		"""
		"""
		if TreasurePositions._instance is None:
			TreasurePositions._instance = TreasurePositions()
		return TreasurePositions._instance
		
	def loadTreasurePos( self, configFile ):
		"""
		读取宝藏随机地点配置文件
		"""
		if len( configFile ) <= 0:
			return
		
		sect = Language.openConfigSection( configFile )
		assert sect is not None, "open %s false." % configFile
		for node in sect.values():
			level = int( node.name )
			mapName = node["map"].asString
			if not self._treasurePositions.has_key( mapName ):
				self._treasurePositions[mapName] = {}
			if not self._treasurePositions[mapName].has_key( level ):
				self._treasurePositions[mapName][level] = []
			self._treasurePositions[mapName][level].append( node["position"].asVector3 )
		# 读取完毕则关闭打开的文件
		Language.purgeConfig( configFile )
	
	def getTreasureSpawnPointsLocationList( self, spaceName, level ):
		"""
		根据地图和级别获取坐标点列表
		"""
		levelList = self.getTreasureLevelPointsBySpace( spaceName )
		if len( levelList ) == 0:
			INFO_MSG( "藏宝图表中没有地图名为%s的地图,将默认采用表中第一个地图名。" % spaceName )
			return self._treasurePositions.values()[0].values()[0]
		if not level in levelList:
			INFO_MSG( "由于藏宝图表中没有级别为%s的地图,故将采用表中第一个级别。" % level )
			return self._treasurePositions[spaceName].values()[0]
		return self._treasurePositions[spaceName][level]
	
	def getTreasureLevelPointsBySpace( self, spaceName ):
		"""
		根据地图获取对应的级别列表
		"""
		if not self._treasurePositions.has_key( spaceName ):
			return []
		return self._treasurePositions[spaceName].keys()