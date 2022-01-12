# -*- coding: gb18030 -*-
"""
�����ͼ��Ӧ�Ĺ��Ｖ����Ϣ���� 2009-01-12 SongPeifang
"""

from bwdebug import *
import Language

class BigWorldLevelMaps:
	"""
	�����ͼ��Ӧ�Ĺ��Ｖ����Ϣ����
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert BigWorldLevelMaps._instance is None
		self._BigWorldLevelMaps = {} 	# �����ͼ��Ӧ�Ĺ��Ｖ����Ϣ��
		self.load( "config/server/Treasure/BigWorldLevelMaps.xml" )
		BigWorldLevelMaps._instance = self

	@staticmethod
	def instance():
		"""
		"""
		if BigWorldLevelMaps._instance is None:
			BigWorldLevelMaps._instance = BigWorldLevelMaps()
		return BigWorldLevelMaps._instance

	def load( self, configFile ):
		"""
		��ȡ�����ͼ��Ӧ�Ĺ��Ｖ����Ϣ�����ļ�
		"""
		if len( configFile ) <= 0:
			return

		sect = Language.openConfigSection( configFile )
		assert sect is not None, "open %s false." % configFile
		for node in sect.values():
			spaceName = node["spaceName"].asString
			if not self._BigWorldLevelMaps.has_key( spaceName ):
				self._BigWorldLevelMaps[spaceName] = {}
			self._BigWorldLevelMaps[spaceName]["spaceNameCH"] = node["spaceNameCH"].asString
			self._BigWorldLevelMaps[spaceName]["min_monster_level"] = node["min_monster_level"].asInt
			self._BigWorldLevelMaps[spaceName]["max_monster_level"] = node["max_monster_level"].asInt
		# ��ȡ�����رմ򿪵��ļ�
		Language.purgeConfig( configFile )

	def getSpaceNameByLevel( self, level ):
		"""
		���ݼ����õ�ͼ������
		"""
		# Ҫ��һ��Ĭ�ϵĵ�ͼ��������֤�Ҳ�����ͼ��ʱ��Ҳ�ܹ����һ����ͼ
		space = "fengming"
		if len( self._BigWorldLevelMaps ) == 0:
			ERROR_MSG( "Config BigWorldLevelMaps load failed!" )
			return space
		for spaceName, datas in self._BigWorldLevelMaps.iteritems():
			if level >= datas["min_monster_level"] and level <= datas["max_monster_level"]:
				space = spaceName
				break
		return space

g_BigWorldLevelMaps = BigWorldLevelMaps.instance()