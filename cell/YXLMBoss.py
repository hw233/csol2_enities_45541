# -*- coding: gb18030 -*-

import BigWorld
import csdefine
from Monster import Monster
from interface.CombatUnit import CombatUnit
from bwdebug import *
from CPUCal import CPU_CostCal




class YXLMBoss( Monster ) :

	def __init__( self ):
		Monster.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM )
		self.getSpaceCell().registMonster( self.className, self )
	
	def getSpaceCell( self ):
		sMB = self.getCurrentSpaceBase()
		if sMB:
			try:
				return BigWorld.entities[sMB.id]
			except KeyError:
				return sMB.cell
		
	def getSpawnPos( self ):
		return self.position
	
	def queryRelation( self, entity ):
		"""
		virtual method.
		取得自己与目标的关系
		@param entity: 任意目标entity
		@return : RELATION_*
		"""
		#if self.isDestroyed or entity.isDestroyed:
		#	return csdefine.RELATION_FRIEND
		
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND

		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.queryRelation( self, entity )
			
		e = entity
		if entity.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = e.getOwner()
			if owner.etype == "MAILBOX" :
				return csdefine.RELATION_FRIEND
			e = owner.entity
			
		if not isinstance( e, CombatUnit ):
			return csdefine.RELATION_FRIEND
		elif e.isState( csdefine.ENTITY_STATE_PENDING ):
			return csdefine.RELATION_NOFIGHT
		elif e.isState( csdefine.ENTITY_STATE_QUIZ_GAME ):
			return csdefine.RELATION_NOFIGHT
		elif e.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			# GM观察者模式
			if e.effect_state & csdefine.EFFECT_STATE_WATCHER:
				return csdefine.RELATION_NOFIGHT
			
			if e.teamMailbox and self.belong == e.teamMailbox.id:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE
		elif e.isEntityType( csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM ):
			if self.belong == e.belong:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		return csdefine.RELATION_FRIEND
		
	def doGoBack( self ):
		if self.isDestroyed or self.state == csdefine.ENTITY_STATE_DEAD:
			return

		self.canPatrol = True
		self.castTrap = True
	
	def createObjectNear( self, npcID, position, direction, state ):
		"""
		virtual method.
		创建一个entity
		@param npcID: STRING, 非玩家控制对象的唯一标识
		@param position: 创建的目标位置
		@param direction: 创建的目标方向
		@param state: see also: cell::BigWorld.createEntity()
		@return: new entity
		"""
		state[ "belong" ] = self.belong
		return Monster.createObjectNear( self, npcID, position, direction, state )

	def receiveDamage( self, casterID, skillID, damageType, damage ):
		"""
		Define and virtual method.
		接受伤害。
		@param   casterID: 施法者ID
		@type    casterID: OBJECT_ID
		@param    skillID: 技能ID
		@type     skillID: INT
		@param damageType: 伤害类型；see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: INT
		@param     damage: 伤害数值
		@type      damage: INT
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_SPEAKER ):
			return
		if self.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ):		#不可被选择的怪物，允许其他怪物攻击他，不允许玩家和宠物攻击他
			obj = BigWorld.entities.get( casterID )
			if obj and ( obj.isEntityType( csdefine.ENTITY_TYPE_PET ) or obj.isEntityType( csdefine.ENTITY_TYPE_ROLE ) ):
				return

		state = self.getState()
		subState = self.getSubState()
		hasCaster = BigWorld.entities.has_key( casterID )

		# 回走状态时，无敌状态 死亡了
		if subState == csdefine.M_SUB_STATE_GOBACK or state == csdefine.ENTITY_STATE_DEAD or \
		( hasCaster and BigWorld.entities[ casterID ].getState() == csdefine.ENTITY_STATE_DEAD ):
			return

		if not( damageType & csdefine.DAMAGE_TYPE_FLAG_BUFF ) and hasCaster:	# 不是buff伤害且施法者存在
			killerEntity = BigWorld.entities[casterID]
			# 第一次增加仇恨度，自然会进入战斗状态
			if killerEntity.getState() != csdefine.ENTITY_STATE_DEAD:
				if damageType & csdefine.DAMAGE_TYPE_FLAG_BUFF != csdefine.DAMAGE_TYPE_FLAG_BUFF:
					self.addDamageList( killerEntity.id, damage )
		
			# 如果伤害大于0
			if damage > 0 and casterID != self.id:
				self.bootyOwner = ( casterID, 0 )
				if not self.firstBruise:
					self.firstBruise = 1
					self.onFirstBruise( killerEntity, damage, skillID )
		else:
			# 没有攻击源或伤害是buff产生
			pass
		# 最后通知底层，因为如果先通知了底层，那么当怪物被一击必杀的时候很可能它根本就没进入战斗状态
		# 如果是这样的话，有些东西就不可能生效或会出错。
		CombatUnit.receiveDamage( self, casterID, skillID, damageType, damage )
	
	def sendSAICommand( self, recvIDs, type, sid ):
		"""
		发送sai指令
		"""
		self.getSpaceCell().sendSAICommand( recvIDs, type, sid, self )
	
	def recvSAICommand( self, type, sid, sendEntity ):
		"""
		define method.
		接收一个entity发过来的s ai
		"""
		self.setTemp( "SEND_SAI_ENTITY", sendEntity )
		self.insertSAI( sid )
		
	def onThink( self ):
		"""
		virtual method.
		"""
		if not self.canThink():
			return
		if self.state == csdefine.ENTITY_STATE_FIGHT:
			self.thinkSpeed = 1.0
			CPU_CostCal( csdefine.CPU_COST_AI, csdefine.CPU_COST_AI_FIGHT, self.className )
			self.onFightAIHeartbeat()
			CPU_CostCal( csdefine.CPU_COST_AI, csdefine.CPU_COST_AI_FIGHT, self.className )
		else:
			#非战斗状态下，心跳速度降低
			CPU_CostCal( csdefine.CPU_COST_AI, csdefine.CPU_COST_AI_FREE, self.className )
			self.onNoFightAIHeartbeat()
			CPU_CostCal( csdefine.CPU_COST_AI, csdefine.CPU_COST_AI_FREE, self.className )
			if self.noFightStateAICount == 0:
				self.thinkSpeed = 5.0
			else:
				self.thinkSpeed = 1.0

			if self.isDestroyed or not self.isReal():
				return

			if self.castTrap and self.initiativeRange > 0:
				self.onPlaceTrap( 0, 0 )													# 放置陷井
				self.castTrap = False

			if self.actionSign( csdefine.ACTION_FORBID_MOVE ):								# 执行散步或巡逻判断
				DEBUG_MSG( "im cannot the move!" )
				self.stopMoving()
			elif self.state == csdefine.ENTITY_STATE_FREE:
				if self.move_speed > 0 and not self.isMoving():								# 正在移动时或没有速度，那么跳过，等下次think(不论原因)
					if not self.patrolList and self.randomWalkRange > 0:													# 如果没有固定巡逻路线
						if self.randomWalkTime <= 0:
							if not self.queryTemp( "talkFollowID", 0 ):
								self.doRandomWalk()												# 随机移动
						else:
							self.randomWalkTime -= 1

		if not self.isDestroyed and self.isReal():
			self.think( self.thinkSpeed )

