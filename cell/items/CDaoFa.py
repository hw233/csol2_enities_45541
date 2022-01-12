# -*- coding: gb18030 -*-

import random
from Function import newUID
from bwdebug import *
import ItemTypeEnum
from ZDDataLoader import *
from EquipEffectLoader import EquipEffectLoader

g_equipEffect = EquipEffectLoader.instance()
g_daofaData = DaofaDataLoader.instance()

class CDaoFa:
	"""
	道法基础类
	"""
	def __init__( self, type = 0, level = 1, exp = 0, quality = ItemTypeEnum.CQT_WHITE, order = -1, daoXinID = -1, isLocked = 0 ):
		self.uid = newUID()
		self.type = type
		self.level = level
		self.exp = 0
		self.quality = quality
		self.order = order
		self.daoXinID = daoXinID
		self.isLocked = isLocked
		self.tmpExtra = {}

	def initData( self, dict ):
		"""
		初始化道法数据
		"""
		self.uid = dict[ "uid" ]
		self.type = dict[ "type" ]
		self.level = dict[ "level" ]
		self.exp = dict[ "exp" ]
		self.quality = dict[ "quality" ]
		self.order = dict[ "order" ]
		self.daoXinID = dict[ "daoXinID" ]
		self.isLocked = dict[ "isLocked" ]
		self.tmpExtra = {}
		self.initStaticData()

	def setTemp( self, attrName, value, owner = None ):
		"""
		设置动态的临时数据
		"""
		self.tmpExtra[attrName] = value

	def queryTemp( self, attrName, default = None ):
		"""
		获取一个临时数据
		"""
		if attrName in self.tmpExtra:
			return self.tmpExtra[attrName]
		return default

	def popTemp( self, attrName, default = None ):
		"""
		取出一个临时数据
		"""
		return self.tmpExtra.pop( attrName, default )

	def initStaticData( self ):
		"""
		初始化一些静态数据
		"""
		self.jiyuan = self.quality * 100

	def getJiYuan( self ):
		"""
		获得道法对应的机缘值
		"""
		return self.jiyuan

	def getUID( self ):
		"""
		获取道法的UID
		"""
		return self.uid
	
	def getOrder( self ):
		"""
		获取道法所在的格子号
		"""
		return self.order
		
	def getDaoXinID( self ):
		"""
		获取所在道心ID
		"""
		return self.daoXinID

	def getQuality( self ):
		"""
		获取品质
		"""
		return self.quality

	def setOrder( self, order ):
		"""
		设置所在位置
		"""
		self.order = order
		
	def setDaoXinID( self, daoXinID ):
		"""
		设置所在道心ID
		"""
		self.daoXinID = daoXinID

	def wield( self, owner):
		"""
		装备道法属性
		"""
		effectClass = g_equipEffect.getEffect( self.type )
		value = g_daofaData.getEffectValue( self.quality, self.type,  self.level )
		if value != 0:
			effectClass.attach( owner, value, self  )
			owner.calcDynamicProperties()

	def unwield( self, owner ):
		"""
		卸载道法属性
		"""
		effectClass = g_equipEffect.getEffect( self.type )
		value = g_daofaData.getEffectValue(  self.quality, self.type, self.level )
		if value != 0:
			effectClass.detach( owner, value, self  )
			owner.calcDynamicProperties()