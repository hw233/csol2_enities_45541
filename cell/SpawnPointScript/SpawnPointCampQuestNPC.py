# -*- coding: gb18030 -*-

import random
import csdefine
import csconst
from SpawnPoint import SpawnPoint

class SpawnPointCampQuestNPC( SpawnPoint ):
	"""
	��Ӫ�ݵ�����NPCˢ�µ�: ����NPC��Ҫ����base
	"""
	def createEntity( self, selfEntity, params = {} ):
		"""
		"""
		args = self.getEntityArgs( selfEntity, params )
		selfEntity.base.createNPCObject( selfEntity, selfEntity.entityName, selfEntity.position, selfEntity.direction, args )