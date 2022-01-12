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
		һ��������spawnPoint ������ϡ�
		"""
		SpaceCopy.onSpawnPointLoadedOver( self, retCode )
		self.cell.spawnPotentialMonster()
		
	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		��������һ��entity��֪ͨ
		@param	entityType		: entity�Ľű����
		@type 	entityType		: String
		@param	entity			: baseEntityʵ��
		"""
		if entityType == "SpawnPointCopy":
			self.cell.addDarkSpawnPoint( baseEntity )
