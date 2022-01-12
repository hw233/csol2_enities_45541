# -*- coding: gb18030 -*-
from SpawnPointCopy import SpawnPointCopy
import random
import csdefine
import csconst
from bwdebug import *

class SpawnPointPotential( SpawnPointCopy ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPointCopy.initEntity( self, selfEntity  )
		selfEntity.getCurrentSpaceBase().cell.addSpawnPoint( selfEntity.base )

	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		��ȡҪ������entity����
		"""
		args = SpawnPointCopy.getEntityArgs( self, selfEntity, params )
		args[ "level" ] = params.pop( "level", 1 )
		return args
