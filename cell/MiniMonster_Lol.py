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
	英雄联盟精简怪物专用
	"""
	def __init__( self ):
		"""
		初始化
		"""
		MiniMonster.__init__( self )
		self.getScript().loadLolData( self )
		self.setEntityType( csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM )
	
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

	def doAllEventAI( self, event ):
		"""
		重载事件AI执行
		@param event: 事件ID
		"""
		if not BigWorld.globalData["optimizeWithAI_ShortProcess"] :
			MiniMonster.doAllEventAI( self, event )
			return 
		if self.isDestroyed or not self.isReal():
			return
		
		if event == csdefine.AI_EVENT_SPELL_ENTERTRAP:					# 陷阱事件
			aiTarget = BigWorld.entities.get( self.aiTargetID )
			if aiTarget:
				g_fightMgr.buildEnemyRelation( self, aiTarget )
			return 
		
		if event == csdefine.AI_EVENT_ENEMY_LIST_CHANGED:		# 战斗列表改变事件
			if self.state == csdefine.ENTITY_STATE_FREE:		# 普通状态,选择触发陷阱的敌人作为攻击目标
				eid = self.findFirstEnemyByTime()
				if BigWorld.entities.has_key( eid ):
					self.setAITargetID( eid )
					self.changeAttackTarget( eid )
				return
			
			if self.state == csdefine.ENTITY_STATE_FIGHT:		# 战斗状态下，若敌人列表为空，脱离战斗状态
				if len( self.enemyList ) <= 0:
					self.spawnPos = tuple( self.position )
					self.changeState( csdefine.ENTITY_STATE_FREE )
					return

		if event == csdefine.AI_EVENT_ATTACKER_ON_REMOVE:		# 当前攻击对象被移出敌人列表时(死亡,不在视野,找不到等)
			if self.state == csdefine.ENTITY_STATE_DEAD:		# 死亡或者战斗列表为空不做移除处理
				return 
			self.getNearByEnemy( float( self.viewRange ) )

	def doGoBack( self ):
		"""
		回走时直接进入巡逻
		"""
		if not BigWorld.globalData["optimizeWithAI_ShortProcess"] :
			MiniMonster.doGoBack( self )
			return 

		if self.state == csdefine.ENTITY_STATE_DEAD:
			return
		if self.state == csdefine.ENTITY_STATE_FREE: 			# 普通状态下放陷阱
			self.onPlaceTrap( 0, 0 )
			self.castTrap = False
		
		# 开启巡逻
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
	
	def getNearByEnemy( self, range ):
		"""
		获得最近的目标
		"""
		if self.isWitnessed:									# 如果周围有玩家，向客户端请求
			self.requestNearByEnemy( range )
			return
		
		INFO_MSG( " I %s, %i have no role in  my AOI" % ( self.className, self.id ))
		eid = self.searchNearByEnemyInServer( range )			# 周围没有玩家则在服务器搜索
		target = BigWorld.entities.get( eid )
		if target and target.state != csdefine.ENTITY_STATE_DEAD and self.targetID != eid:
			self.setAITargetID( eid )
			self.changeAttackTarget( eid )
			return
		
		enemyID = self.getNearestEnemy()						# 周围没有搜到，则查找敌人列表
		if target and target.state != csdefine.ENTITY_STATE_DEAD and self.targetID != eid:
			self.setAITargetID( eid )
			self.changeAttackTarget( eid )
			return
		
		self.doGoBack()

	def requestNearByEnemy( self, range ):
		"""
		向客户端请求最近的目标
		"""
		self.removeTemp( "getNearByEnemyID" )
		self.planesOtherClients( "requestNearByEnemy", ( range, ) )

	def receiveNearByEnemy( self, srcEntityID, enemyID ):
		"""
		Exposed method
		客户端返回获取到的enemyID
		"""
		if self.isDestroyed or self.state == csdefine.ENTITY_STATE_DEAD:
			return
		
		srcEntity =  BigWorld.entities.get( srcEntityID )		# 判断玩家和自己是否在同一空间
		if not srcEntity or srcEntity.spaceID != self.spaceID:
			return
		
		if self.queryTemp( "getNearByEnemyID", 0 ):				# 已经接收到了数据则返回
			return
		
		enemy = BigWorld.entities.get( enemyID )
		if enemy and self.queryRelation( enemy ) != csdefine.RELATION_ANTAGONIZE:
			ERROR_MSG( "ClassName %s, id %i: I've got a wrong enemy %i from client, our relation is %i " % ( self.className, self.id, enemyID, self.queryRelation( enemy )))
			return
		
		INFO_MSG( "ClassName %s, id %i: I've received an enemy  %s from client！"  % ( self.className, self.id, enemyID ) )
		self.onReceiveNearByEnemy( enemyID )

	def onReceiveNearByEnemy( self, enemyID ):
		"""
		接收到客户端返回的数据
		"""
		self.setTemp( "getNearByEnemyID", 1 )
		enemy = BigWorld.entities.get( enemyID )
		if not enemy or enemy.isDestroyed or enemy.state == csdefine.ENTITY_STATE_DEAD: 
			enemyID = self.getNearestEnemy() 					# 若客户端返回的数据无效，则获取敌人列表里面的敌人
		
		if self.targetID != enemyID and enemyID:
			self.setAITargetID( enemyID )
			self.changeAttackTarget( enemyID )
			self.think( 0.1 )

	def getNearestEnemy( self ):
		"""
		从敌人列表中选择最近的目标
		"""
		distance = 100.0
		eid = 0

		for id in self.enemyList:								# 选择战斗列表中最近的敌人
			e = BigWorld.entities.get( id )
			if e:
				dis = csarithmetic.distancePP3( e.position, self.position )
				if distance > dis:
					eid = e.id
					distance = dis
		return eid

	def searchNearByEnemyInServer( self, range ):
		"""
		在服务器搜索最近的目标
		"""
		bossID, bossDis, nearID, nearDis, eid, edis = 0, 100.0, 0, 100.0, 0 , 100.0
		rangeEntities = self.entitiesInRangeExt( range )
		rangeEntities.sort( key = lambda e : e.position.distTo( self.position ) )
		for e in rangeEntities:
			if self.queryRelation( e ) ==  csdefine.RELATION_ANTAGONIZE and e.state != csdefine.ENTITY_STATE_DEAD:
				if e.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or isinstance( e, YXLMBoss ):
					if not bossID: 							# 如果最近的是玩家或者Boss，继续选择
						bossID = e.id
						bossDis = e.position.distTo( self.position )
						continue
				
				if not nearID:								# 先选取最近的目标
					nearID = e.id
					nearDis = e.position.distTo( self.position )
					if len( e.damageList ) >= 2:			# 如果最近的目标的攻击者太多，继续选择下一个目标
						continue
					break
				
				edis = e.position.distTo( self.position )
				if edis - nearDis < 3.0:					# 下一个目标距离太远，不再搜索
					break
				if len( e.damageList ) < 2: 				# 如果目标距离最近目标小于3.0，且伤害列表小于2，停止搜索
					eid = e.id
					break
		
		# 只有Boss或玩家、Boss距离小于6米
		if  ( bossID and not nearID and not eid ) \
			or ( bossID and nearID and not eid and bossDis < 6.0 < nearDis and nearDis - bossDis > 3.0 ) \
			or ( bossID and eid and bossDis < 6.0 < edis and edis -  bossDis > 3.0 ):
			eid = bossID
		
		# 只有最近的目标
		if ( not bossID and not eid and nearID ) \
			or ( bossID and nearID and not eid and nearDis - bossDis < 3.0 ):
			eid = nearID
			
		return eid

	def changeAttackTarget( self, enemyID ):
		"""
		重载是为了记录出生点
		"""
		if self.targetID != enemyID:
			MiniMonster.changeAttackTarget( self, enemyID )
			self.spawnPos = self.position

	def onEnterTrapExt( self, entity, range, controllerID ):
		"""
		Entity.onEnterTrapExt( entity, range, controllerID )
		"""
		# 当有entity 进入怪物的陷阱范围之内，此函数就会被调用
		if not BigWorld.globalData["optimizeWithAI_ShortProcess"] :
			MiniMonster.onEnterTrapExt( self, entity, range, controllerID )
			return 
		
		self.spawnPos = self.position		# 避免出现因为脱离领域范围而不能触发陷阱的情况

		if self.checkEnterTrapEntityType( entity ):	# 如果玩家进入我的视野
			DEBUG_MSG( "%s(%i): %s into my initiativeRange." % ( self.getName(), self.id, entity.getName() ) )
			self.aiTargetID = entity.id
			self.doAllEventAI( csdefine.AI_EVENT_SPELL_ENTERTRAP )
			self.aiTargetID = 0

	def checkEnterTrapEntityType( self, entity ):
		"""
		virtual method.
		检查进入陷阱的entity类型
		"""
		if not BigWorld.globalData["optimizeWithAI_ShortProcess"] :
			MiniMonster.checkEnterTrapEntityType( self, entity )
			return False
		
		if not isinstance( entity, Monster ) and entity.utype != csdefine.ENTITY_TYPE_ROLE:	# 不是Monster或玩家，返回
			return False
		
		# 是否为敌对关系
		if self.queryRelation( entity ) != csdefine.RELATION_ANTAGONIZE:
			return False

		# 潜行相关，是否侦测到目标
		if not self.isRealLook( entity.id ):
			return False

		# 不在有效攻击范围内，什么也不做
		if entity.position.distTo( self.spawnPos ) > self.territory:
			INFO_MSG( "entity is not in my territory, entity:className %s, id %i, self:className %s, id %i " % ( entity.className, entity.id, self.className, self.id ))
			return False

		# 注意：getState()取得的状态不一定是real entity的状态,玩家处于销毁状态或死亡状态，什么也不做
		plState = entity.getState()
		if plState == csdefine.ENTITY_STATE_PENDING or plState == csdefine.ENTITY_STATE_QUIZ_GAME or plState == csdefine.ENTITY_STATE_DEAD:
			INFO_MSG( "entity state check:className %s,id %i state is %i " % ( entity.className, entity.id, plState ) )
			return False
		
		# 普通、休息、巡逻状态下可以触发陷阱
		state = self.getState()
		if state != csdefine.ENTITY_STATE_FREE and state != csdefine.ENTITY_STATE_REST and self.movingType != Const.MOVE_TYPE_PATROL:
			INFO_MSG( "self state check: className %s, id %i, state is %i" % ( self.className, self.id, state ) )
			return False

		return True