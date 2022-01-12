# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from SpawnPoint import SpawnPoint

class SpawnPointRoadPoint( SpawnPoint ):
	"""
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def initTempParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化参数
		"""
		tempMapping = {}
		tempMapping[ "trapRange" ] = params[ "trapRange" ].asInt
		tempMapping[ "pointIndex" ] = params[ "pointIndex" ].asInt
		tempMapping[ "endPoint" ] = params[ "endPoint" ].asInt
		return tempMapping
	
	