# -*- coding: gb18030 -*-
from SpawnPoint import SpawnPoint
import BigWorld
import csdefine

class SpawnPointActivity( SpawnPoint ):
	"""
	��������һ�������Ĺ���󣬸�����Ҽ���
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def onActivityEnd( self, selfEntity ):
		"""
		�����
		"""
		pass