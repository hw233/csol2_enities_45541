# -*- coding: gb18030 -*-

import random
import csdefine
import csconst
from SpawnPoint import SpawnPoint

class SpawnPointCampQuestNPC( SpawnPoint ):
	"""
	阵营据点任务NPC刷新点: 任务NPC需要创建base
	"""
	def createEntity( self, selfEntity, params = {} ):
		"""
		"""
		args = self.getEntityArgs( selfEntity, params )
		selfEntity.base.createNPCObject( selfEntity, selfEntity.entityName, selfEntity.position, selfEntity.direction, args )