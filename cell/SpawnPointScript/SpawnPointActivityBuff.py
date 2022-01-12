# -*- coding: gb18030 -*-

from SpawnPoint import SpawnPoint
import BigWorld
import csdefine

class SpawnPointActivityBuff( SpawnPoint ):
	"""
	��������һ�������Ĺ���󣬸�����Ҽ���
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