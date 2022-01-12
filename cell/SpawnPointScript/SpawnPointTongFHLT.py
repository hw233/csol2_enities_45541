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
		怪物死亡通知
		"""
		return
	
	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		获取要创建的entity参数
		"""
		args = SpawnPointCopy.getEntityArgs( self, selfEntity )
		args[ "ownTongDBID" ] = params[ "tongDBID" ]
		return args