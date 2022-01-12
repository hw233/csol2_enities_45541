# -*- coding: gb18030 -*-
# $Id: Exp $

from MonsterBuilding import MonsterBuilding
from bwdebug import *
import csconst
import csdefine
import ECBExtend


class MonsterFHLTBaseTower( MonsterBuilding ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		MonsterBuilding.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_BASE_TOWER )
		
	def queryRelation( self, entity ):
		"""
		virtual method.
		取得自己与目标的关系
		@param entity: 任意目标entity
		@return : RELATION_*
		"""
		#if self.isDestroyed or entity.isDestroyed:
		#	return csdefine.RELATION_NOFIGHT
		
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return MonsterBuilding.queryRelation( self, entity )
			
		if entity.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = entity.getOwner()
			if owner.etype == "MAILBOX" :
				return csdefine.RELATION_FRIEND
			entity = owner.entity
		
		if entity.utype in [ csdefine.ENTITY_TYPE_MONSTER, csdefine.ENTITY_TYPE_NPC, csdefine.ENTITY_TYPE_CONVOY_MONSTER, csdefine.ENTITY_TYPE_ROLE ]:
			if entity.state in [csdefine.ENTITY_STATE_PENDING, csdefine.ENTITY_STATE_QUIZ_GAME, csdefine.ENTITY_STATE_DEAD]:
				return csdefine.RELATION_NOFIGHT
			
			if self.effect_state & csdefine.EFFECT_STATE_ALL_NO_FIGHT or entity.effect_state & csdefine.EFFECT_STATE_ALL_NO_FIGHT:
				return csdefine.RELATION_NOFIGHT
			
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
				
		return csdefine.RELATION_FRIEND
		