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
		ȡ���Լ���Ŀ��Ĺ�ϵ
		@param entity: ����Ŀ��entity
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
			# GM�۲���ģʽ
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
		����һ��entity
		@param npcID: STRING, ����ҿ��ƶ����Ψһ��ʶ
		@param position: ������Ŀ��λ��
		@param direction: ������Ŀ�귽��
		@param state: see also: cell::BigWorld.createEntity()
		@return: new entity
		"""
		state[ "belong" ] = self.belong
		return Monster.createObjectNear( self, npcID, position, direction, state )

	def receiveDamage( self, casterID, skillID, damageType, damage ):
		"""
		Define and virtual method.
		�����˺���
		@param   casterID: ʩ����ID
		@type    casterID: OBJECT_ID
		@param    skillID: ����ID
		@type     skillID: INT
		@param damageType: �˺����ͣ�see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: INT
		@param     damage: �˺���ֵ
		@type      damage: INT
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_SPEAKER ):
			return
		if self.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ):		#���ɱ�ѡ��Ĺ�������������﹥��������������Һͳ��﹥����
			obj = BigWorld.entities.get( casterID )
			if obj and ( obj.isEntityType( csdefine.ENTITY_TYPE_PET ) or obj.isEntityType( csdefine.ENTITY_TYPE_ROLE ) ):
				return

		state = self.getState()
		subState = self.getSubState()
		hasCaster = BigWorld.entities.has_key( casterID )

		# ����״̬ʱ���޵�״̬ ������
		if subState == csdefine.M_SUB_STATE_GOBACK or state == csdefine.ENTITY_STATE_DEAD or \
		( hasCaster and BigWorld.entities[ casterID ].getState() == csdefine.ENTITY_STATE_DEAD ):
			return

		if not( damageType & csdefine.DAMAGE_TYPE_FLAG_BUFF ) and hasCaster:	# ����buff�˺���ʩ���ߴ���
			killerEntity = BigWorld.entities[casterID]
			# ��һ�����ӳ�޶ȣ���Ȼ�����ս��״̬
			if killerEntity.getState() != csdefine.ENTITY_STATE_DEAD:
				if damageType & csdefine.DAMAGE_TYPE_FLAG_BUFF != csdefine.DAMAGE_TYPE_FLAG_BUFF:
					self.addDamageList( killerEntity.id, damage )
		
			# ����˺�����0
			if damage > 0 and casterID != self.id:
				self.bootyOwner = ( casterID, 0 )
				if not self.firstBruise:
					self.firstBruise = 1
					self.onFirstBruise( killerEntity, damage, skillID )
		else:
			# û�й���Դ���˺���buff����
			pass
		# ���֪ͨ�ײ㣬��Ϊ�����֪ͨ�˵ײ㣬��ô�����ﱻһ����ɱ��ʱ��ܿ�����������û����ս��״̬
		# ����������Ļ�����Щ�����Ͳ�������Ч������
		CombatUnit.receiveDamage( self, casterID, skillID, damageType, damage )
	
	def sendSAICommand( self, recvIDs, type, sid ):
		"""
		����saiָ��
		"""
		self.getSpaceCell().sendSAICommand( recvIDs, type, sid, self )
	
	def recvSAICommand( self, type, sid, sendEntity ):
		"""
		define method.
		����һ��entity��������s ai
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
			#��ս��״̬�£������ٶȽ���
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
				self.onPlaceTrap( 0, 0 )													# �����ݾ�
				self.castTrap = False

			if self.actionSign( csdefine.ACTION_FORBID_MOVE ):								# ִ��ɢ����Ѳ���ж�
				DEBUG_MSG( "im cannot the move!" )
				self.stopMoving()
			elif self.state == csdefine.ENTITY_STATE_FREE:
				if self.move_speed > 0 and not self.isMoving():								# �����ƶ�ʱ��û���ٶȣ���ô���������´�think(����ԭ��)
					if not self.patrolList and self.randomWalkRange > 0:													# ���û�й̶�Ѳ��·��
						if self.randomWalkTime <= 0:
							if not self.queryTemp( "talkFollowID", 0 ):
								self.doRandomWalk()												# ����ƶ�
						else:
							self.randomWalkTime -= 1

		if not self.isDestroyed and self.isReal():
			self.think( self.thinkSpeed )

