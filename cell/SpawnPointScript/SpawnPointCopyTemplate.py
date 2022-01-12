# -*- coding: gb18030 -*-

"""
副本中怪物出生点类型，服务器启动后不需要直接创建怪物，怪物死亡后不需要复活
"""

import BigWorld
from bwdebug import *
import csdefine
import csconst
import random
from SpawnPointCopy import SpawnPointCopy

class SpawnPointCopyTemplate( SpawnPointCopy ):
	"""
	新副本模板使用的怪物出生点类型,仅用于新副本模板 CopyTemplate 及其子类。
	此类
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPointCopy.initEntity( self, selfEntity )
		try :
			selfEntity.getCurrentSpaceBase().copyTemplate_addSpawnPoint( selfEntity.base, selfEntity.queryTemp( "monsterType", 0 ) )
		except :
			ERROR_MSG( "this SpawnPoint only use new copy 'CopyTemplate' or it's subclass." )

