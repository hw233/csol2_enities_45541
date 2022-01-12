# -*- coding: gb18030 -*-


"""
副本中怪物出生点
"""
import BigWorld
from bwdebug import *

from SpawnPoint import SpawnPoint

class SpawnPointCopy( SpawnPoint ):
	"""
	副本中怪物出生点类型
	"""
	def initEntity( self, selfEntity ):
		if hasattr( selfEntity, "cellData" ):
			selfEntity.className = selfEntity.cellData[ "entityName" ]
			
		SpawnPoint.initEntity( self, selfEntity )
	
	def getEntityType( self ):
		"""
		获取SpawnPoint 的 Entity Type
		retrun String
		"""
		return "SpawnPointCopy"
		