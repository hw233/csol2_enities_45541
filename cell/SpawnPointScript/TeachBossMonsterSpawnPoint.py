# -*- coding:gb18030 -*-

from bwdebug import *
from SpawnPoint import SpawnPoint
from ObjectScripts.GameObjectFactory import g_objFactory

class TeachBossMonsterSpawnPoint( SpawnPoint ):
	"""
	"""
	def entityDead( self, selfEntity ):
		"""
		Define method.
		��������֪ͨ
		"""
		currentSpaceBase = selfEntity.getCurrentSpaceBase()
		if currentSpaceBase is None:
			return
		currentSpaceBase.cell.bossDead( selfEntity.base )		