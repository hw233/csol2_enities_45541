# -*- coding: gb18030 -*-


"""
副本中怪物出生点
"""
import BigWorld
from bwdebug import *

from SpawnPointCopy import SpawnPointCopy

class SpawnPointCopyTemplate( SpawnPointCopy ):
	"""
	副本中怪物出生点类型
	"""
	def initEntity( self, selfEntity ):
		if hasattr( selfEntity, "cellData" ):
			selfEntity.className = selfEntity.cellData[ "entityName" ]
			
		SpawnPointCopy.initEntity( self, selfEntity )
	
	def initTempParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化参数
		"""
		tempMapping = {}
		tempMapping[ "monsterType" ] = params[ "monsterType" ].asInt
		return tempMapping
	