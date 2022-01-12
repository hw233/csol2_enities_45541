# -*- coding: gb18030 -*-
"""
世界地图对应的怪物级别信息加载 2009-01-12 SongPeifang
"""

from bwdebug import *
import Language

class BigWorldLevelMaps:
	"""
	世界地图对应的怪物级别信息加载
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert BigWorldLevelMaps._instance is None
		self._BigWorldLevelMaps = {} 	# 世界地图对应的怪物级别信息表
		self.load( "config/server/Treasure/BigWorldLevelMaps.xml" )
		BigWorldLevelMaps._instance = self

	@staticmethod
	def instance():
		"""
		"""
		if BigWorldLevelMaps._instance is None:
			BigWorldLevelMaps._instance = BigWorldLevelMaps()
		return BigWorldLevelMaps._instance

	def load( self, configFile ):
		"""
		读取世界地图对应的怪物级别信息配置文件
		"""
		if len( configFile ) <= 0:
			return

		sect = Language.openConfigSection( configFile )
		assert sect is not None, "open %s false." % configFile
		for node in sect.values():
			spaceName = node["spaceName"].asString
			if not self._BigWorldLevelMaps.has_key( spaceName ):
				self._BigWorldLevelMaps[spaceName] = {}
			self._BigWorldLevelMaps[spaceName]["spaceNameCH"] = node["spaceNameCH"].asString
			self._BigWorldLevelMaps[spaceName]["min_monster_level"] = node["min_monster_level"].asInt
			self._BigWorldLevelMaps[spaceName]["max_monster_level"] = node["max_monster_level"].asInt
		# 读取完毕则关闭打开的文件
		Language.purgeConfig( configFile )

	def getSpaceNameByLevel( self, level ):
		"""
		根据级别获得地图的名字
		"""
		# 要有一个默认的地图凤鸣，保证找不到地图的时候也能够获得一个地图
		space = "fengming"
		if len( self._BigWorldLevelMaps ) == 0:
			ERROR_MSG( "Config BigWorldLevelMaps load failed!" )
			return space
		for spaceName, datas in self._BigWorldLevelMaps.iteritems():
			if level >= datas["min_monster_level"] and level <= datas["max_monster_level"]:
				space = spaceName
				break
		return space

g_BigWorldLevelMaps = BigWorldLevelMaps.instance()