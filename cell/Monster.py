# -*- coding: gb18030 -*-
# Monster.py

"""
怪物模块
"""
# $Id: Monster.py,v 1.178 2008-09-04 07:44:14 kebiao Exp $
#-------------------------------------------------
# Python
import random
import math
#-------------------------------------------------
# Engine
import BigWorld
import time
#-------------------------------------------------
# Cell
import Role	#add by wuxo 2011-10-11
import Math
import Const
import utils
from bwdebug import *
from NPCObject import NPCObject
from interface.CombatUnit import CombatUnit
from interface.AIInterface import AIInterface
from Resource import PatrolMgr
from interface.AmbulantObject import AmbulantObject
from NPCExpLoader import NPCExpLoader
from NPCPotentialLoader import NPCPotentialLoader
from NPCAccumLoader import NPCAccumLoader
from DaohengLoader import DaohengLoader     # 道行属性
from MonsterDaohengLoader import MonsterDaohengLoader  # 道行击杀奖励
import ECBExtend
import Resource.AIData
import Function
from NPCBaseAttrLoader import NPCBaseAttrLoader
from ObjectScripts.GameObjectFactory import g_objFactory	# 14:27 2008-8-20,wsf
g_npcBaseAttr = NPCBaseAttrLoader.instance()
from Resource.NPCExcDataLoader import NPCExcDataLoader
from MonsterIntensifyPropertyData import MonsterIntensifyPropertyData
import csarithmetic
g_npcExcData = NPCExcDataLoader.instance()
from config.server.gameObject.MonsterCampMorale import Datas as g_campMorale
#-------------------------------------------------
# Common
import utils
import csconst
import csdefine
import csstatus
import ItemTypeEnum
#-------------------------------------------------
from MsgLogger import g_logger

g_patrolMgr = PatrolMgr.PatrolMgr.instance()
g_aiDatas = Resource.AIData.aiData_instance()
g_monsterIntensifyAttr = MonsterIntensifyPropertyData.instance()
g_npcExp = NPCExpLoader.instance()
g_npcPotential = NPCPotentialLoader.instance()
g_npcAccum = NPCAccumLoader.instance()
g_daoheng = DaohengLoader.instance()			# 道行
g_daohengAch = MonsterDaohengLoader.instance()

from CPUCal import CPU_CostCal
from Domain_Fight import g_fightMgr


