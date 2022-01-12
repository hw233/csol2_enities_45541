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
	����������ü���
	@ivar _data: ȫ�������ֵ�; key is id, value is dict like as {key��[...], ...}
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
		�����ȡ�ɳ���ֵ
		"""
		pro = random.random()
		for info in growthL:
			if info[1] < pro <= info[2]:
				return info[0]
		return 0
	
	def getGrowth( self, step, source ):
		"""
		��ȡ�ɳ���
		step���״�
		source����Դ�����������ף�
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
		ͨ������Ӧ��ƷID�������������
		"""
		if P_DATA.has_key( srcItemID ):
			pp = P_DATA[srcItemID]
			return  ( pp["level"], pp["step"],pp["fullDegree"],pp["type"] )
		else:
			return ( 1, 1, 0 ,1 )
		
	def getCanUpStep( self, srcItemID ):
		"""
		�ܷ�����
		"""
		if P_DATA.has_key( srcItemID ):
			return P_DATA[srcItemID]["nextStepItemID"]
		else:
			return 0
		
	def getSIDC( self, level, growth ):
		"""
		������������������ݡ�����
		"""
		if S_DATA.has_key( level ):
			standard = S_DATA[level]["standard"]
			kValue = S_DATA[level]["kValue"]
			v = math.ceil( growth*kValue/standard )
			return ( int(v),int(v),int(v),int(v) )
		else:
			return (0,0,0,0)
		
		