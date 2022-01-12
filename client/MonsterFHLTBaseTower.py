# -*- coding: gb18030 -*-

from MonsterBuilding import MonsterBuilding
import csdefine
from bwdebug import *

class MonsterFHLTBaseTower( MonsterBuilding ):
	def __init__( self ):
		MonsterBuilding.__init__( self )
	
	def queryRelation( self, entity ):
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return MonsterBuilding.queryRelation( self, entity )
		
		if entity.isEntityType( csdefine.ENTITY_TYPE_MONSTER ):
			return csdefine.RELATION_NEUTRALLY

		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if entity.tong_dbID == self.ownTongDBID:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE
		
		if entity.isEntityType( csdefine.ENTITY_TYPE_XIAN_FENG ):
			if entity.ownTongDBID == self.ownTongDBID:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		return csdefine.RELATION_NEUTRALLY