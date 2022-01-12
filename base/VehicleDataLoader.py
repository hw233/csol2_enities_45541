# -*- coding: gb18030 -*-
import math
import random
import Const
from bwdebug import *
from config.VehicleProperty import Datas as P_DATA
from config.server.vehicle.VehicleGrowth import Datas as G_DATA
from config.server.vehicle.VehicleGrowthStandard import Datas as S_DATA

class VehicleDataLoader:
	"""
	骑宠属性配置加载
	@ivar _data: 全局数据字典; key is id, value is dict like as {key：[...], ...}
	@type _data: dict
	"""
	_instance = None

	def __init__( self, xmlConf = None ):
		assert VehicleDataLoader._instance is None, "instance already exist in"
		VehicleDataLoader._instance = self

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = VehicleDataLoader()
		return self._instance
		
	def __getGrowthPro( self, growthL ):
		"""
		随机获取成长度值
		"""
		pro = random.random()
		for info in growthL:
			if info[1] < pro <= info[2]:
				return info[0]
		return 0
	
	def getGrowth( self, step, source ):
		"""
		获取成长度
		step：阶次
		source：来源（孵蛋、升阶）
		"""
		if G_DATA.has_key( step ):
			if source == Const.VEHICLE_SOURCE_INCUBATE:
				return self.__getGrowthPro( G_DATA[ step ]["incubate"] )
			elif source == Const.VEHICLE_SOURCE_UP_STEEP_LOW:
				return self.__getGrowthPro( G_DATA[ step ]["low"] )
			elif source == Const.VEHICLE_SOURCE_UP_STEEP_HIGH:
				return self.__getGrowthPro( G_DATA[ step ]["high"] )
		else:
			return 0
		
	def getProperty( self, srcItemID ):
		"""
		通过骑宠对应物品ID获得骑宠相关属性
		"""
		if P_DATA.has_key( srcItemID ):
			pp = P_DATA[srcItemID]
			return  ( pp["level"], pp["step"],pp["fullDegree"],pp["type"] )
		else:
			return ( 1, 1, 0 ,1 )
		
	def getCanUpStep( self, srcItemID ):
		"""
		能否升阶
		"""
		if P_DATA.has_key( srcItemID ):
			return P_DATA[srcItemID]["nextStepItemID"]
		else:
			return 0
		
	def getSIDC( self, level, growth ):
		"""
		获得力量、智力、敏捷、体力
		"""
		if S_DATA.has_key( level ):
			standard = S_DATA[level]["standard"]
			kValue = S_DATA[level]["kValue"]
			v = math.ceil( growth*kValue/standard )
			return ( int(v),int(v),int(v),int(v) )
		else:
			return (0,0,0,0)
		
		