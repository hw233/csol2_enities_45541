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
	����ҵȼ�ת��Ϊ�ֵ��е�key
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
	֤��ϵͳ��ʦ���ݼ�����
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert ZDGuidDataLoader._instance is None
		self._datas = guid_data
		ZDGuidDataLoader._instance = self

	def getScoreByLevel( self, roleLevel, guideLevel ):
		"""
		���ݵ�ʦ�ȼ��õ�����
		
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
		���ݵ�ʦ�ȼ�����������ĵĻ�Ե
		"""
		level = roleLevelToDictKey( roleLevel )
		try:
			return self._datas[level][guideLevel]["jiyuan"]
		except:
			ERROR_MSG( "roleLevel %i, GuidLevel %i has not in table ZDGuidDataLoader." %  ( roleLevel, guideLevel ) )
			return 0
	
	def getNextGuideActiveRate( self, guideLevel ):
		"""
		���ݵ�ǰ��ʦ�ȼ������һ����ʦ����ļ���
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
		������ҡ���ʦ�ȼ���õ���Ʒ��
		
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
	���ݵ�����Ʒ�ʻ�ȡ����������
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert DaofaTypeRateLoader._instance is None
		self._datas = type_rate
		DaofaTypeRateLoader._instance = self

	def getType( self, quality ):
		"""
		���ݵ���Ʒ�ʻ�ȡ����������
		
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
	�����������ݼ���
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert DaofaDataLoader._instance is None
		self._datas = g_daofa
		DaofaDataLoader._instance = self

	def getQuaWhiteType( self ):
		"""
		��ȡ��������
		"""
		keys = self._datas[ 1 ].keys()
		type = int( random.choice( keys) ) 
		return type

	def getEffectValue( self, quality, type, level ):
		"""
		��������
		"""
		if quality == 1:
			return 0
		return self._datas[ quality ][ type ]["levelData"][ level ]

	def getName( self, quality, type ):
		"""
		��õ�������
		"""
		if type not in self._datas[ quality ].keys():
			return ""
		return self._datas[ quality ][ type ]["name"]

	def getAllTypeByQuality( self, quality ):
		"""
		���Ʒ������Ӧ�����е�������
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
	���ֶһ����ݼ���
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert ZDScoreShopLoader._instance is None
		self.datas = []

	def load( self, xmlConfig ):
		"""
		��������
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
		��ȡ�������
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
	���ֶһ��̳ǵ���
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
		�����Ʒ����
		"""
		dataList = [ ]
		dataList = [ self.quality, self.type, self.score, self.level ]
		return dataList

	def getScore( self ):
		"""
		����
		"""
		return self.score

	def getQuality( self ):
		"""
		Ʒ��
		"""
		return self.quality

	def getType( self ):
		"""
		����
		"""
		return self.type

