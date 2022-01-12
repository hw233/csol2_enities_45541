# -*- coding: gb18030 -*-

import Language
import random
from bwdebug import *
from csarithmetic import getRandomElement
from config.ZhengDao.ZDTeachGuidData import Datas as guid_data
from config.ZhengDao.DaofaTypeRate import Datas as type_rate
from config.ZhengDao.Daofa import Datas as g_daofa

def roleLevelToDictKey( roleLevel ):
	"""
	将玩家等级转换为字典中的key
	"""
	if roleLevel < 30:
		ERROR_MSG( " Role level is under 30 ")
		level = 0 
	elif roleLevel <= 60:
		level = 1
	else:
		level = 2
	
	return level

class ZDGuidDataLoader:
	"""
	证道系统导师数据加载器
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert ZDGuidDataLoader._instance is None
		self._datas = guid_data
		ZDGuidDataLoader._instance = self

	def getScoreByLevel( self, roleLevel, guideLevel ):
		"""
		根据导师等级得到积分
		
		@return: INT
		"""
		level = roleLevelToDictKey( roleLevel )
		try:
			return self._datas[ level ][guideLevel]["zdScore"]
		except:
			ERROR_MSG( "roleLevel %i, GuidLevel %i has not in table ZDGuidDataLoader." %  ( roleLevel, guideLevel ) )
			return 0

	def getCostJYByLevel( self, roleLevel, guideLevel ):
		"""
		根据导师等级获得所需消耗的机缘
		"""
		level = roleLevelToDictKey( roleLevel )
		try:
			return self._datas[level][guideLevel]["jiyuan"]
		except:
			ERROR_MSG( "roleLevel %i, GuidLevel %i has not in table ZDGuidDataLoader." %  ( roleLevel, guideLevel ) )
			return 0
	
	def getNextGuideActiveRate( self, guideLevel ):
		"""
		根据当前导师等级获得下一个导师激活的几率
		"""
		level = 1
		try:
			return self._datas[ level ][ guideLevel ][ "activeRate" ]
		except KeyError:
			if guideLevel != 0:
				ERROR_MSG( "GuidLevel %i has not in table ZDGuidDataLoader." % guideLevel )
			return 0


	def getQuality( self, roleLevel, guideLevel ):
		"""
		根据玩家、导师等级获得道法品质
		
		@return: INT
		"""
		rate = random.random()
		if roleLevel < 30:
			ERROR_MSG( " Role level is under 30 ")
			return 0
		
		if roleLevel <= 60:
			level = 1
		else:
			level = 2
			
		dict = self._datas[ level ][ guideLevel ][ "qualityRate" ]
		if rate < dict[1]:
			return 1
		elif rate < dict[1] + dict[ 2 ]:
			return 2
		elif rate < dict[1] + dict[ 2 ] + dict[ 3 ]:
			return 3
		elif rate < dict[1] + dict[ 2 ] + dict[ 3 ] + dict[ 4 ]:
			return 4
		else:
			return 5

	@staticmethod
	def instance():
		"""
		"""
		if ZDGuidDataLoader._instance is None:
			ZDGuidDataLoader._instance = ZDGuidDataLoader()
		return ZDGuidDataLoader._instance

class DaofaTypeRateLoader:
	"""
	根据道法的品质获取道法的类型
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert DaofaTypeRateLoader._instance is None
		self._datas = type_rate
		DaofaTypeRateLoader._instance = self

	def getType( self, quality ):
		"""
		根据道法品质获取道法的类型
		
		@return: INT
		"""
		if quality not in self._datas.keys():
			ERROR_MSG( "Quality %i has no type in DaofaTypeRate "  % quality )
			return
		elements = self._datas[ quality ][ "type" ]
		rndOdds = self._datas[ quality ][ "rate" ]
		type = getRandomElement( elements, rndOdds )
		return type

	@staticmethod
	def instance():
		"""
		"""
		if DaofaTypeRateLoader._instance is None:
			DaofaTypeRateLoader._instance = DaofaTypeRateLoader()
		return DaofaTypeRateLoader._instance

class DaofaDataLoader:
	"""
	道法配置数据加载
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert DaofaDataLoader._instance is None
		self._datas = g_daofa
		DaofaDataLoader._instance = self

	def getQuaWhiteType( self ):
		"""
		获取道法类型
		"""
		keys = self._datas[ 1 ].keys()
		type = int( random.choice( keys) ) 
		return type

	def getEffectValue( self, quality, type, level ):
		"""
		附加属性
		"""
		if quality == 1:
			return 0
		return self._datas[ quality ][ type ]["levelData"][ level ]

	def getName( self, quality, type ):
		"""
		获得道法名字
		"""
		if type not in self._datas[ quality ].keys():
			return ""
		return self._datas[ quality ][ type ]["name"]

	def getAllTypeByQuality( self, quality ):
		"""
		获得品质所对应的所有道法类型
		"""
		return self._datas[ quality ].keys()

	@staticmethod
	def instance():
		"""
		"""
		if DaofaDataLoader._instance is None:
			DaofaDataLoader._instance = DaofaDataLoader()
		return DaofaDataLoader._instance

class ZDScoreShopLoader:
	"""
	积分兑换数据加载
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert ZDScoreShopLoader._instance is None
		self.datas = []

	def load( self, xmlConfig ):
		"""
		加载配置
		"""
		section = Language.openConfigSection( xmlConfig )
		if section is None:
			raise SystemError,"cannot load %s." % xmlConfig
		
		for daofa in section.values():
			quality = daofa.readInt( "quality" )
			type = daofa.readInt( "type" )
			score = daofa.readInt( "score" )
			level = daofa.readInt( "level" )
			if daofa in self.datas:
				ERROR_MSG( "daofa ( quality %i, type %i) has already in data."%( quality, type ) )
				continue

			tempDaofa = SpecialDaofa( quality, type, score, level )
			self.datas.append( tempDaofa )

	def getSpecialDaofa( self, quality, type ):
		"""
		获取所需积分
		"""
		for df in self.datas:
			if df.getQuality() == quality and df.getType() == type:
				return df.getDataList()

	@staticmethod
	def instance():
		"""
		"""
		if ZDScoreShopLoader._instance is None:
			ZDScoreShopLoader._instance = ZDScoreShopLoader()
		return ZDScoreShopLoader._instance

g_daofaShop = ZDScoreShopLoader.instance()

class SpecialDaofa:
	"""
	积分兑换商城道法
	"""
	def __init__( self, quality, type, score, level ):
		"""
		"""
		self.quality = quality
		self.type = type
		self.score = score
		self.level = level

	def getDataList( self ):
		"""
		获得物品数据
		"""
		dataList = [ ]
		dataList = [ self.quality, self.type, self.score, self.level ]
		return dataList

	def getScore( self ):
		"""
		积分
		"""
		return self.score

	def getQuality( self ):
		"""
		品质
		"""
		return self.quality

	def getType( self ):
		"""
		类型
		"""
		return self.type

