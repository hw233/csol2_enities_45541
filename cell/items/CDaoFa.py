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
	����������
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
		��ʼ����������
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
		���ö�̬����ʱ����
		"""
		self.tmpExtra[attrName] = value

	def queryTemp( self, attrName, default = None ):
		"""
		��ȡһ����ʱ����
		"""
		if attrName in self.tmpExtra:
			return self.tmpExtra[attrName]
		return default

	def popTemp( self, attrName, default = None ):
		"""
		ȡ��һ����ʱ����
		"""
		return self.tmpExtra.pop( attrName, default )

	def initStaticData( self ):
		"""
		��ʼ��һЩ��̬����
		"""
		self.jiyuan = self.quality * 100

	def getJiYuan( self ):
		"""
		��õ�����Ӧ�Ļ�Եֵ
		"""
		return self.jiyuan

	def getUID( self ):
		"""
		��ȡ������UID
		"""
		return self.uid
	
	def getOrder( self ):
		"""
		��ȡ�������ڵĸ��Ӻ�
		"""
		return self.order
		
	def getDaoXinID( self ):
		"""
		��ȡ���ڵ���ID
		"""
		return self.daoXinID

	def getQuality( self ):
		"""
		��ȡƷ��
		"""
		return self.quality

	def setOrder( self, order ):
		"""
		��������λ��
		"""
		self.order = order
		
	def setDaoXinID( self, daoXinID ):
		"""
		�������ڵ���ID
		"""
		self.daoXinID = daoXinID

	def wield( self, owner):
		"""
		װ����������
		"""
		effectClass = g_equipEffect.getEffect( self.type )
		value = g_daofaData.getEffectValue( self.quality, self.type,  self.level )
		if value != 0:
			effectClass.attach( owner, value, self  )
			owner.calcDynamicProperties()

	def unwield( self, owner ):
		"""
		ж�ص�������
		"""
		effectClass = g_equipEffect.getEffect( self.type )
		value = g_daofaData.getEffectValue(  self.quality, self.type, self.level )
		if value != 0:
			effectClass.detach( owner, value, self  )
			owner.calcDynamicProperties()