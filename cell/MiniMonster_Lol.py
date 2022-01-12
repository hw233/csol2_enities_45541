# -*- coding: gb18030 -*-
from MiniMonster import MiniMonster
import BigWorld
import csdefine
from bwdebug import *
import csarithmetic
import time
import Const
import csconst
from interface.CombatUnit import CombatUnit
from YXLMBoss import YXLMBoss
from Monster import Monster
from Domain_Fight import g_fightMgr

class MiniMonster_Lol( MiniMonster ):
	"""
	Ӣ�����˾������ר��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		MiniMonster.__init__( self )
		self.getScript().loadLolData( self )
		self.setEntityType( csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM )
	
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

	def doAllEventAI( self, event ):
		"""
		�����¼�AIִ��
		@param event: �¼�ID
		"""
		if not BigWorld.globalData["optimizeWithAI_ShortProcess"] :
			MiniMonster.doAllEventAI( self, event )
			return 
		if self.isDestroyed or not self.isReal():
			return
		
		if event == csdefine.AI_EVENT_SPELL_ENTERTRAP:					# �����¼�
			aiTarget = BigWorld.entities.get( self.aiTargetID )
			if aiTarget:
				g_fightMgr.buildEnemyRelation( self, aiTarget )
			return 
		
		if event == csdefine.AI_EVENT_ENEMY_LIST_CHANGED:		# ս���б�ı��¼�
			if self.state == csdefine.ENTITY_STATE_FREE:		# ��ͨ״̬,ѡ�񴥷�����ĵ�����Ϊ����Ŀ��
				eid = self.findFirstEnemyByTime()
				if BigWorld.entities.has_key( eid ):
					self.setAITargetID( eid )
					self.changeAttackTarget( eid )
				return
			
			if self.state == csdefine.ENTITY_STATE_FIGHT:		# ս��״̬�£��������б�Ϊ�գ�����ս��״̬
				if len( self.enemyList ) <= 0:
					self.spawnPos = tuple( self.position )
					self.changeState( csdefine.ENTITY_STATE_FREE )
					return

		if event == csdefine.AI_EVENT_ATTACKER_ON_REMOVE:		# ��ǰ���������Ƴ������б�ʱ(����,������Ұ,�Ҳ�����)
			if self.state == csdefine.ENTITY_STATE_DEAD:		# ��������ս���б�Ϊ�ղ����Ƴ�����
				return 
			self.getNearByEnemy( float( self.viewRange ) )

	def doGoBack( self ):
		"""
		����ʱֱ�ӽ���Ѳ��
		"""
		if not BigWorld.globalData["optimizeWithAI_ShortProcess"] :
			MiniMonster.doGoBack( self )
			return 

		if self.state == csdefine.ENTITY_STATE_DEAD:
			return
		if self.state == csdefine.ENTITY_STATE_FREE: 			# ��ͨ״̬�·�����
			self.onPlaceTrap( 0, 0 )
			self.castTrap = False
		
		# ����Ѳ��
		graphID = self.getScript().patrolList
		patrolList = BigWorld.PatrolPath( graphID )
		if not patrolList or not patrolList.isReady():
			ERROR_MSG( "[ %s, %i ] patrol(%s) unWorked. it's not ready or not have such graphID!" % ( self.className, self.id, graphID) )
			return
		patrolPathNode, position = patrolList.nearestNode( self.position )
		self.doPatrol( patrolPathNode, patrolList  )

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
	
	def getNearByEnemy( self, range ):
		"""
		��������Ŀ��
		"""
		if self.isWitnessed:									# �����Χ����ң���ͻ�������
			self.requestNearByEnemy( range )
			return
		
		INFO_MSG( " I %s, %i have no role in  my AOI" % ( self.className, self.id ))
		eid = self.searchNearByEnemyInServer( range )			# ��Χû��������ڷ���������
		target = BigWorld.entities.get( eid )
		if target and target.state != csdefine.ENTITY_STATE_DEAD and self.targetID != eid:
			self.setAITargetID( eid )
			self.changeAttackTarget( eid )
			return
		
		enemyID = self.getNearestEnemy()						# ��Χû���ѵ�������ҵ����б�
		if target and target.state != csdefine.ENTITY_STATE_DEAD and self.targetID != eid:
			self.setAITargetID( eid )
			self.changeAttackTarget( eid )
			return
		
		self.doGoBack()

	def requestNearByEnemy( self, range ):
		"""
		��ͻ������������Ŀ��
		"""
		self.removeTemp( "getNearByEnemyID" )
		self.planesOtherClients( "requestNearByEnemy", ( range, ) )

	def receiveNearByEnemy( self, srcEntityID, enemyID ):
		"""
		Exposed method
		�ͻ��˷��ػ�ȡ����enemyID
		"""
		if self.isDestroyed or self.state == csdefine.ENTITY_STATE_DEAD:
			return
		
		srcEntity =  BigWorld.entities.get( srcEntityID )		# �ж���Һ��Լ��Ƿ���ͬһ�ռ�
		if not srcEntity or srcEntity.spaceID != self.spaceID:
			return
		
		if self.queryTemp( "getNearByEnemyID", 0 ):				# �Ѿ����յ��������򷵻�
			return
		
		enemy = BigWorld.entities.get( enemyID )
		if enemy and self.queryRelation( enemy ) != csdefine.RELATION_ANTAGONIZE:
			ERROR_MSG( "ClassName %s, id %i: I've got a wrong enemy %i from client, our relation is %i " % ( self.className, self.id, enemyID, self.queryRelation( enemy )))
			return
		
		INFO_MSG( "ClassName %s, id %i: I've received an enemy  %s from client��"  % ( self.className, self.id, enemyID ) )
		self.onReceiveNearByEnemy( enemyID )

	def onReceiveNearByEnemy( self, enemyID ):
		"""
		���յ��ͻ��˷��ص�����
		"""
		self.setTemp( "getNearByEnemyID", 1 )
		enemy = BigWorld.entities.get( enemyID )
		if not enemy or enemy.isDestroyed or enemy.state == csdefine.ENTITY_STATE_DEAD: 
			enemyID = self.getNearestEnemy() 					# ���ͻ��˷��ص�������Ч�����ȡ�����б�����ĵ���
		
		if self.targetID != enemyID and enemyID:
			self.setAITargetID( enemyID )
			self.changeAttackTarget( enemyID )
			self.think( 0.1 )

	def getNearestEnemy( self ):
		"""
		�ӵ����б���ѡ�������Ŀ��
		"""
		distance = 100.0
		eid = 0

		for id in self.enemyList:								# ѡ��ս���б�������ĵ���
			e = BigWorld.entities.get( id )
			if e:
				dis = csarithmetic.distancePP3( e.position, self.position )
				if distance > dis:
					eid = e.id
					distance = dis
		return eid

	def searchNearByEnemyInServer( self, range ):
		"""
		�ڷ��������������Ŀ��
		"""
		bossID, bossDis, nearID, nearDis, eid, edis = 0, 100.0, 0, 100.0, 0 , 100.0
		rangeEntities = self.entitiesInRangeExt( range )
		rangeEntities.sort( key = lambda e : e.position.distTo( self.position ) )
		for e in rangeEntities:
			if self.queryRelation( e ) ==  csdefine.RELATION_ANTAGONIZE and e.state != csdefine.ENTITY_STATE_DEAD:
				if e.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or isinstance( e, YXLMBoss ):
					if not bossID: 							# ������������һ���Boss������ѡ��
						bossID = e.id
						bossDis = e.position.distTo( self.position )
						continue
				
				if not nearID:								# ��ѡȡ�����Ŀ��
					nearID = e.id
					nearDis = e.position.distTo( self.position )
					if len( e.damageList ) >= 2:			# ��������Ŀ��Ĺ�����̫�࣬����ѡ����һ��Ŀ��
						continue
					break
				
				edis = e.position.distTo( self.position )
				if edis - nearDis < 3.0:					# ��һ��Ŀ�����̫Զ����������
					break
				if len( e.damageList ) < 2: 				# ���Ŀ��������Ŀ��С��3.0�����˺��б�С��2��ֹͣ����
					eid = e.id
					break
		
		# ֻ��Boss����ҡ�Boss����С��6��
		if  ( bossID and not nearID and not eid ) \
			or ( bossID and nearID and not eid and bossDis < 6.0 < nearDis and nearDis - bossDis > 3.0 ) \
			or ( bossID and eid and bossDis < 6.0 < edis and edis -  bossDis > 3.0 ):
			eid = bossID
		
		# ֻ�������Ŀ��
		if ( not bossID and not eid and nearID ) \
			or ( bossID and nearID and not eid and nearDis - bossDis < 3.0 ):
			eid = nearID
			
		return eid

	def changeAttackTarget( self, enemyID ):
		"""
		������Ϊ�˼�¼������
		"""
		if self.targetID != enemyID:
			MiniMonster.changeAttackTarget( self, enemyID )
			self.spawnPos = self.position

	def onEnterTrapExt( self, entity, range, controllerID ):
		"""
		Entity.onEnterTrapExt( entity, range, controllerID )
		"""
		# ����entity �����������巶Χ֮�ڣ��˺����ͻᱻ����
		if not BigWorld.globalData["optimizeWithAI_ShortProcess"] :
			MiniMonster.onEnterTrapExt( self, entity, range, controllerID )
			return 
		
		self.spawnPos = self.position		# ���������Ϊ��������Χ�����ܴ�����������

		if self.checkEnterTrapEntityType( entity ):	# �����ҽ����ҵ���Ұ
			DEBUG_MSG( "%s(%i): %s into my initiativeRange." % ( self.getName(), self.id, entity.getName() ) )
			self.aiTargetID = entity.id
			self.doAllEventAI( csdefine.AI_EVENT_SPELL_ENTERTRAP )
			self.aiTargetID = 0

	def checkEnterTrapEntityType( self, entity ):
		"""
		virtual method.
		�����������entity����
		"""
		if not BigWorld.globalData["optimizeWithAI_ShortProcess"] :
			MiniMonster.checkEnterTrapEntityType( self, entity )
			return False
		
		if not isinstance( entity, Monster ) and entity.utype != csdefine.ENTITY_TYPE_ROLE:	# ����Monster����ң�����
			return False
		
		# �Ƿ�Ϊ�жԹ�ϵ
		if self.queryRelation( entity ) != csdefine.RELATION_ANTAGONIZE:
			return False

		# Ǳ����أ��Ƿ���⵽Ŀ��
		if not self.isRealLook( entity.id ):
			return False

		# ������Ч������Χ�ڣ�ʲôҲ����
		if entity.position.distTo( self.spawnPos ) > self.territory:
			INFO_MSG( "entity is not in my territory, entity:className %s, id %i, self:className %s, id %i " % ( entity.className, entity.id, self.className, self.id ))
			return False

		# ע�⣺getState()ȡ�õ�״̬��һ����real entity��״̬,��Ҵ�������״̬������״̬��ʲôҲ����
		plState = entity.getState()
		if plState == csdefine.ENTITY_STATE_PENDING or plState == csdefine.ENTITY_STATE_QUIZ_GAME or plState == csdefine.ENTITY_STATE_DEAD:
			INFO_MSG( "entity state check:className %s,id %i state is %i " % ( entity.className, entity.id, plState ) )
			return False
		
		# ��ͨ����Ϣ��Ѳ��״̬�¿��Դ�������
		state = self.getState()
		if state != csdefine.ENTITY_STATE_FREE and state != csdefine.ENTITY_STATE_REST and self.movingType != Const.MOVE_TYPE_PATROL:
			INFO_MSG( "self state check: className %s, id %i, state is %i" % ( self.className, self.id, state ) )
			return False

		return True