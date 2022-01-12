# -*- coding: gb18030 -*-
from SpawnPointCopy import SpawnPointCopy
import random
import csdefine
import csconst
from bwdebug import *

class SpawnPointTongFHLT( SpawnPointCopy ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPointCopy.initEntity( self, selfEntity )
		spaceBaseMB = selfEntity.getCurrentSpaceBase()
		belongTong = selfEntity.getEntityData( "belongTong" )
		spaceBaseMB.cell.addSpawnPoint( selfEntity.base, belongTong )

	def entityDead( self, selfEntity ):
		"""
		Define method.
		��������֪ͨ
		"""
		return
	
	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		��ȡҪ������entity����
		"""
		args = SpawnPointCopy.getEntityArgs( self, selfEntity )
		args[ "ownTongDBID" ] = params[ "tongDBID" ]
		return args