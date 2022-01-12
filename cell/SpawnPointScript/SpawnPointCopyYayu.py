# -*- coding: gb18030 -*-

from SpawnPointCopy import SpawnPointCopy
from ObjectScripts.GameObjectFactory import g_objFactory

class SpawnPointCopyYayu( SpawnPointCopy ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPointCopy.initEntity( self, selfEntity )
		selfEntity.getCurrentSpaceBase().addSpawnPointYayu( selfEntity.base, selfEntity.queryTemp( "monsterType", 0 ) )

	def entityDead( self, selfEntity ):
		"""
		Define method.
		��������֪ͨ
		"""
		if selfEntity.getCurrentSpaceBase() == None:
			return
		if selfEntity.getCurrentSpaceBase() and selfEntity.queryTemp( "monsterType", 0 ) == 0:
			selfEntity.getCurrentSpaceBase().cell.onYayuDie()

	def createEntity( self, selfEntity, params = {} ):
		"""
		"""
		args = self.getEntityArgs( selfEntity, params )
		entity = g_objFactory.getObject( selfEntity.entityName ).createEntity( selfEntity.spaceID, selfEntity.position, selfEntity.direction, args )
		if selfEntity.queryTemp( "monsterType", 0 ) == 0:	# �m؅
			entity.viewRange =  200
			entity.territory = 200
			selfEntity.getCurrentSpaceBase().cell.onConditionChange( { "yayuID": entity.id } )