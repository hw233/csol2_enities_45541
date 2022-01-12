# -*- coding: gb18030 -*-


"""
�����й��������
"""
import BigWorld
from bwdebug import *

from SpawnPoint import SpawnPoint

class SpawnPointCopy( SpawnPoint ):
	"""
	�����й������������
	"""
	def initEntity( self, selfEntity ):
		if hasattr( selfEntity, "cellData" ):
			selfEntity.className = selfEntity.cellData[ "entityName" ]
			
		SpawnPoint.initEntity( self, selfEntity )
	
	def getEntityType( self ):
		"""
		��ȡSpawnPoint �� Entity Type
		retrun String
		"""
		return "SpawnPointCopy"
		