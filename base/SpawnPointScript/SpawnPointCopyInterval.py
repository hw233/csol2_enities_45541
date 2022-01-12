# -*- coding: gb18030 -*-
"""
�����й��������
"""
from SpawnPoint import SpawnPoint

class SpawnPointCopyInterval( SpawnPoint ):
	"""
	�����й�����������ͣ����һ��ʱ�䣬����һ�����ֱ���㹻����
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def initTempParams( self, spaceEntity, params ):
		"""
		virtual method.
		��ʼ������
		"""
		tempMapping = {}
		tempMapping[ "spawnNum" ] = params[ "spawnNum" ].asInt
		tempMapping[ "intervalTime" ] = params[ "intervalTime" ].asInt
		return tempMapping