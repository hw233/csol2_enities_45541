# -*- coding: gb18030 -*-
import BigWorld
from bwdebug import *
from SpawnPoint import SpawnPoint

class SpawnPointTrap( SpawnPoint ):
	"""
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
	
	def initEntityParams( self, spaceEntity, params ):
		"""
		virtual method.
		��ʼ��һ�²���
		"""
		entityParams = {}
		entityParams[ "trapRange" ] = params[ "trapRange" ].asInt
		return entityParams
	