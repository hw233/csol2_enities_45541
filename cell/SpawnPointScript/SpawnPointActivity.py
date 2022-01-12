# -*- coding: gb18030 -*-
from SpawnPoint import SpawnPoint
import BigWorld
import csdefine

class SpawnPointActivity( SpawnPoint ):
	"""
	用于消灭一个地区的怪物后，给予玩家技能
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def onActivityEnd( self, selfEntity ):
		"""
		活动结束
		"""
		pass