class Monster( NPCObject, AmbulantObject, CombatUnit, AIInterface ):
	"""
	怪物类，续承于NPC和可战斗单位
	"""
	def __init__(self):
		AIInterface.__init__( self )
		AmbulantObject.__init__( self )
		CombatUnit.__init__( self )
		NPCObject.__init__(self)

		self.otherClients.onReviviscence()

		# 临时变量

		self.setTemp( "callSign", False )										# 设置怪物初始化战斗呼叫标志 为true代表不可呼叫与被呼叫
		self.removeTemp( "patrol_stop" )

		# 设置默认速度
		self.move_speed_base = self.walkSpeed									# 设置怪物初始化移动速度
		self.calcMoveSpeed()													# 计算怪物移动速度
		self.subState = csdefine.M_SUB_STATE_NONE								# 设置怪物初始化sub状态
		self.castTrap = False

		# 如果是巡逻NPC，则持续启动AI
		if self.patrolList != None:
			self.canPatrol = True
			# 等待30秒后开始巡逻， self.patrolList需要被引擎初始化 self.patrolList.isReady()
			self.think( 30.0 )													# 对于巡逻NPC,为了保证巡逻位置的正确性,只能马上就开始think()

		if self.hasFlag( csdefine.ENTITY_FLAG_MONSTER_THINK ):
			self.think( 2.0 )

		#以下判定是用于确保怪物在有敌人进入陷阱后，能引发陷阱效果。主要是避免策划填写错误
		if self.initiativeRange > 0:
			self.addTimer( 1, 0, ECBExtend.MONENMITY_ADD_TRAP_TIMER_CBID )
			if ( self.initiativeRange + self.randomWalkRange ) > self.territory:
				ERROR_MSG( "Monster(NPC)'s className(%s) initiativeRange + randomWalkRange > territory"%self.className )
		if self.viewRange < self.initiativeRange:
			ERROR_MSG( "Monster(NPC)'s className(%s) viewRange < initiativeRange"%self.className )
		#由于策划新手经常会配置一些领域范围或者视野范围为500的大数值，而这样配置不太合理，
		#因此打印一些警告信息，以便后续能够改正过来，也方便后续跟进
		if self.territory > Const.TERRITORY_LIMIT:
			WARNING_MSG( "Monster(NPC)'s className(%s) territory > 100"%self.className )
		if self.viewRange > Const.VIEWRANGE_LIMIT:
			WARNING_MSG( "Monster(NPC)'s className(%s) viewRange > 100"%self.className )

		if self.getCurrentSpaceBase():
			self.getCurrentSpaceBase().addMonsterCount()
		else:
			self.addTimer( 1.0, 0, ECBExtend.DESTROY_SELF_TIMER_CBID ) # 找不到Space Base,这时候估计Space已经销毁了
			#ERROR_MSG( "Monster(NPC)'s className(%s) create before space create!!"%self.className )
		if self.hasFlag(csdefine.ENTITY_VOLATILE_ALWAYS_OPEN) and self.hasFlag(csdefine.ENTITY_VOLATILE_ALWAYS_CLOSE ):
			ERROR_MSG( "Monster(NPC)'s className(%s) has VOLATILE_ALWAYS_OPEN while flag VOLATILE_ALWAYS_CLOSE is already exist!" % self.className )
		if self.hasFlag(csdefine.ENTITY_VOLATILE_ALWAYS_OPEN):
			self.openVolatileInfo()
		if self.hasFlag(csdefine.ENTITY_VOLATILE_ALWAYS_CLOSE):
			self.closeVolatileInfo()

		self.firstHide = True

	#-----------------------------------------------------------------------------------------------------
	# 主动攻击类型怪物陷阱相关
	#-----------------------------------------------------------------------------------------------------
	def onPlaceTrap( self, controllerID, userData ):
		"""
		timer for place trap
		called by MONENMITY_ADD_TRAP_TIMER_CBID
		"""
		if self.queryTemp( "proximityID", 0 ) == 0:# 如果怪物是主动攻击类型的
			self.setTemp( "test_Proximity", True )								# 这个设置主要是要处理刚放陷阱就被entity进入导致onEnterTrapExt马上调用的情况
			id = self.addProximityExt( self.initiativeRange )						# 则添加一个陷阱，当有entity进入陷阱时，onEnterTrapExt()会自动被调用
			if self.queryTemp( "test_Proximity", False ):
				self.setTemp( "proximityID", id )
				self.removeTemp( "test_Proximity" )

	def checkEnterTrapEntityType( self, entity ):
		"""
		virtual method.
		检查进入陷阱的entity类型
		"""
		# 是否为敌对关系
		#if self.queryRelation( entity ) != csdefine.RELATION_ANTAGONIZE:
		#	return False

		if not self.isWitnessed and not self.hasFlag( csdefine.ENTITY_FLAG_MONSTER_THINK ):
			return False

		if not isinstance( entity, CombatUnit ):
			return False

		# 注意：getState()取得的状态不一定是real entity的状态
		plState = entity.getState()
		# 玩家处于销毁状态或死亡状态，什么也不做
		if plState == csdefine.ENTITY_STATE_PENDING or plState == csdefine.ENTITY_STATE_QUIZ_GAME or plState == csdefine.ENTITY_STATE_DEAD:
			return False

		state = self.getState()
		if state != csdefine.ENTITY_STATE_FREE and state != csdefine.ENTITY_STATE_REST:
			return False

		# 不在有效攻击范围内，什么也不做
		if entity.position.distTo( self.getSpawnPos() ) > self.territory:
			return False

		# 潜行相关，是否侦测到目标
		if not self.isRealLook( entity.id ):
			return False

		return True
	
	def getSpawnPos( self ):
		return self.spawnPos
	
	def activeTriggerTrap( self ):
		"""
		怪物主动触发自己的攻击陷阱
		"""
		es = self.entitiesInRangeExt( self.initiativeRange, None, self.position )
		for e in es:
			# 暂时只检测角色和宠物
			if not e.getEntityType() in [csdefine.ENTITY_TYPE_ROLE, csdefine.ENTITY_TYPE_PET]: continue
			range = self.position.flatDistTo( e.position )
			self.triggerTrap( e.id, range )

	def triggerTrap( self, entityID, range ):
		"""
		define method.
		主动触发怪物的陷阱
		例如：使用引路蜂传送到怪物周围后， 传送保护buff结束会触发这里
		"""
		state = self.getState()
		if state == csdefine.ENTITY_STATE_FIGHT:
			return

		proximityID = self.queryTemp( "proximityID", 0 )
		if proximityID != 0 and self.initiativeRange >= range:
			entity = BigWorld.entities.get( entityID )
			if entity:
				self.onEnterTrapExt( entity, range, proximityID )

	def _onRemoveFirstAttacker( self ):
		"""
		当需要把self.bootyOwner[0]置为0时应该调用此方法来检查当前的attacker是否存在于队伍中。
		所有者规则：进入战斗状态后第一个产生伤害动作的目标将被作为所有者，如果这个目标在队伍中，则以队伍为所有者。
		如果敌意消失，则丢失所有者身份，队伍情况是对所有队伍成员的敌意都消失则丢失。
		"""
		if self.bootyOwner[1] != 0:										# 存在于队伍中
			bwe = BigWorld.entities
			for e in self.enemyList:
				try:
					obj = bwe[e]
				except KeyError:
					continue

				if obj.isEntityType( csdefine.ENTITY_TYPE_PET ) or obj.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
					enemyTeam = obj.getTeamMailbox()
					if enemyTeam is not None and enemyTeam.id == self.bootyOwner[1]:
						self.bootyOwner = ( e, enemyTeam.id )							# 如果还有存在于队伍的敌人则选一个
						return

		self.bootyOwner = ( 0, 0 )

	def addEnemyCheck( self, entityID ):
		"""
		extend method.
		"""
		if not CombatUnit.addEnemyCheck( self, entityID ):
			return False
		
		entity = BigWorld.entities[entityID]
		
		if self.getSubState() == csdefine.M_SUB_STATE_GOBACK:
			return False
		
		if self.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ):		#不可被选择的怪物，允许其他怪物攻击他，不允许玩家和宠物攻击他
			if entity.isEntityType( csdefine.ENTITY_TYPE_PET ) or entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				return False
		
		return True

	def addDamageList( self, entityID, damage ):
		"""
		添加伤害列表
		@param entityID  : entityID
		@param damage	 : 伤害值
		"""
		# 如果回走状态 则忽略任何敌人
		if self.getSubState() == csdefine.M_SUB_STATE_GOBACK:
			return
		CombatUnit.addDamageList( self, entityID, damage )

	def onRemoveEnemy( self, entityID ):
		"""
		"""
		CombatUnit.onRemoveEnemy( self, entityID )
		if self.targetID == entityID:		# 如果删除的是当前攻击目标则必须改变攻击目标
			self.targetID = 0
			self.doAllEventAI( csdefine.AI_EVENT_ATTACKER_ON_REMOVE )

		if self.bootyOwner[0] == entityID:
			self._onRemoveFirstAttacker()	# 丢失战利品的拥有者
			if self.bootyOwner == ( 0, 0 ) :
				self.onBootyOwnerChanged()

	def resetEnemyList( self ):
		"""
		重置所有敌人信息表
		"""
		CombatUnit.resetEnemyList( self )
		# 敌人信息都没有了 重置
		self.targetID = 0
		self.firstBruise = 0
		isChanged = self.bootyOwner != ( 0, 0 )
		self.bootyOwner = ( 0, 0 )
		if isChanged :
			self.onBootyOwnerChanged()

	def addCureList( self, entityID, cure ):
		"""
		添加治疗列表
		@param entityID  : entityID
		@param cure		 : 治疗值
		"""
		# 如果回走状态 则忽略任何敌人
		if self.getSubState() == csdefine.M_SUB_STATE_GOBACK:
			return
		CombatUnit.addCureList( self, entityID, cure )

	def exitFight( self ):
		"""
		脱离战斗， 由外部调用决定强制脱离
		"""
		self.doGoBack()

	def onViewRange( self ):
		"""
		视野范围
		清理已经不在视野内的所有敌人 只有在战斗状态时才进行检测
		return :None
		"""
		bwe = BigWorld.entities
		eids = []
		for eid, val in self.enemyList.iteritems():
			if not bwe.has_key( eid ):
				eids.append( eid )
				continue
			e = bwe[eid]
			#如果不在自己的视野范围内
			if not self.checkViewRange( e ) or e.getState() == csdefine.ENTITY_STATE_DEAD:
				eids.append( eid )

		if len( eids ) <= 0:
			return
		
		g_fightMgr.breakGroupEnemyRelationByIDs( self, eids )


	#-----------------------------------------------------------------------------------------------------
	# 怪物当前目标相关
	#-----------------------------------------------------------------------------------------------------
	def changeAttackTarget( self, newTargetID ):
		"""
		改变攻击目标
		@param newTargetID: 目标entityID
		@type  newTargetID: OBJECT_ID
		@return:            无
		"""
		state = self.getState()
		subState = self.getSubState()
		if state == csdefine.ENTITY_STATE_DEAD or subState == csdefine.M_SUB_STATE_GOBACK:
			return

		target = BigWorld.entities.get( newTargetID )
		if not target or target.spaceID != self.spaceID:
			self.onChangeTargetFailed( newTargetID )
			return

		if self.targetID == newTargetID:
			return 
			
		if self.queryRelation( target ) != csdefine.RELATION_ANTAGONIZE:
			DEBUG_MSG( "RelationError: self.className = %s" % ( self.className ) )

		oldEnemyID = self.targetID
		self.targetID = newTargetID

		if self.isMoving():
			self.stopMoving()


		DEBUG_MSG( "%i: oldEnemy = %i, targetID = %i, current state = %i" % (self.id, oldEnemyID, self.targetID, state) )
		if state == csdefine.ENTITY_STATE_FREE or state == csdefine.ENTITY_STATE_REST:
			if self.getScript().hasPreAction and self.firstHide:
				jumpPointType = self.getScript().jumpPointType
				jumpPoint = self.getScript().jumpPoint
				target_pos = self.getDstPos( jumpPointType, jumpPoint )
				isMovedAction = self.getScript().isMovedAction
				preActionTime = self.getScript().preActionTime
				time = self.doPreEvent( target_pos, isMovedAction, preActionTime )
				self.addTimer( time, 0, ECBExtend.PRE_TO_FIGHT_STATE )
				return
			self.changeState( csdefine.ENTITY_STATE_FIGHT )

		self.onChangeTarget( oldEnemyID )	# 回调，改变攻击目标

	def preRemoveFlag( self,timerID, cbID ):
		"""
		移除标志位
		"""
		self.removeFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE )
	
	def preToFightState( self, timerID, cbID ):
		"""
		在自由状态里有了攻击目标则改变为战斗状态过程
		如果怪物有入场动作，则表现入场动作
		自由状态下 进入预战斗状态,播放预战斗状态动作
		动画和位移结束后重新进入战斗状态
		"""
		state = self.getState()
		subState = self.getSubState()
		if state == csdefine.ENTITY_STATE_DEAD or subState == csdefine.M_SUB_STATE_GOBACK:
			return
		target = BigWorld.entities.get( self.targetID )
		if not target or target.spaceID != self.spaceID:
			self.onChangeTargetFailed( self.targetID )
			return
		self.removeTemp("pre_speed")
		self.removeFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE )
		self.changeState( csdefine.ENTITY_STATE_FIGHT )	# 在自由状态里有了攻击目标则改变为战斗状态
		self.onChangeTarget( self.targetID )

	def doPreEvent( self, target_pos, isMovedAction, preActionTime ):
		"""
		执行预攻击事件
		"""
		self.firstHide = False
		self.rotateToTarget()
		if isMovedAction : 				 # 有位移的入场动画
			pre_speed = self.queryTemp("pre_speed",20.0)				# 播放入场动作怪物的速度
			self.addFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE )
			pos_vect3 = Math.Vector3( self.position - target_pos )
			dist = pos_vect3.length
			pre_time = dist/pre_speed						# 播放入场动画持续的时间
			self.playActionToPoint( target_pos, pre_speed )
			return dist/pre_speed
		else :                                        # 没有位移的入场动画
			self.addFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE )
			self.planesAllClients( "playAdmissionAction", () )
			return preActionTime + 0.1			# 容许延迟时间0.1s
			
	def getDstPos( self, jumpPointType, jumpPoint ):
		"""
		获取落地点目标位置
		"""
		target = BigWorld.entities.get( self.targetID )
		if not target:
			return
		if jumpPointType == 0 :
			return target.position
		elif jumpPointType == 1:
			try:
				radius = int( jumpPoint )
			except:
				DEBUG_MSG("%s:jumpPointType is error" % ( self.className ))
				return target.position
			target_pos = target.position + Math.Vector3(random.random() * radius * 2 - radius, 0, random.random() * radius * 2 - radius )
			return csarithmetic.getCollidePoint( self.spaceID, target.position, target_pos )
		elif jumpPointType == 2:
			return Math.Vector3( eval( jumpPoint ) )
		else:
			dst = float( jumpPoint )
			pos =  csarithmetic.getSeparatePoint3( target.position, self.position, dst )
			return csarithmetic.getCollidePoint( self.spaceID, target.position, pos )

	def playActionToPoint(self, position, speed ):
		"""
		播放动作到某个位置
		"""
		self.planesAllClients( "actionToPoint", ( position, speed ) )
		self.openVolatileInfo()
		self.position = position


	def onChangeTarget( self, oldEnemyID ):
		"""
		告诉其它人，当前的攻击目标改变；可以被派生，但继承者必须先调用这个方法后再判断其它相关值才是正确的。
		这里有几种可能性：1.如果oldEnemyID为0即表示它之前没有攻击目标；2.如果self.targetID为0即表示攻击目标丢失
		@param oldEnemyID: 旧的攻击目标
		@type  oldEnemyID: OBJECT_ID
		@return: 无
		"""
		target = BigWorld.entities.get( self.targetID )
		if target:
			g_fightMgr.buildEnemyRelation( self, target )
		self.getScript().onChangeTarget( self, oldEnemyID )

	def onChangeTargetFailed( self, newTargetID ):
		"""
		改变目标失败通知
		"""
		target = BigWorld.entities.get(newTargetID)
		if target:
			g_fightMgr.breakEnemyRelation( self, target )

	def checkAttackTarget( self, entityID ):
		"""
		检查攻击目标时的一些有效性判断
		@param entityID: 攻击目标的entityID
		@type  entityID: OBJECT_ID
		@return:       无
		"""
		distance = self.position.flatDistTo( self.getSpawnPos() )	#取得自己和出生点距离
		#在活动领域外就清除敌人 至于是否回走或追打是怪物战斗AI的事情
		if distance > self.territory:
			self.exitFight()		# 按策划要求 超出领域范围直接重置。

	#-----------------------------------------------------------------------------------------------------
	# 怪物sub相关
	#-----------------------------------------------------------------------------------------------------
	# 怪物sub状态
	def changeSubState( self, state ):
		"""
		改变sub状态
		@param state: 状态
		@type  state: INT16
		@return:   无
		"""
		if self.getSubState() == state:
			return
		self.setTemp( "old_subState", self.subState )
		self.subState = state
		self.doAllEventAI( csdefine.AI_EVENT_SUBSTATE_CHANGED )

	def getOldSubState( self ):
		"""
		获得旧的sub状态
		@return:   sub状态
		"""
		return self.queryTemp( "old_subState" )

	def getSubState( self ):
		"""
		取sub状态
		@return:   sub状态
		"""
		return self.subState

	def canThink( self ):
		"""
		virtual method.
		判定是否可以think
		"""
		return self.getScript().canThink( self )

	# 思考
	def onThink( self ):
		"""
		virtual method.
		"""
		if not self.canThink():
			return
		if self.state == csdefine.ENTITY_STATE_FIGHT:
			CPU_CostCal( csdefine.CPU_COST_AI, csdefine.CPU_COST_AI_FIGHT, self.className )
			self.onFightAIHeartbeat()
			CPU_CostCal( csdefine.CPU_COST_AI, csdefine.CPU_COST_AI_FIGHT, self.className )
		else:
			#非战斗状态下，心跳速度降低
			CPU_CostCal( csdefine.CPU_COST_AI, csdefine.CPU_COST_AI_FREE, self.className )
			self.onNoFightAIHeartbeat()
			CPU_CostCal( csdefine.CPU_COST_AI, csdefine.CPU_COST_AI_FREE, self.className )

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
					else:
						if self.canPatrol:
							self.doPatrol( self.patrolPathNode, self.patrolList )

		self.setThinkSpeed()
		if not self.isDestroyed and self.isReal():
			self.think( self.thinkSpeed )

	def onSpecialAINotDo( self ):
		"""
		特殊AI执行失败要做的处理
		"""
		if not self.isMoving() and self.hasFlag( csdefine.ENTITY_FLAG_RAD_FOLLOW ) and not self.actionSign( csdefine.ACTION_FORBID_MOVE ):			# 执行游荡
			target = BigWorld.entities.get( self.targetID )
			if not target:
				return
			if self.queryTemp( "roundTime", None ) and time.time() - self.queryTemp( "roundTime", time.time() ) < Const.ROUND_TIME_LIMIT:
				return
			self.setTemp( "roundTime", time.time() )
			distance = self.distanceBB( target )
			
			if distance < Const.ROUND_MIN_DIS:
				self.moveBack( self.targetID, distance - Const.ROUND_MIN_DIS - 1 )		# 多退后一米，保证退到游荡范围内
			elif distance <= Const.ROUND_MAX_DIS:
				ang = random.choice( [-90, -60, 60, 90] )
				self.moveRadiFollow( self.targetID, ang, ( Const.ROUND_MIN_DIS,  Const.ROUND_MAX_DIS ) )
			else:
				self.chaseTarget( target, Const.ROUND_MAX_DIS - 1 )

	def doGoBack( self ):
		"""
		移动回作战位置
		"""
		if self.state == csdefine.ENTITY_STATE_DEAD:
			return

		self.changeSubState( csdefine.M_SUB_STATE_GOBACK )
		# changeSubState 会触发AI， 可能造成死亡
		if self.isDestroyed or self.state == csdefine.ENTITY_STATE_DEAD:
			return

		if not self.hasFlag( csdefine.ENTITY_FLAG_NOT_FULL ):		# 如果有标记则不回血回蓝
			self.full()
		self.clearBuff( [csdefine.BUFF_INTERRUPT_NONE] )
		self.resetEnemyList()

		if self.isMovingType( Const.MOVE_TYPE_PATROL ) or not self.getScript().doGoBack( self ):
			# 回走失败， 直接拉回出生点， 统一由onMovedOver内处理，
			# 因为并不一定第一次移动即失败
			self.onMovedOver( False )

		if self.move_speed < 0.001:
			self.onMovedOver( False )


	def doFlee( self ):
		"""
		逃跑
		"""
		if self.actionSign( csdefine.ACTION_FORBID_MOVE ):
			DEBUG_MSG( "im cannot the move!" )
			self.stopMoving()
			return

		# 改为逃跑状态
		self.changeSubState( csdefine.M_SUB_STATE_FLEE )

		# 移动
		if not self.doRandomRun( self.position, 5 ):
			#self.think( 5.0 )
			pass # 由于think实现机制被改变，逃跑暂时没有用到， 逃跑失败是要停顿5秒的，将来实现需要考虑

	def doRandomWalk( self ):
		"""
		随机转悠处理
		"""
		# 改为走路状态
		self.changeSubState( csdefine.M_SUB_STATE_WALK )
		# 随机取点 散步
		rnd = random.random()
		a = self.randomWalkRange * rnd
		b = 2*math.pi * rnd
		x = a * math.cos( b ) #半径 * 正余玄
		z = a * math.sin( b )
		pos = Math.Vector3( self.getSpawnPos() )
		pos.x += x
		pos.z += z

		# 散步移动
		self.gotoPosition( pos )

	# 呼叫帮手
	def onFightCall( self, targetID, className ):
		"""
		define method.
		战斗呼叫
		@param  targetID: 攻击目标ID
		@type   targetID: OBJECT_ID
		@param className: 呼叫者的类型（或者说是呼叫类型）
		@type  className: STRING
		"""
		if self.queryTemp( "callSign", True ):
			return

		if self.getSubState() != csdefine.M_SUB_STATE_GOBACK and self.getState() != csdefine.ENTITY_STATE_DEAD and self.getState() != csdefine.ENTITY_STATE_FIGHT:
			try:
				enemy = BigWorld.entities[ targetID ]
			except:
				WARNING_MSG( className, self.className, "target not found.", targetID )
				return

			self.setTemp( "callSign", True )
			g_fightMgr.buildEnemyRelation( self, enemy )


	def chaseTarget( self, entity, distance ):
		"""
		virtual method.
		追踪一个entity；
		注意: 底层的chaseEntity在monster层不可直接使用，monster追击一个目标应该使用本接口
		@param   entity: 被追赶的目标
		@type    entity: Entity
		@param distance: 离目标entity多远的距离停下来(米/秒)
		@type  distance: FLOAT
		@return: 返回此次接口调用是否成功
		@rtype:  BOOL
		"""
		if entity.isDestroyed or self.isDestroyed:
			return False

		if self.move_speed < 0.001:
			return False

		self.setTemp( "firstAttackAfterChase", 0 )

		# 使用与技能相匹配的距离计算公式
		dist = entity.getBoundingBox().z / 2 + distance + self.getBoundingBox().z / 2
		if self.getGroundPosition().distTo( entity.getGroundPosition() ) <= dist:
			return True
		elif self.chaseEntity( entity, dist ):
			self.changeSubState( csdefine.M_SUB_STATE_CHASE )
			if entity.isDestroyed or self.isDead():return False
			self.pathNotFindNum = 0
			return True

		if self.pathNotFindNum>3: #失败的次数超过一定的次数（3， 待定）
			self.pathNotFindNum = 0
			self.position = Math.Vector3( self.getSpawnPos() )
			self.doGoBack()
			ERROR_MSG( "Monster(NPC)'s className(%s,%s) can not find path to chase target!"%(self.className,self.getName()), "my position =", self.position, "target position =", entity.position, "distance =", distance, "Monster SpaceName=", self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), "entity SpaceName=", entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )   )
			return False

		self.pathNotFindNum += 1
		self.changeSubState(csdefine.M_SUB_STATE_CONTINUECHASE)
		if entity.isDestroyed or self.state == csdefine.ENTITY_STATE_DEAD:return False
		self.setTemp( "GSChaseEntityID", entity.id )
		self.setTemp( "GSChaseEntityDistance", distance )
		self.doRandomRun( entity.position, distance )
		return True

	#-----------------------------------------------------------------------------------------------------
	# 受到伤害
	#-----------------------------------------------------------------------------------------------------
	def receiveSpell( self, casterID, skillID, param1, param2, param3 ):
		"""
		Define method.
		接受技能处理

		@type   casterID: OBJECT_ID
		@type    skillID: INT
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		state = self.getState()
		subState = self.getSubState()
		# 回走状态时，无敌状态 死亡了
		if subState == csdefine.M_SUB_STATE_GOBACK or state == csdefine.ENTITY_STATE_DEAD or \
		( BigWorld.entities.has_key( casterID ) and BigWorld.entities[ casterID ].getState() == csdefine.ENTITY_STATE_DEAD ):
			return

		if self.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ):
			return

		if self.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ):
			if self.ownerVisibleInfos != (0,0):
				pid = self.ownerVisibleInfos[0]
				tid = self.ownerVisibleInfos[1]
				obj = BigWorld.entities.get( casterID )
				if not obj:
					if pid != casterID:
						return
				else:
					if obj.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
						if not obj.teamMailbox:
							if pid != casterID:
								return
						else:
							if pid != casterID or tid != obj.teamMailbox.id:
								return

		CombatUnit.receiveSpell( self, casterID, skillID, param1, param2, param3 )	# 通知底层

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
				# 记录第一次受击
				if not self.firstBruise:
					if killerEntity.utype in [csdefine.ENTITY_TYPE_PET, csdefine.ENTITY_TYPE_ROLE, csdefine.ENTITY_TYPE_SLAVE_MONSTER, \
						csdefine.ENTITY_TYPE_VEHICLE_DART, csdefine.ENTITY_TYPE_CALL_MONSTER, csdefine.ENTITY_TYPE_PANGU_NAGUAL ]: # added by dqh
						self.firstBruise = 1
						# 如果有队伍则记录队伍mailbox
						getEnemyTeam = getattr( killerEntity, "getTeamMailbox", None )	# hyw
						if getEnemyTeam and getEnemyTeam():
							self.bootyOwner = ( casterID, getEnemyTeam().id )
							DEBUG_MSG("The fatcTeam is ----->>>>> %s" % getEnemyTeam().id )
						else:
							# 进入战斗状态后第一个产生伤害目标将被作为所有者
							self.bootyOwner = ( casterID, 0 )
							DEBUG_MSG("The firstAttacker is ----->>>>> %s" % casterID )
						# 第一次受击事件
						self.onBootyOwnerChanged()
						self.onFirstBruise( killerEntity, damage, skillID )
		else:
			# 没有攻击源或伤害是buff产生
			pass
		self.getScript().receiveDamage( self, casterID, skillID, damageType, damage )
		# 最后通知底层，因为如果先通知了底层，那么当怪物被一击必杀的时候很可能它根本就没进入战斗状态
		# 如果是这样的话，有些东西就不可能生效或会出错。
		CombatUnit.receiveDamage( self, casterID, skillID, damageType, damage )

	def addBuff( self, buff ):
		"""
		添加一个Buff。

		@param buff			:	instance of BUFF
		@type  buff			:	BUFF
		"""
		state = self.getState()
		subState = self.getSubState()
		# 回走状态时，无敌状态 死亡了
		if subState == csdefine.M_SUB_STATE_GOBACK or state == csdefine.ENTITY_STATE_DEAD:
			return
		CombatUnit.addBuff( self, buff )	# 通知底层
		self.doAllEventAI( csdefine.AI_EVENT_ADD_REMOVE_BUFF )

	def removeBuff( self, index, reasons ):
		"""
		从列表中去除一个Buff并通知客户端。
		@param index: BUFF所在的索引
		@param reasons:请求取消该BUFF的理由
		"""
		if self.isDestroyed:
			return
		CombatUnit.removeBuff( self, index, reasons )
		self.doAllEventAI( csdefine.AI_EVENT_ADD_REMOVE_BUFF )

	def doAttackerOnHit( self, receiver, damageType ):
		"""
		在命中后（即获得伤害后，这时人可能已经挂了）被触发，主要用于一些需要在命中后再触发的效果；

		适用于：
		    击中目标时$1%几率给予目标额外伤害$2
		    击中目标时$1%几率使目标攻击力降低$2，持续$3秒
		    被击中时$1几率恢复$2生命
		    被击中时$1%几率提高闪避$2，持续$3秒
		    etc.
		@param skill:技能实例
		@type skill: SKILL
		@param caster:施法者
		@type caster: ENTITY
		"""
		CombatUnit.doAttackerOnHit( self, receiver, damageType )
		self.doAllEventAI( csdefine.AI_EVENT_SKILL_HIT )

	def doVictimOnHit( self, caster, damageType ):
		"""
		在被命中后（即获得伤害后，这时人可能已经挂了）被触发，主要用于一些需要在被命中后再触发的效果；

		适用于：
		    被击中目标时$1%几率给予目标额外伤害$2
		    etc.
		@param skill:技能实例
		@type skill: SKILL
		@param caster:施法者
		@type caster: ENTITY
		"""
		CombatUnit.doVictimOnHit( self, caster, damageType )
		self.doAllEventAI( csdefine.AI_EVENT_SKILL_RECEIVE_HIT )

	def onAttackerMiss( self, receiver, damageType ):
		"""
		攻击者未命中
		"""
		CombatUnit.onAttackerMiss( self, receiver, damageType )
		self.doAllEventAI( csdefine.AI_EVENT_SKILL_MISS )

	def doAttackerOnDoubleHit( self, receiver, damageType ):
		"""
		在产生物理暴击时（即获得伤害后，这时人可能已经挂了）被触发
		@param skill:技能实例
		@type skill: SKILL
		@param caster:施法者
		@type caster: ENTITY
		"""
		CombatUnit.doAttackerOnDoubleHit( self, receiver, damageType )
		self.doAllEventAI( csdefine.AI_EVENT_SKILL_DOUBLEHIT )

	def doVictimOnDoubleHit( self, caster, damageType ):
		"""
		在被物理暴击时（即获得伤害后，这时人可能已经挂了）被触发
		@param skill:技能实例
		@type skill: SKILL
		@param caster:施法者
		@type caster: ENTITY
		"""
		CombatUnit.doVictimOnDoubleHit( self, caster, damageType )
		self.doAllEventAI( csdefine.AI_EVENT_SKILL_RECEIVE_DOUBLEHIT )

	def doAttackerOnResistHit( self, receiver, damageType ):
		"""
		在目标招架成功时（即获得伤害后，这时人可能已经挂了）被触发
		@param skill:技能实例
		@type skill: SKILL
		@param caster:施法者
		@type caster: ENTITY
		"""
		CombatUnit.doAttackerOnResistHit( self, receiver, damageType )
		self.doAllEventAI( csdefine.AI_EVENT_SKILL_RESISTHIT )

	def spellTarget( self, skillID, targetID ):
		"""
		向一个entity施法
		@param  skillID: 法术标识符
		@type   skillID: INT16
		@param targetID: 目标entityID
		@type  targetID: OBJECT_ID
		"""
		if self.getSubState() == csdefine.M_SUB_STATE_GOBACK:	# 回走状态下不能施法
			return csstatus.SKILL_NO_MSG

		return CombatUnit.spellTarget( self, skillID, targetID )

	#-----------------------------------------------------------------------------------------------------
	# 怪物死亡销毁
	#-----------------------------------------------------------------------------------------------------
	def beforeDie( self, killerID ):
		"""
		virtual method.
		"""
		return True

	def afterDie( self, killerID ):
		"""
		virtual method.
		"""
		self.getScript().afterDie( self, killerID )

	def onDie( self, killerID ):
		"""
		virtual method.

		死亡事情处理。
		"""
		try:
			self.getScript().onMonsterDie( self, killerID )
		except:
			EXCEHOOK_MSG("onMonsterDie wrong")
			sys.excepthook(*sys.exc_info())
		self.doAllEventAI( csdefine.AI_EVENT_ENTITY_ON_DEAD )

		if self.getCurrentSpaceBase() != None:
			self.getCurrentSpaceBase().subMonsterCount()


	def onCorpseDelayTimer( self, controllerID, userData ):
		"""
		MONSTER_CORPSE_DELAY_TIMER_CBID的callback函数；
		"""
		self.destroy()

	def onDestroy( self ):
		"""
		entity 销毁的时候由BigWorld.Entity自动调用
		"""
		self.doAllEventAI( csdefine.AI_EVENT_ENTITY_ON_DESTROY )
		NPCObject.onDestroy( self )


	#-----------------------------------------------------------------------------------------------------
	# 怪物战利品相关
	#-----------------------------------------------------------------------------------------------------
	def getBootyOwner( self ):
		"""
		获得战利品的拥有者
		"""
		return self.getScript().getBootyOwner( self )

	def calculateBootyOwner( self ):
		"""
		取得战利品的拥有者；
		建议在怪物死亡时（即在onDie()时）再调用此方法，否则如果拥有者不存在的话计算出来的结果可能会是错误的。

		@return: 无
		"""
		if len( self.bootyOwner ) <= 0:
			self.bootyOwner = ( 0, 0 )
		# 如果所有权是队伍
		elif self.bootyOwner[1]  != 0:
			entities = self.searchTeamMember( self.bootyOwner[1], Const.TEAM_GAIN_EXP_RANGE )
			# 表示队伍解散了
			if len( entities ) == 0:
				# 无所有权
				self.bootyOwner = ( 0, 0 )

		# 如果所有权是个人，判断是否在队伍，移交所有权
		elif self.bootyOwner[0] != 0:
			try:
				entity = BigWorld.entities[self.bootyOwner[0]]
			except KeyError:
				ERROR_MSG( "I hav firstAttacker(%i), but it not exsit." % self.bootyOwner[0] )
				self.bootyOwner = ( 0, 0 )
			else:
				if entity.isEntityType( csdefine.ENTITY_TYPE_PET ) or entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or  entity.isEntityType( csdefine.ENTITY_TYPE_SLAVE_MONSTER ) or entity.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ) or entity.isEntityType( csdefine.ENTITY_TYPE_CALL_MONSTER ) or entity.isEntityType( csdefine.ENTITY_TYPE_PANGU_NAGUAL ):
					if entity.isInTeam():
						self.bootyOwner = ( self.bootyOwner[0], entity.getTeamMailbox().id )	# 指向队伍的ID
				if entity.isEntityType( csdefine.ENTITY_TYPE_PET ) or entity.isEntityType( csdefine.ENTITY_TYPE_SLAVE_MONSTER ) or entity.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ) or entity.isEntityType( csdefine.ENTITY_TYPE_CALL_MONSTER ) or entity.isEntityType( csdefine.ENTITY_TYPE_PANGU_NAGUAL ):
					self.bootyOwner = ( entity.ownerID, self.bootyOwner[1] )

	def onBootyOwnerChanged( self ) :
		"""
		怪物归属权改变
		"""
		self.calculateBootyOwner()
		self.doAllEventAI( csdefine.AI_EVENT_BOOTY_OWNER_CHANGED )
		self.planesAllClients( "onSetBootyOwner", ( self.bootyOwner, ) )	# 向客户端广播

	def queryBootyOwner( self, scrEntityID ) :
		"""
		Exposed method
		客户端申请查询怪物的归属权
		"""
		player = BigWorld.entities.get( scrEntityID, None )
		if player :
			player.clientEntity( self.id ).onSetBootyOwner( self.bootyOwner )


	#-----------------------------------------------------------------------------------------------------
	# 怪物属性其他相关
	#-----------------------------------------------------------------------------------------------------
	def gainReward( self, entity, exp, pot, accum ,daohengAch, campMorale ):
		"""
		获得经验值、潜能、气运、道行
		注意:该接口是对单人进行等级差折算和经验加成的后实际加到単人身上的经验值,组队时计算完组队的折算和加成后,使用该接口才能计算出加到人物身上的最终
		值。
			@param 	entity	:	加经验对像
			@type 	entity	:	Entity
			@param 	exp		:	经验值
			@type 	exp		:	int
		"""
		if entity is None : return

		offset = self.getScript().getExpAmendRate( entity.level - self.level )
		# 经验值偏移计算
		dat = int( exp * offset )
		extra_potential_percent = 0

		# 加入系统多倍经验计算
		if BigWorld.globalData.has_key( "AS_SysMultExp" ) and BigWorld.globalData[ "AS_SysMultExp" ] > 0:
			sysExtraExp = int( BigWorld.globalData[ "AS_SysMultExp" ] * dat )
			dat += sysExtraExp
			extra_potential_percent = BigWorld.globalData[ "AS_SysMultExp" ]

		# 加入角色自身获得的多倍经验计算
		if entity.multExp > 0:
			extraExp = int( entity.multExp * dat )
			dat += extraExp

		if dat > 0:
			entity.addKillMonsterExp( dat )
			if entity.kaStone_SpellID > 0:
				# 记录分配经验人数 技能需要根据人数调整魂魄的数量
				entity.setTemp( "bootyOwnerCount", self.popTemp( "bootyOwnerCount", 1 ) )
				self.spellTarget( entity.kaStone_SpellID,  entity.id )

		# 宠物计算经验只和宠物有关
		actPet = entity.pcg_getActPet()
		if actPet and actPet.etype != "MAILBOX" :
			dat = exp
			if abs( actPet.entity.level - self.level ) > 30:
				dat = exp * 0.5

			# 加入系统多倍经验计算
			if BigWorld.globalData.has_key( "AS_SysMultExp" ) and BigWorld.globalData[ "AS_SysMultExp" ] > 0:
				sysExtraExp = int( BigWorld.globalData[ "AS_SysMultExp" ] * dat )
				dat += sysExtraExp
			# 加入角色自身获得的多倍经验计算
			if entity.multExp > 0:
				extraExp = int( entity.multExp * dat )
				dat += extraExp

			actPet.entity.addEXP( int( dat ) )

		# 潜能奖励偏移计算
		pdat = int( pot * offset )
		if pdat > 0:
			pdat = int( math.ceil( pdat * ( 1 + entity.potential_percent + extra_potential_percent ) ) )
			entity.addPotential( pdat )
			entity.addPotentialBook( pdat )

		# 气运
		spaceKey = entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )
		if accum> 0 and spaceScript.canGetAccum:											# 只有配有canGetAccum为1的地图才能获得气运值
			accumOffset = self.getScript().getAccumAmemdRate( entity.level - self.level )	# 等级修正
			entity.addAccumPoint( accum *  accumOffset * entity.extraAccumRate )			# 气运值 = 怪物拥有气运值 * 组队修正系数 * 等级修正系数 * 难度修正系数
			
		# 道行
		adjust_param = Const.DAOHENG_AMEND_RATE      # 道行调整值，策划备用
		n = entity.getDaoheng() / g_daoheng.get( entity.getLevel() )
		daoheng_n =  adjust_param /(math.log( ( 1 + adjust_param ), math.e ) )  * pow( ( 1+ adjust_param ), -n )  # 道行修正值计算公式k(n)=(a/ln(1+a)) * (1/(1+a)^n)
		daoheng_ach = daoheng_n * daohengAch * offset
		if 0 < daoheng_ach <= 1.0:
			daoheng = 1
		else:
			daoheng =  int ( round ( daoheng_n * daohengAch * offset ) ) 
		entity.addDaoheng( daoheng, csdefine.ADD_DAOHENG_REASON_KILL_MONSTER )
		
		if campMorale > 0:
			BigWorld.globalData[ "CampMgr" ].addMorale( self.getCamp(), campMorale )

	def gainSingleReward( self, gainEntityID ):
		"""
		获得单人杀怪经验
		"""
		killers = []

		try:
			expEntity = BigWorld.entities[ gainEntityID ]
		except:
			WARNING_MSG( "allot Exp ! not find entity. entity id = ", gainEntityID )
		else:
			if not expEntity.state == csdefine.ENTITY_STATE_DEAD:
				# 已死亡者不给予经验
				if expEntity.isEntityType( csdefine.ENTITY_TYPE_PET ) :
					owner = expEntity.getOwner()
					if owner.etype != "MAILBOX" :
						self.gainReward( owner.entity, self.exp, self.potential, self.accumPoint, self.daohengAch, self.campMorale )				# 将怪物的经验分给玩家(个人经验的获取)
						killers = [owner.entity]
				if expEntity.isEntityType( csdefine.ENTITY_TYPE_PANGU_NAGUAL ) :
					owner = expEntity.getOwner()
					if not hasattr( owner, "cell" ) :
						self.gainReward( owner, self.exp, self.potential, self.accumPoint, self.daohengAch, self.campMorale )				# 将盘古守护的经验分给玩家(个人经验的获取)
						killers = [ owner ]
				elif expEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
					self.gainReward( expEntity, self.exp, self.potential, self.accumPoint, self.daohengAch, self.campMorale )					# 将怪物的经验分给玩家(个人经验的获取)
					killers = [ expEntity ]
		return killers

	def calcTeamMemberTongExpRate( self, entities ):
		"""
		计算队伍中的与帮会成员导致经验加成的比率
		"""
		expRates = {}
		tongs = []

		# 找出所有的帮会
		for e in entities:
			if e.tong_dbID > 0:
				tongs.append( e.tong_dbID )

		for e in entities:
			expRate = 0.0
			if e.tong_dbID != 0:
				# 判断帮会的数量策划规定队伍内有1个同帮会成员增加3%经验
				fc = tongs.count( e.tong_dbID ) - 1
				if fc > 0:
					expRate += fc * 0.03

			expRates[ e.id ] = expRate
		return expRates

	def gainTeamReward( self, entities ):
		"""
		组队获得经验值
			@param 	entities	:	加经验对像集
			@type 	entities	:	list
			@param 	exp			:	经验值
			@type 	exp			:	int
		组队后的经验和潜能系数调整到:2个人是0.7，3个人是0.6，4个人是0.55，5个人是0.52
		组队后的气运值系数为：2个人是0.5，3个人是0.35，4个人是0.25，5个人是0.20
		"""
		expRateDict = { 1 : 1.0,
						2 : 0.9,
						3 : 0.67,
						4 : 0.55,
						5 : 0.52,
						}
		accumRateDict = {	1 : 1.0,
							2 : 0.5,
							3 : 0.35,
							4 : 0.25,
							5 : 0.20,
						}

		# 过滤掉已经死亡的人
		for idx in xrange( len( entities ) - 1, -1, -1 ):
			if entities[ idx ].state == csdefine.ENTITY_STATE_DEAD:
				entities.pop( idx )

		count = len( entities )
		if count == 0:
			return

		tongExpRates = self.calcTeamMemberTongExpRate( entities )

		#由于魂魄石吸魂技能计算需要获得当前经验分配的人数, 所以这里怪物总是记录分配人数
		self.setTemp( "bootyOwnerCount", count )

		for e in entities:
			#offset = AmendExp.instance().getLevelRate( e.level - self.level )#和策划讨论后决定等级差不属于组队经验计算考虑的范围，组队经验的计算,应该
			#只考虑组队方面对经验的影响，而等级差属于个人对获取经验的影响。这样可以独立出个人经验计算的模块，避免和组队经验计算相互牵扯. by---hd
			#组队后的经验和潜能系数调整到:2个人是0.7，3个人是0.6，4个人是0.55，5个人是0.52
			#gexp = (( count - 1 ) * 0.1 + 1 ) * exp 		#* offset	# 没有加成前的经验
			#gpot = (( count - 1 ) * 0.1 + 1 ) * pot 		#* offset	# 没有加成前的潜能
			gexp = expRateDict[ count ] * self.exp
			gpot = expRateDict[ count ] * self.potential
			accum = accumRateDict[ count ] * self.accumPoint

			idList = [ mb.id for mb in e.getTeamMemberMailboxs() ]

			# 如果玩家存在师父且满足获得师徒组队额外经验的条件，给玩家加上相应经验
			teachExp = 0.0

			# 将帮会加成增加进去
			tongExp = int( gexp * tongExpRates[ e.id ] )

			# 给玩家加上师徒组队额外经验,gexp * 20%
			if e.hasMaster():
				masterMB = e.getMasterMB()
				if masterMB and masterMB.id in idList:
					master = BigWorld.entities.get( masterMB.id )
					if gexp and master and e.position.flatDistTo( master.position ) <= csconst.TEACH_TEAM_KILL_BENEFIT_DISTANCE and e.spaceID == master.spaceID:
						teachExp = gexp * csconst.TEACH_TEAM_EXP_ADDITIONAL_PERCENT

			# 如果玩家夫妻组队，获得夫妻经验加成,gexp * %10
			loveExp = 0.0
			if e.hasCouple():
				for tempID in idList:
					if e.isCouple( tempID ):
						loveExp = gexp * csconst.COUPLE_TEAM_EXP_PERCENT
						break

			# 玩家结拜关系加成
			allyExp = 0
			if e.hasAllyRelation():
				for tempID in idList:
					if e.checkAllyByID( tempID ):
						allyExp = gexp * csconst.ALLY_TEAM_EXP_PERCENT
						break

			#这里就计算出了受到组队夫妻、帮会、师徒、结拜的影响
			gexp = gexp + teachExp + loveExp + tongExp + allyExp
			self.gainReward( e, gexp, gpot, accum , self.daohengAch, self.campMorale )

	def queryRelation( self, entity ):
		"""
		"""
		return self.getScript().queryRelation( self, entity )

	def calcMoveSpeed( self ):
		"""
		virtual method.
		移动速度
		"""
		# 重载移动速度计算函数，当速度改变时重新进行当前的移动(如果正在移动)
		move_speed = self.move_speed
		CombatUnit.calcMoveSpeed( self )
		if move_speed != self.move_speed:
			self.resetMoving()

	def onWitnessed( self, isWitnessed ):
		"""
		see also Python Cell API::Entity::onWitnessed()
		@param isWitnessed: A boolean indicating whether or not the entity is now witnessed;
		@type  isWitnessed: bool
		"""
		self.getScript().onWitnessed( self, isWitnessed )
		if isWitnessed:
			INFO_MSG( "I in witness, className(%s),ID(%i)." % ( self.className, self.id ) )
			self.think( 0.5 )			# 必须延时think,因为收到这个消息时self.isWitnessed属性值还没改变过来

	def wieldExcData( self ):
		"""
		给怪物装备上附加属性

		@param dataID: 附加属性数据ID
		@type  dataID: INT32
		"""
		# 策划用的扩展属性，用于灵活增加指定NPC的属性
		# 替代旧的怪物装备配置
		dic = g_npcExcData.get( self.getClass(), self.level )
		if len( dic ) == 0: return
		self.physics_dps_value = int( dic["data_dps"] * csconst.FLOAT_ZIP_PERCENT * self.excAtt )
		self.magic_damage_value = int( dic["data_magicDamage"] * self.excAtt )
		self.armor_value = int( dic["data_physicsArmor"] )
		self.magic_armor_value = int( dic["data_magicArmor"] )

		self.wave_dps_value = int( dic["data_dpsWave"] * csconst.FLOAT_ZIP_PERCENT )
		self.hit_speed_value = int( dic["data_speed"] * csconst.FLOAT_ZIP_PERCENT )
		self.range_value = int( dic["data_range"] * csconst.FLOAT_ZIP_PERCENT )

	def setLevel( self, level ):
		"""
		设置怪物等级
		"""
		if level == 0:
			self.level = 1
		else:
			self.level = min( self.getScript().maxLv, level )
		
		self.exp = int( g_npcExp.get( self.level ) * self.getScript()._expRate )
		self.potential = int( g_npcPotential.get( self.level ) * self.getScript()._potentialRate )
		self.accumPoint = int( g_npcAccum.get( self.level ) * self.getScript()._accumRate )
		self.daohengAch = float( g_daohengAch.get( self.level ) * self.getScript()._daohengRate )   # 怪物击杀道行奖励
		self.campMorale = float( g_campMorale[ self.level ] * self.getScript()._campMoraleRate )   # 怪物击杀道行奖励
		#设置道行值
		dh_l = g_daoheng.get( self.level )
		dh = self.getScript()._daohengAtt * dh_l
		dh = max( 1, dh )
		self.setDaoheng( dh )
		#重载属性值，有一些属性值策划需要另外的配置
		attrs = g_monsterIntensifyAttr.getAttrs( self.className, self.level )
		if attrs:
			for i in attrs:
				if hasattr( self, i ):
					setattr( self, i, attrs[i] )
		#针对气运属性重载增加当说填写等级为-1时，重载所有所有等级的怪物的气运值
		attr_accum = g_monsterIntensifyAttr.getAttr( self.className, -1, "accumPoint" )
		if attr_accum:
			setattr( self, "accumPoint", attr_accum )

		# 体质等基础属性的计算必须放在后面，因为baseAtt和excAtt属性也有可能被重载
		dic = g_npcBaseAttr.get( self.getClass(), self.level )
		self.strength_base = dic[ "strength_base" ] * self.baseAtt
		self.dexterity_base = dic[ "dexterity_base" ] * self.baseAtt
		self.intellect_base = dic[ "intellect_base" ] * self.baseAtt
		self.corporeity_base = dic[ "corporeity_base" ] * self.baseAtt
		self.wieldExcData()    # 初始化怪物装备属性,这里改成直接从NPCExcData中获取数据
		# 重新计算属性
		self.calcDynamicProperties()
		# 满血满魔
		self.full()

	#-----------------------------------------------------------------------------------------------------
	# 巡逻相关  kb
	#-----------------------------------------------------------------------------------------------------
	def onPatrolToPointOver( self, command ):
		"""
		virtual method.
		用于onPatrolToPointFinish()函数在ECBExtend模块中的回调处理

		@param command: 巡逻到一个点所得到的命令参数
		"""
		if command != -1:
			ai = g_aiDatas[ command ]
			if self.aiCommonCheck( ai ):
				ai.do( self )

		self.patrolPathNode = self.queryTemp( "patrolPathNode", "" )
		self.think(0.3)
		if BigWorld.time() - self.queryTemp( "patrol_moving_start_time" )  < 0.01:
			return False
		return True

	#-----------------------------------------------------------------------------------------------------
	# 其他回调相关  kb
	#-----------------------------------------------------------------------------------------------------
	def onMovedOver( self, state ):
		"""
		virtual method.
		使用gotoPosition()移动结束通告
		@param state: 移动结果，表示是否成功
		@type  state: bool
		@return:      None
		"""
		AmbulantObject.onMovedOver( self, state )
		subState = self.subState
		self.changeSubState( csdefine.M_SUB_STATE_NONE )

		# changeSubState 可能会触发AI销毁了entity
		if self.isDestroyed:
			return

		if subState == csdefine.M_SUB_STATE_CONTINUECHASE:
			chaseEntityID = self.queryTemp("GSChaseEntityID", 0)
			dst = self.queryTemp("GSChaseEntityDistance", 10)
			try:
				entity = BigWorld.entities[chaseEntityID]
			except KeyError:
				DEBUG_MSG("entity not exist!")
				return
			DEBUG_MSG("==>>Try to chaseEntity again, %i." % entity.id )
			self.chaseTarget( entity, dst )
			return
		elif subState == csdefine.M_SUB_STATE_WALK:
			self.randomWalkTime = random.randint( 0, 10 )	# 随机走动；待在原地一段时间后继续走
			return
		elif subState == csdefine.M_SUB_STATE_GOBACK:
			if not state:										# 如果走不过去则直接跳回
				self.position = Math.Vector3( self.getSpawnPos() )
			self.targetID = 0
			self.resetAI()
			self.setTemp( "callSign", False )
			self.move_speed_base = self.walkSpeed
			self.calcMoveSpeed()
			self.castTrap = True
			self.think( 0.5 )
			if self.patrolList != None:
				self.canPatrol = True
			self.activeTriggerTrap()	# 回走结束触发主动攻击陷阱
		elif subState == csdefine.M_SUB_STATE_FLEE:
			self.onFleeOver()

	# 追击结束事件
	def onChaseOver( self, entity, state ):
		"""
		virtual method.
		使用chaseEntity()移动结束通告
		@param   entity: 被追赶的目标，如果在结束时目标找不到（即目标消失了）则此值为None
		@type    entity: Entity
		@param    state: 移动结果，表示是否成功
		@type     state: bool
		@return:         None
		"""
		AmbulantObject.onChaseOver( self, entity, state )
		# 用于解决一堆怪物追击同一个目标时重叠在一起的问题。
		self.setTemp( "firstAttackAfterChase", 0 )	# 值为0表示是追击刚结束
		self.think(0.1)

	# 释放技能完成事件
	def onSkillCastOver( self, spellInstance, target ):
		"""
		virtual method.
		释放技能完成。

		@param  spellInstance: 技能实例
		@type   spellInstance: SPELL
		@param  target: 技能目标
		@type   target: SkillImplTargetObj
		"""
		CombatUnit.onSkillCastOver( self, spellInstance, target )
		self.setTemp( "last_use_spell", spellInstance.getID() )
		self.doAllEventAI( csdefine.AI_EVENT_SPELL_OVER )

	# 技能被打断事件
	def onSpellInterrupted( self ):
		"""
		当施法被打断时的通知；
		可以通过self.attrIntonateTargetID、self.attrIntonatePosition、self.attrIntonateSkill获得当前的施法目标、位置以及法术实例
		"""
		CombatUnit.onSpellInterrupted( self )
		self.updateTopSpeed()
		self.doAllEventAI( csdefine.AI_EVENT_SPELL_INTERRUPTED )
		# 攻击中断
		#self.think()

	# 逃跑结束事件
	def onFleeOver( self ):
		"""
		逃跑结束
		"""
		pass

	def onFirstBruise( self, killerEntity, damage, skillID ):
		"""
		第一次受击事件

		@param killerEntity: 对你产生伤害的人
		@type  killerEntity: Entity
		@param       damage: 伤害
		@type        damage: int
		@param      skillID: 法术ID
		@type       skillID: INT
		@return:             无
		"""
		if self.isMoving():
			self.stopMoving()

	def onStateChanged( self, old, new ):
		"""
		状态切换。
			@param old	:	更改以前的状态
			@type old	:	integer
			@param new	:	更改以后的状态
			@type new	:	integer
		"""
		CombatUnit.onStateChanged( self, old, new )
		self.getScript().onStateChanged( self, old, new )

		# 如果是第一次攻击，记录做战位置，方便战斗完成后回到该位
		if new == csdefine.ENTITY_STATE_FIGHT:
			self.rotateToTarget()
			self.resetAI()
			self.doAllEventAI( csdefine.AI_EVENT_STATE_CHANGED )
			self.move_speed_base = self.runSpeed
			self.calcMoveSpeed()
			self.think(0.5)
			return
		elif new == csdefine.ENTITY_STATE_FREE:
			if old == csdefine.ENTITY_STATE_FIGHT:					# 如果战斗结束，改变状态为空闲状态
				self.doAllEventAI( csdefine.AI_EVENT_STATE_CHANGED )
				self.doGoBack()
				return
			if old == csdefine.ENTITY_STATE_ENVIRONMENT_OBJECT:
				self.castTrap = True
		self.doAllEventAI( csdefine.AI_EVENT_STATE_CHANGED )
		if new == csdefine.ENTITY_STATE_DEAD:
			if self.isMoving():										# 如果移动则停止
				self.stopMoving()

	def onEnemyListChange( self, entityID ):
		"""
		战斗信息表有改动通知
		"""
		self.aiTargetID = entityID
		self.doAllEventAI( csdefine.AI_EVENT_ENEMY_LIST_CHANGED )
		self.aiTargetID = 0

	def onDamageListChange( self, entityID ):
		"""
		伤害信息表有改动通知
		"""
		self.aiTargetID = entityID
		self.doAllEventAI( csdefine.AI_EVENT_DAMAGE_LIST_CHANGED )
		self.aiTargetID = 0

	def onCureListChange( self, entityID ):
		"""
		治疗信息表有改动通知
		"""
		self.aiTargetID = entityID
		self.doAllEventAI( csdefine.AI_EVENT_CURE_LIST_CHANGED )
		self.aiTargetID = 0

	def onFriendListChange( self, entityID ):
		"""
		友方信息表有改动通知
		"""
		self.aiTargetID = entityID
		self.doAllEventAI( csdefine.AI_EVENT_FRIEND_LIST_CHANGED )
		self.aiTargetID = 0

	def onHPChanged( self ):
		"""
		HP被改变回调
		"""
		CombatUnit.onHPChanged( self )
		self.doAllEventAI( csdefine.AI_EVENT_HP_CHANGED )
		self.getScript().onHPChanged( self )

	def onMPChanged( self ):
		"""
		MP被改变回调
		"""
		CombatUnit.onMPChanged( self )
		self.doAllEventAI( csdefine.AI_EVENT_MP_CHANGED )

	#----------------------------------------------怪物加强属性的融合-------------------------------------------

	def calcPhysicsDPSBase( self ):
		"""
		计算物理DPS_base值
		"""
		pass

	def calcHPMaxBase( self ):
		"""
		real entity method.
		virtual method
		生命上限值基础值
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "HP_Max_base" )
		if val != None:
			self.HP_Max_base = val
			return
		CombatUnit.calcHPMaxBase( self )

	def calcMPMaxBase( self ):
		"""
		real entity method.
		virtual method
		法力上限值基础值
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "MP_Max_base" )
		if val != None:
			self.MP_Max_base = val
			return
		CombatUnit.calcMPMaxBase( self )

	def calcStrengthBase( self ):
		"""
		计算力量基础值
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "strength_base" )
		if val != None:
			self.strength_base = val
			return
		CombatUnit.calcStrengthBase( self )

	def calcDexterityBase( self ):
		"""
		计算敏捷基础值
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "dexterity_base" )
		if val != None:
			self.dexterity_base = val
			return
		CombatUnit.calcDexterityBase( self )

	def calcIntellectBase( self ):
		"""
		计算智力基础值
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "intellect_base" )
		if val != None:
			self.intellect_base = val
			return
		CombatUnit.calcIntellectBase( self )

	def calcCorporeityBase( self ):
		"""
		计算体质基础值
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "corporeity_base" )
		if val != None:
			self.corporeity_base = val
			return
		CombatUnit.calcCorporeityBase( self )

	def calcDamageMinBase( self ):
		"""
		计算最小物理攻击力 基础值
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "damage_min_base" )
		if val != None:
			self.damage_min_base = val
			return
		CombatUnit.calcDamageMinBase( self )

	def calcDamageMaxBase( self ):
		"""
		计算最大物理攻击力 基础值
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "damage_max_base" )
		if val != None:
			self.damage_max_base = val
			return
		CombatUnit.calcDamageMaxBase( self )

	def calcMagicDamageBase( self ):
		"""
		virtual method
		法术攻击力
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "magic_damage_base" )
		if val != None:
			self.magic_damage_base = val
			return
		CombatUnit.calcMagicDamageBase( self )

	def calcDodgeProbabilityBase( self ):
		"""
		闪避率 基础值
		角色闪躲对方攻击的几率。普通物理攻击可以被闪避。物理技能攻击和法术技能攻击不能被闪避。闪避成功后，被攻击方本次攻击不受任何伤害。
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "dodge_probability_base" )
		if val != None:
			self.dodge_probability_base = val
			return
		CombatUnit.calcDodgeProbabilityBase( self )

	def calcArmorBase( self ):
		"""
		virtual method
		物理防御值	表示当角色受到物理攻击时，能对此物理攻击力进行削减的能力。
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "armor_base" )
		if val != None:
			self.armor_base = val
			return
		CombatUnit.calcArmorBase( self )

	def calcMagicArmorBase( self ):
		"""
		virtual method
		法术防御值	表示当角色受到法术攻击时，能对此法术攻击力进行削减的能力。
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "magic_armor_base" )
		if val != None:
			self.magic_armor_base = val
			return
		CombatUnit.calcMagicArmorBase( self )

	def calcDoubleHitProbabilityBase( self ):
		"""
		物理爆击率
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "double_hit_probability_base" )
		if val != None:
			self.double_hit_probability_base = val
			return
		CombatUnit.calcDoubleHitProbabilityBase( self )

	def calcMagicDoubleHitProbabilityBase( self ):
		"""
		法术爆击率
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "magic_double_hit_probability_base" )
		if val != None:
			self.magic_double_hit_probability_base = val
			return
		CombatUnit.calcMagicDoubleHitProbabilityBase( self )

	def changeToNPC( self ):
		"""
		变成NPC
		"""
		self.addFlag( csdefine.ENTITY_FLAG_SPEAKER )
		self.setTemp( "state_npc_speaker", True )
		self.setDefaultAILevel( 0 )
		self.setNextRunAILevel( 0 )
		self.changeState( csdefine.ENTITY_STATE_FREE )
		self.utype = csdefine.ENTITY_TYPE_NPC

	def changeToMonster( self, level, playerID ):
		"""
		define method
		变成怪物（针对已经变成NPC来说的）
		"""
		self.utype = csdefine.ENTITY_TYPE_MONSTER
		self.removeFlag( csdefine.ENTITY_FLAG_SPEAKER )
		self.setTemp( "state_npc_speaker", False )
		self.attrAINowLevel = 1
		
		player = BigWorld.entities.get( playerID, None )

		if player:
			g_fightMgr.buildEnemyRelation( self, player )

		self.setDefaultAILevel( 1 )
		self.setNextRunAILevel( 1 )
		self.setLevel( level )
		self.setTemp( "lastLevel", level )


	def requestTakeLevel( self, srcEntityID ):
		"""
		Exposed method.
		客户端申请获得携带等级数据
		"""
		player = BigWorld.entities.get( srcEntityID )
		if player is None or not self.hasFlag( csdefine.ENTITY_FLAG_CAN_CATCH ):
			return
		player.clientEntity( self.id ).receiveTakeLevel( self.getScript().takeLevel )

	def setLeftHandNumber( self, modelNumber ):
		"""
		define method.
		设置左手模型
		"""
		self.lefthandNumber = modelNumber
		self.planesAllClients( "onSetLeftHandNumber", ( modelNumber, ) )

	def setRightHandNumber( self, modelNumber ):
		"""
		define method.
		设置右手模型
		"""
		self.righthandNumber = modelNumber
		self.planesAllClients( "onSetRightHandNumber", ( modelNumber, ) )


	def farDestroy( self ):
		"""
		define method
		远程销毁
		"""
		self.resetEnemyList()
		self.destroy()

	def setBattleCamp( self, battleCamp ):
		"""
		define method
		玩家阵营被改变
		"""
		self.battleCamp = battleCamp
		self.doAllEventAI( csdefine.AI_EVENT_CHANGE_BATTLECAMP )


	def intonate( self, skill, target, time ):
		"""
		让怪物去吟唱一个技能，并广播给allClients；

		@param    skill: instance of Spell
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: BOOL；如果已经在吟唱则返回False，否则返回True
		"""
		if self.actionSign( csdefine.ACTION_FORBID_INTONATING ):
			self.statusMessage( csstatus.SKILL_FORBID_INTONATING )
			return False

		if self.attrIntonateTimer > 0:
			return False

		if self.attrHomingSpell:
			self.delHomingSpell( csstatus.SKILL_INTERRUPTED_BY_SPELL_2 )

		intonateTime = time
		self.attrIntonateTimer = self.addTimer( intonateTime, 0, ECBExtend.INTONATE_TIMER_CBID )
		# 记录intonate结束后需要用到的参数
		self.attrIntonateSkill = skill
		self.attrIntonateTarget = target
		self.setTemp( "RANDOM_WALK_RANGE", self.randomWalkRange )
		self.randomWalkRange = 0 #避免未进入战斗状态使用吟唱技能 会移动
		self.stopMoving()

		self.planesAllClients( "intonate", ( skill.getID(), intonateTime, target ) )
		return True

	def onIntonateOver( self, controllerID, userData ):
		"""
		timer callback.
		see also Entity.onTimer() method.

		在此处，我们需要找到相应的skill，并调用skill.use()方法进行施放法术。
		"""
		target = self.attrIntonateTarget

		#INFO_MSG( "--> %i: spellID = %i, targetID = %i, position =" % ( self.id, self.attrIntonateSkill.getID(), targetID ), position  )
		skill = self.attrIntonateSkill
		state = skill.castValidityCheck( self, target )
		if state != csstatus.SKILL_GO_ON:
			self.interruptSpell( state )
			return

		# 重置attrIntonateSkill(吟唱)技能，
		# 属性attrIntonateTarget不重置似乎也可以，所以暂时没有重置这些属性。
		self.attrIntonateSkill = None
		self.attrIntonateTimer = 0
		range = self.queryTemp( "RANDOM_WALK_RANGE", 0 )
		self.removeTemp( "RANDOM_WALK_RANGE")
		self.randomWalkRange = range
		self.updateTopSpeed()

		# 开始施放效果
		skill.cast( self, target )

	def rotateToTarget( self ):
		"""
		转向当前目标
		"""
		target = BigWorld.entities.get( self.targetID )
		if not target:
			return
		if self.hasFlag( csdefine.ENTITY_FLAG_CANT_ROTATE_IN_FIGHT_STATE ):
			return

		effectState = csdefine.EFFECT_STATE_FIX | csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_SLEEP
		if not (self.effect_state & effectState) == 0: #禁止转向的判定
			return
		
		disPos = target.position - self.position
		if math.fabs( disPos.yaw ) > 0.0:
			self.rotateToPos( target.position )

	def moveToPosFC( self, endDstPos, targetMoveSpeed, targetMoveFace ):
		"""
		连击移动
		"""
		if self.hasFlag(csdefine.ENTITY_VOLATILE_ALWAYS_CLOSE):return
		self.position = endDstPos
		self.planesAllClients( "moveToPosFC", ( endDstPos, targetMoveSpeed, targetMoveFace ) )
		
	def getOwner( self ):
		"""
		获得所有者
		"""
		return self.getScript().getOwner( self )
		
	def getOwnerID( self ):
		"""
		获得所有者ID
		"""
		return self.getScript().getOwnerID( self )
		
	def setOwner( self, owner ):
		"""
		设置所有者
		"""
		self.getScript().setOwner( self, owner )

	def setThinkSpeed( self, delay = 0 ):
		"""
		设置心跳速度
		"""
		if len( self.nextAIInterval):
			delay = max( self.nextAIInterval )
			if delay > 0:
				self.thinkSpeed = delay
				self.nextAIInterval = []
				return
			self.nextAIInterval = []

		# 战斗状态下
		if self.state == csdefine.ENTITY_STATE_FIGHT:
			self.thinkSpeed = 1.0
		else:
			#非战斗状态下，心跳速度降低
			if self.noFightStateAICount == 0:
				self.thinkSpeed = 5.0
			else:
				self.thinkSpeed = 1.0

	def changeRelationMode( self, type ):
		"""
		由于怪物是通过配置战斗模式来决定的，不需要改变他的静态的战斗模式，所以直接pass
		"""
		pass
		
	def queryGlobalCombatConstraint( self, entity ):
		"""
		查询全局战斗约束
		"""
		return self.getScript().queryGlobalCombatConstraint( self, entity )
		
# Monster.py
