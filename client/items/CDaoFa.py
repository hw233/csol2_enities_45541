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
	װ��������
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
		self.initStaticData()
		
	def initStaticData( self ):
		"""
		��ʼ��һЩ��̬����
		"""
		self.jiyuan = csconst.DAOFA_PRICE[ self.quality ]
		self.name = g_daofa.getName( self.quality, self.type )

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

	def setDaoXinID( self, daoXinID ):
		"""
		�������ڵ���ID
		"""
		self.daoXinID = daoXinID

	def getQualityExp( self ):
		"""
		��ȡƷ�ʶ�Ӧ�ľ���ֵ
		"""
		return csconst.DAOFA_QUALITY_EXP[ self.quality ]

	def addExp( self, exp ):
		"""
		�������Ӿ���
		"""
		self.exp += exp
		if csconst.DAOFA_UPGRADE_EXP[ self.level ][ self.quality ] != 0 and self.exp >= csconst.DAOFA_UPGRADE_EXP[ self.level ][ self.quality ] :
			self.setLevel( self.level +1  )
	
	def setLevel( self, level ):
		"""
		���õ����ȼ�
		"""
		self.level = level

	def setLock( self , isLock = 0 ):
		"""
		��������
		"""
		self.isLocked = isLock

	def getLockState( self ):
		"""
		�Ƿ�����
		"""
		return self.isLocked

	def getType( self ):
		"""
		��������
		"""
		return self.type

	def getName( self ):
		"""
		��������
		"""
		return  self.name

	def getExpMax( self ):
		"""
		���������
		"""
		return csconst.DAOFA_UPGRADE_EXP[ self.level ][ self.quality ]

	def getLevelExp( self ):
		"""
		��õ�ǰ�ȼ���ʾ�ľ���ֵ
		"""
		tempExp = 0
		maxLevel = csconst.DAOFA_MAX_LEVEL[ self.quality ]
		if self.level != maxLevel:
			for level in csconst.DAOFA_UPGRADE_EXP.keys():
				if level < self.level:
					tempExp += csconst.DAOFA_UPGRADE_EXP[ level ][ self.quality ]
			return self.exp - tempExp
		return csconst.DAOFA_UPGRADE_EXP[ self.level -1 ][ self.quality ]
