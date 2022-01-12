# -*- coding: gb18030 -*-

import random
from Function import newUID
from bwdebug import *
import ItemTypeEnum
from ZDDataLoader import DaofaDataLoader
import csconst
g_daofa = DaofaDataLoader.instance()

class CDaoFa:
	"""
	装备基础类
	"""
	def __init__( self, type = 0, level = 1, exp = 0, quality = ItemTypeEnum.CQT_WHITE, order = -1, daoXinID = -1 ):
		self.uid = 0
		self.type = type
		self.level = level
		self.exp = 0
		self.quality = quality
		self.order = order
		self.daoXinID = daoXinID
		self.isLocked = 0

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
		self.initStaticData()
		
	def initStaticData( self ):
		"""
		初始化一些静态数据
		"""
		self.jiyuan = csconst.DAOFA_PRICE[ self.quality ]
		self.name = g_daofa.getName( self.quality, self.type )

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

	def setDaoXinID( self, daoXinID ):
		"""
		设置所在道心ID
		"""
		self.daoXinID = daoXinID

	def getQualityExp( self ):
		"""
		获取品质对应的经验值
		"""
		return csconst.DAOFA_QUALITY_EXP[ self.quality ]

	def addExp( self, exp ):
		"""
		道法增加经验
		"""
		self.exp += exp
		if csconst.DAOFA_UPGRADE_EXP[ self.level ][ self.quality ] != 0 and self.exp >= csconst.DAOFA_UPGRADE_EXP[ self.level ][ self.quality ] :
			self.setLevel( self.level +1  )
	
	def setLevel( self, level ):
		"""
		设置道法等级
		"""
		self.level = level

	def setLock( self , isLock = 0 ):
		"""
		锁定道法
		"""
		self.isLocked = isLock

	def getLockState( self ):
		"""
		是否锁定
		"""
		return self.isLocked

	def getType( self ):
		"""
		道法类型
		"""
		return self.type

	def getName( self ):
		"""
		道法名称
		"""
		return  self.name

	def getExpMax( self ):
		"""
		道法最大经验
		"""
		return csconst.DAOFA_UPGRADE_EXP[ self.level ][ self.quality ]

	def getLevelExp( self ):
		"""
		获得当前等级显示的经验值
		"""
		tempExp = 0
		maxLevel = csconst.DAOFA_MAX_LEVEL[ self.quality ]
		if self.level != maxLevel:
			for level in csconst.DAOFA_UPGRADE_EXP.keys():
				if level < self.level:
					tempExp += csconst.DAOFA_UPGRADE_EXP[ level ][ self.quality ]
			return self.exp - tempExp
		return csconst.DAOFA_UPGRADE_EXP[ self.level -1 ][ self.quality ]
