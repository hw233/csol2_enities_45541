# -*- coding: gb18030 -*-

from bwdebug import *
from NPC import NPC
import csstatus
import csdefine

class GuardNPC( NPC ):
	"""
	守卫
	"""
	def __init__( self ):
		"""
		"""
		NPC.__init__( self )
		
		
	def doGoBack( self, selfEntity ):
		"""
		"""
		return selfEntity.gotoPosition(tuple( selfEntity.spawnPos ))
		
	def onWitnessed( self, selfEntity, isWitnessed ):
		"""
		This method is called when the state of this entity being witnessed changes.
		@param isWitnessed: A boolean indicating whether or not the entity is now witnessed;
		@type  isWitnessed: bool
		"""
		if isWitnessed:
			if selfEntity.initiativeRange > 0:
				self.onPlaceGuardTrap( selfEntity, 0, 0 )													# 放置陷井
		else:
			guardProximityID = selfEntity.queryTemp( "guardProximityID", 0 )
			if guardProximityID != 0:
				selfEntity.cancel( guardProximityID )
				selfEntity.removeTemp( "guardProximityID" )
				selfEntity.removeTemp( "test_GuardProximity" )
		
	def onEnterTrapExt( self, selfEntity, entity, range, controllerID ):
		"""
		Entity.onEnterTrapExt( entity, range, controllerID )
		"""
		guardTrapID = selfEntity.queryTemp( "guardProximityID", 0 )
		if guardTrapID == 0 and controllerID != guardTrapID:
			return

		if self.checkEnterTrapEntityType( selfEntity, entity ):	# 如果玩家进入我的视野
			DEBUG_MSG( "%s(%i): %s into my initiativeRange." % ( selfEntity.getName(), selfEntity.id, entity.getName() ) )
			DEBUG_MSG( "my position =", selfEntity.position, "role position =", entity.position, "distance =", entity.position.distTo( selfEntity.position ), "my initiativeRange =", selfEntity.initiativeRange, "range =", range )
			selfEntity.aiTargetID = entity.id
			selfEntity.doAllEventAI( csdefine.AI_EVENT_ENTER_GUARD_TRAP )
			selfEntity.aiTargetID = 0
		
	def onPlaceGuardTrap( self, selfEntity, controllerID, userData ):
		"""
		timer for place trap
		called by MONENMITY_ADD_TRAP_TIMER_CBID
		"""
		if selfEntity.queryTemp( "guardProximityID", 0 ) == 0:
			selfEntity.setTemp( "test_GuardProximity", True )								# 这个设置主要是要处理刚放陷阱就被entity进入导致onEnterTrapExt马上调用的情况
			id = selfEntity.addProximityExt( selfEntity.initiativeRange )						# 则添加一个陷阱，当有entity进入陷阱时，onEnterTrapExt()会自动被调用
			if selfEntity.queryTemp( "test_GuardProximity", False ):
				selfEntity.setTemp( "guardProximityID", id )
				selfEntity.removeTemp( "test_GuardProximity" )
		
	def checkEnterTrapEntityType( self, selfEntity, entity ):
		"""
		检查进入陷阱的entity类型
		"""
		# 是否为敌对关系
		if selfEntity.queryRelation( entity ) != csdefine.RELATION_ANTAGONIZE:
			return False

		# 注意：getState()取得的状态不一定是real entity的状态
		plState = entity.getState()
		# 玩家处于销毁状态或死亡状态，什么也不做
		if plState == csdefine.ENTITY_STATE_PENDING or plState == csdefine.ENTITY_STATE_QUIZ_GAME or plState == csdefine.ENTITY_STATE_DEAD:
			return False

		state = selfEntity.getState()
		if state != csdefine.ENTITY_STATE_FREE and state != csdefine.ENTITY_STATE_REST:
			return False

		# 不在有效攻击范围内，什么也不做
		if selfEntity.patrolList != None:
			if entity.position.distTo( selfEntity.position ) > selfEntity.territory:
				return False
		else:
			if entity.position.distTo( selfEntity.spawnPos ) > selfEntity.territory:
				return False

		# 潜行相关，是否侦测到目标
		if not selfEntity.isRealLook( entity.id ):
			return False

		return True
		