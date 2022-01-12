# -*- coding: gb18030 -*-
# $Id: Exp $

from Monster import Monster
import csdefine
from bwdebug import *


class MonsterCampXianFeng( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_CAMP_XIAN_FENG )
		self.integral = 0

	def addIntegral( self, integral ):
		"""
		增加先锋怪拾取的积分
		"""
		self.integral = self.integral + integral
		self.getCurrentSpaceBase().cell.addCampFengHuoLianTianIntegral( self.ownCamp, integral )

	def onDie( self, killerID ):
		"""
		virtual method.

		死亡事情处理。
		
		"""
		killer = BigWorld.entities.get( killerID, None )
		if not killer:
			ERROR_MSG( "killer is None,id is %s"%killerID )
			Monster.onDie( self, killerID )
			return
		
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" :
				Monster.onDie( self, killerID )
				return
			killer = owner.entity
			
		if killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			self.getCurrentSpaceBase().cell.addCampFengHuoLianTianIntegral( killer.getCamp(), self.integral )
		elif killer.isEntityType( csdefine.ENTITY_TYPE_CAMP_XIAN_FENG ) or killer.isEntityType( csdefine.ENTITY_TYPE_CAMP_FENG_HUO_TOWER ) or killer.isEntityType( csdefine.ENTITY_TYPE_CAMP_FENG_HUO_BASE_TOWER ):
			self.getCurrentSpaceBase().cell.addCampFengHuoLianTianIntegral( killer.ownCamp, self.integral )
		self.getCurrentSpaceBase().cell.decCampFengHuoLianTianIntegral( self.ownCamp, self.integral )
		#self.getCurrentSpaceBase().cell.onMonsterXianFengDie( self.ownTongDBID, self.road )

		Monster.onDie( self, killerID )
		
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
			return Monster.queryRelation( self, entity )
			
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
				
		if entity.isEntityType( csdefine.ENTITY_TYPE_CAMP_XIAN_FENG ) or entity.isEntityType( csdefine.ENTITY_TYPE_CAMP_FENG_HUO_TOWER ) or \
			entity.isEntityType( csdefine.ENTITY_TYPE_CAMP_FENG_HUO_ALTAR ) or entity.isEntityType( csdefine.ENTITY_TYPE_CAMP_FENG_HUO_BASE_TOWER ):
			if entity.ownCamp == self.ownCamp:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE
				
		return csdefine.RELATION_FRIEND
		
#	def onDestroy( self ):
#		"""
#		entity 销毁的时候由BigWorld.Entity自动调用
#		"""
#		if self.getCurrentSpaceBase():
#			self.getCurrentSpaceBase().cell.onMonsterXianFengDie( self.ownTongDBID, self.road )
#		Monster.onDestroy( self )

	def onCorpseDelayTimer( self, controllerID, userData ):
		"""
		MONSTER_CORPSE_DELAY_TIMER_CBID的callback函数；
		"""
		self.getCurrentSpaceBase().cell.onMonsterXianFengDie( self.ownCamp, self.road )
		self.destroy()

