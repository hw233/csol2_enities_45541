# -*- coding: gb18030 -*-
#
# 2008-12-26 SongPeifang
#
"""
Ͷ������������Ϣ�洢��
"""

from bwdebug import *
import Language
import random
from config.item.A_DarkTraderDatas import serverDatas as g_serverDatas

class DarkTraderDatas:
	"""
	Ͷ������������Ϣ�洢��
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert DarkTraderDatas._instance is None
		self._DarkTraderMaps = []	 	# Ͷ�����˵�ͼ��Ϣ
		self._DarkTraderPositions = {} 	# Ͷ�����˵ص���Ϣ
		self._DarkTraderDatas = g_serverDatas	# Ͷ��������Ʒ��Ϣ string:string(��ƷID���ַ���:��Ʒ����)
		self._currentGoodID = 0			# Ͷ�����˵�ǰ�չ�����ƷID
		self._currentGoodName = ""		# Ͷ�����˵�ǰ�չ�����Ʒ����
		self.loadDarkTaderPos( "config/server/DarkTraderPoints.xml" )	# ��ʱ��ȡ����ͼ������λ��
		DarkTraderDatas._instance = self

	@staticmethod
	def instance():
		"""
		"""
		if DarkTraderDatas._instance is None:
			DarkTraderDatas._instance = DarkTraderDatas()
		return DarkTraderDatas._instance
		
	def loadDarkTaderPos( self, configFile ):
		"""
		��ȡͶ����������ص������ļ�
		"""
		if len( configFile ) <= 0:
			return
		
		sect = Language.openConfigSection( configFile )
		assert sect is not None, "open %s false." % configFile
		for node in sect.values():
			mapName = node["map"].asString
			if not mapName in self._DarkTraderMaps:
				self._DarkTraderMaps.append( mapName )
			if not self._DarkTraderPositions.has_key( mapName ):
				self._DarkTraderPositions[mapName] = []
			self._DarkTraderPositions[mapName].append( node["position"].asVector3 )
		# ��ȡ�����رմ򿪵��ļ�
		Language.purgeConfig( configFile )


	def genCollectGoodID( self, className, spaceName ):
		"""
		����Ͷ�����˵�ǰ�չ�����ƷID
		��ǰ�㷨Ϊ�漴�㷨
		"""
		if not self._DarkTraderDatas.has_key( className ):
			ERROR_MSG( "Ͷ���������ݴ��󣬲�����IDΪ%s��Ͷ������NPC!"%className )
			return 0
		if not self._DarkTraderDatas[className].has_key( spaceName ):
			ERROR_MSG( "Ͷ���������ݴ���û�иõ�ͼ%s����Ϣ!"%spaceName )
			return 0
		iteIDStr = self._DarkTraderDatas[className][spaceName]
		self._currentGoodID = int( iteIDStr )
		self._currentGoodName = self._DarkTraderDatas[className][iteIDStr]