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
		self.uid = newUID()
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
		levelExp = 0
		tempLevel = 1
		self.exp += exp
		maxExp = self.getMaxExp( self.quality )
		self.exp = min( self.exp, maxExp )
	
		# �ȼ�����
		maxLevel = csconst.DAOFA_MAX_LEVEL[ self.quality ]
		for level in csconst.DAOFA_UPGRADE_EXP.keys():
			if level < maxLevel:
				levelExp +=  csconst.DAOFA_UPGRADE_EXP[ level ][ self.quality ]
				if self.exp >= levelExp:
					tempLevel = level + 1
					continue
		self.setLevel( tempLevel )

	def setLevel( self, level ):
		"""
		���õ����ȼ�
		"""
		self.level = level

	def getLevel( self ):
		"""
		�����ȼ�
		"""
		return self.level

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

	def getExp( self ):
		"""
		��������
		"""
		return self.exp

	def getMaxExp( self, quality ):
		"""
		��������ֵ
		"""
		exp = 0
		for level in csconst.DAOFA_UPGRADE_EXP.keys():
			if csconst.DAOFA_UPGRADE_EXP[ level ][ quality ] != 0:
				exp += csconst.DAOFA_UPGRADE_EXP[ level ][ quality ]
		return exp

	def getName( self ):
		"""
		��������
		"""
		return self.name

