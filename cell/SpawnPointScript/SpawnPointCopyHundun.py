# -*- coding: gb18030 -*-

from SpawnPointCopyTemplate import SpawnPointCopyTemplate
import random
from ObjectScripts.GameObjectFactory import g_objFactory

class SpawnPointCopyHundun( SpawnPointCopyTemplate ):
	"""
	"""

	def getEntityArgs( self, selfEntity, params = {} ):
		args = SpawnPointCopyTemplate.getEntityArgs( self, selfEntity, params )
		args[ "className" ] = random.choice( selfEntity.entityName.split( "|" ) )
		return args
	
	def createEntity( self, selfEntity, params = {} ):
		"""
		virtual method.
		通知刷出怪物
		"""
		SpawnPointCopyTemplate.createEntity( self, selfEntity, params )

	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		if selfEntity.getCurrentSpaceBase() == None:
			return
		if selfEntity.getCurrentSpaceBase():
			selfEntity.getCurrentSpaceBase().cell.onConditionChange( {} )