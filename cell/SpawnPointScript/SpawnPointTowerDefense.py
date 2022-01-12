# -*- coding: gb18030 -*-

# $Id: SpawnPointPotential.py,v 1.1 add by hzm $
"""
"""

from SpawnPoint import SpawnPoint
import random
import csdefine
import csconst
from bwdebug import *



class SpawnPointTowerDefense( SpawnPoint ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPoint.initEntity( self, selfEntity  )
		selfEntity.getCurrentSpaceBase().cell.addSpawnPoint( selfEntity.base )

	def onTimer( self, selfEntity, controllerID, userData ):
		"""
		"""
		return
	
	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		获取要创建的entity参数
		"""
		args = SpawnPoint.getEntityArgs( self, selfEntity )
		args[ "level" ] = params[ "level" ]
		return args

	def createEntity( self, selfEntity, params = {} ):
		"""
		define method
		"""
		args = self.getEntityArgs( selfEntity, params )#获取参数
		
		batchNum = params[ "batchNum" ]
		entityNameList = selfEntity.entityName.split(";")
		if batchNum < len( entityNameList ):
			entityName = entityNameList[ batchNum ]
			if entityName and int( entityName ):
				selfEntity.createNPCObject( entityName, selfEntity.position, selfEntity.direction, d )
