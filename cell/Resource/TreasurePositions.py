# -*- coding: gb18030 -*-
"""
�����������ݹ��� spf
"""

from bwdebug import *
import Language

class TreasurePositions:
	"""
	�����������ݹ���
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert TreasurePositions._instance is None
		self._treasurePositions = {} 	# ��������ص�����
		self.loadTreasurePos( "config/server/Treasure/TreasureSpawnPoints.xml" )
		TreasurePositions._instance = self

	@staticmethod
	def instance():
		"""
		"""
		if TreasurePositions._instance is None:
			TreasurePositions._instance = TreasurePositions()
		return TreasurePositions._instance
		
	def loadTreasurePos( self, configFile ):
		"""
		��ȡ��������ص������ļ�
		"""
		if len( configFile ) <= 0:
			return
		
		sect = Language.openConfigSection( configFile )
		assert sect is not None, "open %s false." % configFile
		for node in sect.values():
			level = int( node.name )
			mapName = node["map"].asString
			if not self._treasurePositions.has_key( mapName ):
				self._treasurePositions[mapName] = {}
			if not self._treasurePositions[mapName].has_key( level ):
				self._treasurePositions[mapName][level] = []
			self._treasurePositions[mapName][level].append( node["position"].asVector3 )
		# ��ȡ�����رմ򿪵��ļ�
		Language.purgeConfig( configFile )
	
	def getTreasureSpawnPointsLocationList( self, spaceName, level ):
		"""
		���ݵ�ͼ�ͼ����ȡ������б�
		"""
		levelList = self.getTreasureLevelPointsBySpace( spaceName )
		if len( levelList ) == 0:
			INFO_MSG( "�ر�ͼ����û�е�ͼ��Ϊ%s�ĵ�ͼ,��Ĭ�ϲ��ñ��е�һ����ͼ����" % spaceName )
			return self._treasurePositions.values()[0].values()[0]
		if not level in levelList:
			INFO_MSG( "���ڲر�ͼ����û�м���Ϊ%s�ĵ�ͼ,�ʽ����ñ��е�һ������" % level )
			return self._treasurePositions[spaceName].values()[0]
		return self._treasurePositions[spaceName][level]
	
	def getTreasureLevelPointsBySpace( self, spaceName ):
		"""
		���ݵ�ͼ��ȡ��Ӧ�ļ����б�
		"""
		if not self._treasurePositions.has_key( spaceName ):
			return []
		return self._treasurePositions[spaceName].keys()