# -*- coding: gb18030 -*-

from SpawnPoint import SpawnPoint
import BigWorld
import csdefine

class SpawnPointActivityBuff( SpawnPoint ):
	"""
	用于消灭一个地区的怪物后，给予玩家技能
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity  )
		BigWorld.globalData['MonsterActivityManager'].addActivityBuffSpawnPoint( selfEntity.spaceType, selfEntity.base )
		
	def addAreaPlayerBuff( self, selfEntity ):
		"""
		define method
		"""
		if self.buffID == "":
			return		
		for i in self.entitiesInRangeExt( self.buffRange, 'Role' ):
			i.spellTarget( int(self.buffID), i.id )
	
	def entityDead( self, selfEntity ):
		pass

	def createEntity( self, selfEntity, params = {} ):
		"""
		"""
		pass