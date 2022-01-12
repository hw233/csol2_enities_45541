# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
import Love3
import Const
from bwdebug import *

class SpaceCopyPotential( SpaceCopy ):
	"""
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		self.monsterTotalCount = 0
		self.spawnPointMBList = []

	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		一个副本的spawnPoint 加载完毕。
		"""
		SpaceCopy.onSpawnPointLoadedOver( self, retCode )
		self.cell.spawnPotentialMonster()
		
	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		创建好了一个entity的通知
		@param	entityType		: entity的脚本类别
		@type 	entityType		: String
		@param	entity			: baseEntity实体
		"""
		if entityType == "SpawnPointCopy":
			self.cell.addDarkSpawnPoint( baseEntity )
