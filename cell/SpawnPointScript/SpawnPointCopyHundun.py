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
		֪ͨˢ������
		"""
		SpawnPointCopyTemplate.createEntity( self, selfEntity, params )

	def entityDead( self, selfEntity ):
		"""
		Define method.
		��������֪ͨ
		"""
		if selfEntity.getCurrentSpaceBase() == None:
			return
		if selfEntity.getCurrentSpaceBase():
			selfEntity.getCurrentSpaceBase().cell.onConditionChange( {} )