# -*- coding: gb18030 -*-
# $Id: Exp $

from MonsterBuilding import MonsterBuilding
from bwdebug import *
import csconst
import csdefine
import ECBExtend


class MonsterCampFHLTTower( MonsterBuilding ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		MonsterBuilding.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_CAMP_FENG_HUO_TOWER )
		if self.getCurrentSpaceBase():
			self.getCurrentSpaceBase().cell.addTowerNum( self.ownCamp )
	
	def onDie( self, killerID ):
		"""
		virtual method.

		死亡事情处理。
		
		"""
		killer = BigWorld.entities.get( killerID, None )
		if not killer:
			ERROR_MSG( "killer is None,id is %s"%killerID )
			MonsterBuilding.onDie( self, killerID )
			return
			
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" :
				MonsterBuilding.onDie( self, killerID )
				return
			killer = owner.entity
			
		if killer.isEntityType( csdefine.ENTITY_TYPE_CAMP_XIAN_FENG ):
			self.getCurrentSpaceBase().cell.decTowerNum( self.ownCamp )
			self.getCurrentSpaceBase().cell.addHostilityCampIntegral( killer.ownCamp, self.ownCamp )
			killer.addTimer( csconst.MONSTER_CORPSE_DURATION, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
		else:
			self.getCurrentSpaceBase().cell.decTowerNum( self.ownCamp )
			self.getCurrentSpaceBase().cell.addHostilityCampIntegral( killer.getCamp(), self.ownCamp )

		MonsterBuilding.onDie( self, killerID )
		
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
			if entity.getCamp() == self.ownCamp:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE
				
		if entity.isEntityType( csdefine.ENTITY_TYPE_CAMP_XIAN_FENG ):
			if entity.ownCamp == self.ownCamp:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE
				
		return csdefine.RELATION_FRIEND
		