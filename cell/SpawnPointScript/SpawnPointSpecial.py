# -*- coding: gb18030 -*-
from SpawnPoint import SpawnPoint
import BigWorld
import csdefine

class SpawnPointSpecial( SpawnPoint ):
	"""
	��������һ�������Ĺ���󣬸�����Ҽ���
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )