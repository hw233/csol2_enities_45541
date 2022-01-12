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
		��ʼ������
		"""
		tempMapping = {}
		tempMapping[ "trapRange" ] = params[ "trapRange" ].asInt
		tempMapping[ "pointIndex" ] = params[ "pointIndex" ].asInt
		tempMapping[ "endPoint" ] = params[ "endPoint" ].asInt
		return tempMapping
	
	