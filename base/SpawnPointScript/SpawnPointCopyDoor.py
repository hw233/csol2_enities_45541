# -*- coding: gb18030 -*-
import BigWorld
from bwdebug import *
from SpawnPoint import SpawnPoint

class SpawnPointCopyDoor( SpawnPoint ):
	"""
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def initEntityParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化一下参数
		"""
		entityParams = {}
		entityParams[ "useRectangle" ] = params[ "useRectangle" ].asInt
		entityParams[ "radius" ] = params[ "radius" ].asInt
		entityParams[ "volume" ] = params[ "radius" ].asString
		return entityParams
	
	def initTempParams( self, spaceEntity, params ):
		"""
		virtual method.
		初始化参数
		"""
		tempMapping = {}
		tempMapping[ "monsterType" ] = params[ "monsterType" ].asInt
		return tempMapping