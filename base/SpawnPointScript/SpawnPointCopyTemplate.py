# -*- coding: gb18030 -*-


"""
�����й��������
"""
import BigWorld
from bwdebug import *

from SpawnPointCopy import SpawnPointCopy

class SpawnPointCopyTemplate( SpawnPointCopy ):
	"""
	�����й������������
	"""
	def initEntity( self, selfEntity ):
		if hasattr( selfEntity, "cellData" ):
			selfEntity.className = selfEntity.cellData[ "entityName" ]
			
		SpawnPointCopy.initEntity( self, selfEntity )
	
	def initTempParams( self, spaceEntity, params ):
		"""
		virtual method.
		��ʼ������
		"""
		tempMapping = {}
		tempMapping[ "monsterType" ] = params[ "monsterType" ].asInt
		return tempMapping
	