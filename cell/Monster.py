# -*- coding: gb18030 -*-
# Monster.py

"""
����ģ��
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
from DaohengLoader import DaohengLoader     # ��������
from MonsterDaohengLoader import MonsterDaohengLoader  # ���л�ɱ����
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
g_daoheng = DaohengLoader.instance()			# ����
g_daohengAch = MonsterDaohengLoader.instance()

from CPUCal import CPU_CostCal
from Domain_Fight import g_fightMgr


class Monster( NPCObject, AmbulantObject, CombatUnit, AIInterface ):
	"""
	�����࣬������NPC�Ϳ�ս����λ
	"""
	def __init__(self):
		AIInterface.__init__( self )
		AmbulantObject.__init__( self )
		CombatUnit.__init__( self )
		NPCObject.__init__(self)

		self.otherClients.onReviviscence()

		# ��ʱ����

		self.setTemp( "callSign", False )										# ���ù����ʼ��ս�����б�־ Ϊtrue�����ɺ����뱻����
		self.removeTemp( "patrol_stop" )

		# ����Ĭ���ٶ�
		self.move_speed_base = self.walkSpeed									# ���ù����ʼ���ƶ��ٶ�
		self.calcMoveSpeed()													# ��������ƶ��ٶ�
		self.subState = csdefine.M_SUB_STATE_NONE								# ���ù����ʼ��sub״̬
		self.castTrap = False

		# �����Ѳ��NPC�����������AI
		if self.patrolList != None:
			self.canPatrol = True
			# �ȴ�30���ʼѲ�ߣ� self.patrolList��Ҫ�������ʼ�� self.patrolList.isReady()
			self.think( 30.0 )													# ����Ѳ��NPC,Ϊ�˱�֤Ѳ��λ�õ���ȷ��,ֻ�����ϾͿ�ʼthink()

		if self.hasFlag( csdefine.ENTITY_FLAG_MONSTER_THINK ):
			self.think( 2.0 )

		#�����ж�������ȷ���������е��˽������������������Ч������Ҫ�Ǳ���߻���д����
		if self.initiativeRange > 0:
			self.addTimer( 1, 0, ECBExtend.MONENMITY_ADD_TRAP_TIMER_CBID )
			if ( self.initiativeRange + self.randomWalkRange ) > self.territory:
				ERROR_MSG( "Monster(NPC)'s className(%s) initiativeRange + randomWalkRange > territory"%self.className )
		if self.viewRange < self.initiativeRange:
			ERROR_MSG( "Monster(NPC)'s className(%s) viewRange < initiativeRange"%self.className )
		#���ڲ߻����־���������һЩ����Χ������Ұ��ΧΪ500�Ĵ���ֵ�����������ò�̫����
		#��˴�ӡһЩ������Ϣ���Ա�����ܹ�����������Ҳ�����������
		if self.territory > Const.TERRITORY_LIMIT:
			WARNING_MSG( "Monster(NPC)'s className(%s) territory > 100"%self.className )
		if self.viewRange > Const.VIEWRANGE_LIMIT:
			WARNING_MSG( "Monster(NPC)'s className(%s) viewRange > 100"%self.className )

		if self.getCurrentSpaceBase():
			self.getCurrentSpaceBase().addMonsterCount()
		else:
			self.addTimer( 1.0, 0, ECBExtend.DESTROY_SELF_TIMER_CBID ) # �Ҳ���Space Base,��ʱ�����Space�Ѿ�������
			#ERROR_MSG( "Monster(NPC)'s className(%s) create before space create!!"%self.className )
		if self.hasFlag(csdefine.ENTITY_VOLATILE_ALWAYS_OPEN) and self.hasFlag(csdefine.ENTITY_VOLATILE_ALWAYS_CLOSE ):
			ERROR_MSG( "Monster(NPC)'s className(%s) has VOLATILE_ALWAYS_OPEN while flag VOLATILE_ALWAYS_CLOSE is already exist!" % self.className )
		if self.hasFlag(csdefine.ENTITY_VOLATILE_ALWAYS_OPEN):
			self.openVolatileInfo()
		if self.hasFlag(csdefine.ENTITY_VOLATILE_ALWAYS_CLOSE):
			self.closeVolatileInfo()

		self.firstHide = True

	#-----------------------------------------------------------------------------------------------------
	# �����������͹����������
	#-----------------------------------------------------------------------------------------------------
	def onPlaceTrap( self, controllerID, userData ):
		"""
		timer for place trap
		called by MONENMITY_ADD_TRAP_TIMER_CBID
		"""
		if self.queryTemp( "proximityID", 0 ) == 0:# ��������������������͵�
			self.setTemp( "test_Proximity", True )								# ���������Ҫ��Ҫ����շ�����ͱ�entity���뵼��onEnterTrapExt���ϵ��õ����
			id = self.addProximityExt( self.initiativeRange )						# �����һ�����壬����entity��������ʱ��onEnterTrapExt()���Զ�������
			if self.queryTemp( "test_Proximity", False ):
				self.setTemp( "proximityID", id )
				self.removeTemp( "test_Proximity" )

	def checkEnterTrapEntityType( self, entity ):
		"""
		virtual method.
		�����������entity����
		"""
		# �Ƿ�Ϊ�жԹ�ϵ
		#if self.queryRelation( entity ) != csdefine.RELATION_ANTAGONIZE:
		#	return False

		if not self.isWitnessed and not self.hasFlag( csdefine.ENTITY_FLAG_MONSTER_THINK ):
			return False

		if not isinstance( entity, CombatUnit ):
			return False

		# ע�⣺getState()ȡ�õ�״̬��һ����real entity��״̬
		plState = entity.getState()
		# ��Ҵ�������״̬������״̬��ʲôҲ����
		if plState == csdefine.ENTITY_STATE_PENDING or plState == csdefine.ENTITY_STATE_QUIZ_GAME or plState == csdefine.ENTITY_STATE_DEAD:
			return False

		state = self.getState()
		if state != csdefine.ENTITY_STATE_FREE and state != csdefine.ENTITY_STATE_REST:
			return False

		# ������Ч������Χ�ڣ�ʲôҲ����
		if entity.position.distTo( self.getSpawnPos() ) > self.territory:
			return False

		# Ǳ����أ��Ƿ���⵽Ŀ��
		if not self.isRealLook( entity.id ):
			return False

		return True
	
	def getSpawnPos( self ):
		return self.spawnPos
	
	def activeTriggerTrap( self ):
		"""
		�������������Լ��Ĺ�������
		"""
		es = self.entitiesInRangeExt( self.initiativeRange, None, self.position )
		for e in es:
			# ��ʱֻ����ɫ�ͳ���
			if not e.getEntityType() in [csdefine.ENTITY_TYPE_ROLE, csdefine.ENTITY_TYPE_PET]: continue
			range = self.position.flatDistTo( e.position )
			self.triggerTrap( e.id, range )

	def triggerTrap( self, entityID, range ):
		"""
		define method.
		�����������������
		���磺ʹ����·�䴫�͵�������Χ�� ���ͱ���buff�����ᴥ������
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
		����Ҫ��self.bootyOwner[0]��Ϊ0ʱӦ�õ��ô˷�������鵱ǰ��attacker�Ƿ�����ڶ����С�
		�����߹��򣺽���ս��״̬���һ�������˺�������Ŀ�꽫����Ϊ�����ߣ�������Ŀ���ڶ����У����Զ���Ϊ�����ߡ�
		���������ʧ����ʧ��������ݣ���������Ƕ����ж����Ա�ĵ��ⶼ��ʧ��ʧ��
		"""
		if self.bootyOwner[1] != 0:										# �����ڶ�����
			bwe = BigWorld.entities
			for e in self.enemyList:
				try:
					obj = bwe[e]
				except KeyError:
					continue

				if obj.isEntityType( csdefine.ENTITY_TYPE_PET ) or obj.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
					enemyTeam = obj.getTeamMailbox()
					if enemyTeam is not None and enemyTeam.id == self.bootyOwner[1]:
						self.bootyOwner = ( e, enemyTeam.id )							# ������д����ڶ���ĵ�����ѡһ��
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
		
		if self.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ):		#���ɱ�ѡ��Ĺ�������������﹥��������������Һͳ��﹥����
			if entity.isEntityType( csdefine.ENTITY_TYPE_PET ) or entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				return False
		
		return True

	def addDamageList( self, entityID, damage ):
		"""
		����˺��б�
		@param entityID  : entityID
		@param damage	 : �˺�ֵ
		"""
		# �������״̬ ������κε���
		if self.getSubState() == csdefine.M_SUB_STATE_GOBACK:
			return
		CombatUnit.addDamageList( self, entityID, damage )

	def onRemoveEnemy( self, entityID ):
		"""
		"""
		CombatUnit.onRemoveEnemy( self, entityID )
		if self.targetID == entityID:		# ���ɾ�����ǵ�ǰ����Ŀ�������ı乥��Ŀ��
			self.targetID = 0
			self.doAllEventAI( csdefine.AI_EVENT_ATTACKER_ON_REMOVE )

		if self.bootyOwner[0] == entityID:
			self._onRemoveFirstAttacker()	# ��ʧս��Ʒ��ӵ����
			if self.bootyOwner == ( 0, 0 ) :
				self.onBootyOwnerChanged()

	def resetEnemyList( self ):
		"""
		�������е�����Ϣ��
		"""
		CombatUnit.resetEnemyList( self )
		# ������Ϣ��û���� ����
		self.targetID = 0
		self.firstBruise = 0
		isChanged = self.bootyOwner != ( 0, 0 )
		self.bootyOwner = ( 0, 0 )
		if isChanged :
			self.onBootyOwnerChanged()

	def addCureList( self, entityID, cure ):
		"""
		��������б�
		@param entityID  : entityID
		@param cure		 : ����ֵ
		"""
		# �������״̬ ������κε���
		if self.getSubState() == csdefine.M_SUB_STATE_GOBACK:
			return
		CombatUnit.addCureList( self, entityID, cure )

	def exitFight( self ):
		"""
		����ս���� ���ⲿ���þ���ǿ������
		"""
		self.doGoBack()

	def onViewRange( self ):
		"""
		��Ұ��Χ
		�����Ѿ�������Ұ�ڵ����е��� ֻ����ս��״̬ʱ�Ž��м��
		return :None
		"""
		bwe = BigWorld.entities
		eids = []
		for eid, val in self.enemyList.iteritems():
			if not bwe.has_key( eid ):
				eids.append( eid )
				continue
			e = bwe[eid]
			#��������Լ�����Ұ��Χ��
			if not self.checkViewRange( e ) or e.getState() == csdefine.ENTITY_STATE_DEAD:
				eids.append( eid )

		if len( eids ) <= 0:
			return
		
		g_fightMgr.breakGroupEnemyRelationByIDs( self, eids )


	#-----------------------------------------------------------------------------------------------------
	# ���ﵱǰĿ�����
	#-----------------------------------------------------------------------------------------------------
	def changeAttackTarget( self, newTargetID ):
		"""
		�ı乥��Ŀ��
		@param newTargetID: Ŀ��entityID
		@type  newTargetID: OBJECT_ID
		@return:            ��
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

		self.onChangeTarget( oldEnemyID )	# �ص����ı乥��Ŀ��

	def preRemoveFlag( self,timerID, cbID ):
		"""
		�Ƴ���־λ
		"""
		self.removeFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE )
	
	def preToFightState( self, timerID, cbID ):
		"""
		������״̬�����˹���Ŀ����ı�Ϊս��״̬����
		����������볡������������볡����
		����״̬�� ����Ԥս��״̬,����Ԥս��״̬����
		������λ�ƽ��������½���ս��״̬
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
		self.changeState( csdefine.ENTITY_STATE_FIGHT )	# ������״̬�����˹���Ŀ����ı�Ϊս��״̬
		self.onChangeTarget( self.targetID )

	def doPreEvent( self, target_pos, isMovedAction, preActionTime ):
		"""
		ִ��Ԥ�����¼�
		"""
		self.firstHide = False
		self.rotateToTarget()
		if isMovedAction : 				 # ��λ�Ƶ��볡����
			pre_speed = self.queryTemp("pre_speed",20.0)				# �����볡����������ٶ�
			self.addFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE )
			pos_vect3 = Math.Vector3( self.position - target_pos )
			dist = pos_vect3.length
			pre_time = dist/pre_speed						# �����볡����������ʱ��
			self.playActionToPoint( target_pos, pre_speed )
			return dist/pre_speed
		else :                                        # û��λ�Ƶ��볡����
			self.addFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE )
			self.planesAllClients( "playAdmissionAction", () )
			return preActionTime + 0.1			# �����ӳ�ʱ��0.1s
			
	def getDstPos( self, jumpPointType, jumpPoint ):
		"""
		��ȡ��ص�Ŀ��λ��
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
		���Ŷ�����ĳ��λ��
		"""
		self.planesAllClients( "actionToPoint", ( position, speed ) )
		self.openVolatileInfo()
		self.position = position


	def onChangeTarget( self, oldEnemyID ):
		"""
		���������ˣ���ǰ�Ĺ���Ŀ��ı䣻���Ա����������̳��߱����ȵ���������������ж��������ֵ������ȷ�ġ�
		�����м��ֿ����ԣ�1.���oldEnemyIDΪ0����ʾ��֮ǰû�й���Ŀ�ꣻ2.���self.targetIDΪ0����ʾ����Ŀ�궪ʧ
		@param oldEnemyID: �ɵĹ���Ŀ��
		@type  oldEnemyID: OBJECT_ID
		@return: ��
		"""
		target = BigWorld.entities.get( self.targetID )
		if target:
			g_fightMgr.buildEnemyRelation( self, target )
		self.getScript().onChangeTarget( self, oldEnemyID )

	def onChangeTargetFailed( self, newTargetID ):
		"""
		�ı�Ŀ��ʧ��֪ͨ
		"""
		target = BigWorld.entities.get(newTargetID)
		if target:
			g_fightMgr.breakEnemyRelation( self, target )

	def checkAttackTarget( self, entityID ):
		"""
		��鹥��Ŀ��ʱ��һЩ��Ч���ж�
		@param entityID: ����Ŀ���entityID
		@type  entityID: OBJECT_ID
		@return:       ��
		"""
		distance = self.position.flatDistTo( self.getSpawnPos() )	#ȡ���Լ��ͳ��������
		#�ڻ�������������� �����Ƿ���߻�׷���ǹ���ս��AI������
		if distance > self.territory:
			self.exitFight()		# ���߻�Ҫ�� ��������Χֱ�����á�

	#-----------------------------------------------------------------------------------------------------
	# ����sub���
	#-----------------------------------------------------------------------------------------------------
	# ����sub״̬
	def changeSubState( self, state ):
		"""
		�ı�sub״̬
		@param state: ״̬
		@type  state: INT16
		@return:   ��
		"""
		if self.getSubState() == state:
			return
		self.setTemp( "old_subState", self.subState )
		self.subState = state
		self.doAllEventAI( csdefine.AI_EVENT_SUBSTATE_CHANGED )

	def getOldSubState( self ):
		"""
		��þɵ�sub״̬
		@return:   sub״̬
		"""
		return self.queryTemp( "old_subState" )

	def getSubState( self ):
		"""
		ȡsub״̬
		@return:   sub״̬
		"""
		return self.subState

	def canThink( self ):
		"""
		virtual method.
		�ж��Ƿ����think
		"""
		return self.getScript().canThink( self )

	# ˼��
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
			#��ս��״̬�£������ٶȽ���
			CPU_CostCal( csdefine.CPU_COST_AI, csdefine.CPU_COST_AI_FREE, self.className )
			self.onNoFightAIHeartbeat()
			CPU_CostCal( csdefine.CPU_COST_AI, csdefine.CPU_COST_AI_FREE, self.className )

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
					else:
						if self.canPatrol:
							self.doPatrol( self.patrolPathNode, self.patrolList )

		self.setThinkSpeed()
		if not self.isDestroyed and self.isReal():
			self.think( self.thinkSpeed )

	def onSpecialAINotDo( self ):
		"""
		����AIִ��ʧ��Ҫ���Ĵ���
		"""
		if not self.isMoving() and self.hasFlag( csdefine.ENTITY_FLAG_RAD_FOLLOW ) and not self.actionSign( csdefine.ACTION_FORBID_MOVE ):			# ִ���ε�
			target = BigWorld.entities.get( self.targetID )
			if not target:
				return
			if self.queryTemp( "roundTime", None ) and time.time() - self.queryTemp( "roundTime", time.time() ) < Const.ROUND_TIME_LIMIT:
				return
			self.setTemp( "roundTime", time.time() )
			distance = self.distanceBB( target )
			
			if distance < Const.ROUND_MIN_DIS:
				self.moveBack( self.targetID, distance - Const.ROUND_MIN_DIS - 1 )		# ���˺�һ�ף���֤�˵��ε���Χ��
			elif distance <= Const.ROUND_MAX_DIS:
				ang = random.choice( [-90, -60, 60, 90] )
				self.moveRadiFollow( self.targetID, ang, ( Const.ROUND_MIN_DIS,  Const.ROUND_MAX_DIS ) )
			else:
				self.chaseTarget( target, Const.ROUND_MAX_DIS - 1 )

	def doGoBack( self ):
		"""
		�ƶ�����սλ��
		"""
		if self.state == csdefine.ENTITY_STATE_DEAD:
			return

		self.changeSubState( csdefine.M_SUB_STATE_GOBACK )
		# changeSubState �ᴥ��AI�� �����������
		if self.isDestroyed or self.state == csdefine.ENTITY_STATE_DEAD:
			return

		if not self.hasFlag( csdefine.ENTITY_FLAG_NOT_FULL ):		# ����б���򲻻�Ѫ����
			self.full()
		self.clearBuff( [csdefine.BUFF_INTERRUPT_NONE] )
		self.resetEnemyList()

		if self.isMovingType( Const.MOVE_TYPE_PATROL ) or not self.getScript().doGoBack( self ):
			# ����ʧ�ܣ� ֱ�����س����㣬 ͳһ��onMovedOver�ڴ���
			# ��Ϊ����һ����һ���ƶ���ʧ��
			self.onMovedOver( False )

		if self.move_speed < 0.001:
			self.onMovedOver( False )


	def doFlee( self ):
		"""
		����
		"""
		if self.actionSign( csdefine.ACTION_FORBID_MOVE ):
			DEBUG_MSG( "im cannot the move!" )
			self.stopMoving()
			return

		# ��Ϊ����״̬
		self.changeSubState( csdefine.M_SUB_STATE_FLEE )

		# �ƶ�
		if not self.doRandomRun( self.position, 5 ):
			#self.think( 5.0 )
			pass # ����thinkʵ�ֻ��Ʊ��ı䣬������ʱû���õ��� ����ʧ����Ҫͣ��5��ģ�����ʵ����Ҫ����

	def doRandomWalk( self ):
		"""
		���ת�ƴ���
		"""
		# ��Ϊ��·״̬
		self.changeSubState( csdefine.M_SUB_STATE_WALK )
		# ���ȡ�� ɢ��
		rnd = random.random()
		a = self.randomWalkRange * rnd
		b = 2*math.pi * rnd
		x = a * math.cos( b ) #�뾶 * ������
		z = a * math.sin( b )
		pos = Math.Vector3( self.getSpawnPos() )
		pos.x += x
		pos.z += z

		# ɢ���ƶ�
		self.gotoPosition( pos )

	# ���а���
	def onFightCall( self, targetID, className ):
		"""
		define method.
		ս������
		@param  targetID: ����Ŀ��ID
		@type   targetID: OBJECT_ID
		@param className: �����ߵ����ͣ�����˵�Ǻ������ͣ�
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
		׷��һ��entity��
		ע��: �ײ��chaseEntity��monster�㲻��ֱ��ʹ�ã�monster׷��һ��Ŀ��Ӧ��ʹ�ñ��ӿ�
		@param   entity: ��׷�ϵ�Ŀ��
		@type    entity: Entity
		@param distance: ��Ŀ��entity��Զ�ľ���ͣ����(��/��)
		@type  distance: FLOAT
		@return: ���ش˴νӿڵ����Ƿ�ɹ�
		@rtype:  BOOL
		"""
		if entity.isDestroyed or self.isDestroyed:
			return False

		if self.move_speed < 0.001:
			return False

		self.setTemp( "firstAttackAfterChase", 0 )

		# ʹ���뼼����ƥ��ľ�����㹫ʽ
		dist = entity.getBoundingBox().z / 2 + distance + self.getBoundingBox().z / 2
		if self.getGroundPosition().distTo( entity.getGroundPosition() ) <= dist:
			return True
		elif self.chaseEntity( entity, dist ):
			self.changeSubState( csdefine.M_SUB_STATE_CHASE )
			if entity.isDestroyed or self.isDead():return False
			self.pathNotFindNum = 0
			return True

		if self.pathNotFindNum>3: #ʧ�ܵĴ�������һ���Ĵ�����3�� ������
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
	# �ܵ��˺�
	#-----------------------------------------------------------------------------------------------------
	def receiveSpell( self, casterID, skillID, param1, param2, param3 ):
		"""
		Define method.
		���ܼ��ܴ���

		@type   casterID: OBJECT_ID
		@type    skillID: INT
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		state = self.getState()
		subState = self.getSubState()
		# ����״̬ʱ���޵�״̬ ������
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

		CombatUnit.receiveSpell( self, casterID, skillID, param1, param2, param3 )	# ֪ͨ�ײ�

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
				# ��¼��һ���ܻ�
				if not self.firstBruise:
					if killerEntity.utype in [csdefine.ENTITY_TYPE_PET, csdefine.ENTITY_TYPE_ROLE, csdefine.ENTITY_TYPE_SLAVE_MONSTER, \
						csdefine.ENTITY_TYPE_VEHICLE_DART, csdefine.ENTITY_TYPE_CALL_MONSTER, csdefine.ENTITY_TYPE_PANGU_NAGUAL ]: # added by dqh
						self.firstBruise = 1
						# ����ж������¼����mailbox
						getEnemyTeam = getattr( killerEntity, "getTeamMailbox", None )	# hyw
						if getEnemyTeam and getEnemyTeam():
							self.bootyOwner = ( casterID, getEnemyTeam().id )
							DEBUG_MSG("The fatcTeam is ----->>>>> %s" % getEnemyTeam().id )
						else:
							# ����ս��״̬���һ�������˺�Ŀ�꽫����Ϊ������
							self.bootyOwner = ( casterID, 0 )
							DEBUG_MSG("The firstAttacker is ----->>>>> %s" % casterID )
						# ��һ���ܻ��¼�
						self.onBootyOwnerChanged()
						self.onFirstBruise( killerEntity, damage, skillID )
		else:
			# û�й���Դ���˺���buff����
			pass
		self.getScript().receiveDamage( self, casterID, skillID, damageType, damage )
		# ���֪ͨ�ײ㣬��Ϊ�����֪ͨ�˵ײ㣬��ô�����ﱻһ����ɱ��ʱ��ܿ�����������û����ս��״̬
		# ����������Ļ�����Щ�����Ͳ�������Ч������
		CombatUnit.receiveDamage( self, casterID, skillID, damageType, damage )

	def addBuff( self, buff ):
		"""
		���һ��Buff��

		@param buff			:	instance of BUFF
		@type  buff			:	BUFF
		"""
		state = self.getState()
		subState = self.getSubState()
		# ����״̬ʱ���޵�״̬ ������
		if subState == csdefine.M_SUB_STATE_GOBACK or state == csdefine.ENTITY_STATE_DEAD:
			return
		CombatUnit.addBuff( self, buff )	# ֪ͨ�ײ�
		self.doAllEventAI( csdefine.AI_EVENT_ADD_REMOVE_BUFF )

	def removeBuff( self, index, reasons ):
		"""
		���б���ȥ��һ��Buff��֪ͨ�ͻ��ˡ�
		@param index: BUFF���ڵ�����
		@param reasons:����ȡ����BUFF������
		"""
		if self.isDestroyed:
			return
		CombatUnit.removeBuff( self, index, reasons )
		self.doAllEventAI( csdefine.AI_EVENT_ADD_REMOVE_BUFF )

	def doAttackerOnHit( self, receiver, damageType ):
		"""
		�����к󣨼�����˺�����ʱ�˿����Ѿ����ˣ�����������Ҫ����һЩ��Ҫ�����к��ٴ�����Ч����

		�����ڣ�
		    ����Ŀ��ʱ$1%���ʸ���Ŀ������˺�$2
		    ����Ŀ��ʱ$1%����ʹĿ�깥��������$2������$3��
		    ������ʱ$1���ʻָ�$2����
		    ������ʱ$1%�����������$2������$3��
		    etc.
		@param skill:����ʵ��
		@type skill: SKILL
		@param caster:ʩ����
		@type caster: ENTITY
		"""
		CombatUnit.doAttackerOnHit( self, receiver, damageType )
		self.doAllEventAI( csdefine.AI_EVENT_SKILL_HIT )

	def doVictimOnHit( self, caster, damageType ):
		"""
		�ڱ����к󣨼�����˺�����ʱ�˿����Ѿ����ˣ�����������Ҫ����һЩ��Ҫ�ڱ����к��ٴ�����Ч����

		�����ڣ�
		    ������Ŀ��ʱ$1%���ʸ���Ŀ������˺�$2
		    etc.
		@param skill:����ʵ��
		@type skill: SKILL
		@param caster:ʩ����
		@type caster: ENTITY
		"""
		CombatUnit.doVictimOnHit( self, caster, damageType )
		self.doAllEventAI( csdefine.AI_EVENT_SKILL_RECEIVE_HIT )

	def onAttackerMiss( self, receiver, damageType ):
		"""
		������δ����
		"""
		CombatUnit.onAttackerMiss( self, receiver, damageType )
		self.doAllEventAI( csdefine.AI_EVENT_SKILL_MISS )

	def doAttackerOnDoubleHit( self, receiver, damageType ):
		"""
		�ڲ���������ʱ��������˺�����ʱ�˿����Ѿ����ˣ�������
		@param skill:����ʵ��
		@type skill: SKILL
		@param caster:ʩ����
		@type caster: ENTITY
		"""
		CombatUnit.doAttackerOnDoubleHit( self, receiver, damageType )
		self.doAllEventAI( csdefine.AI_EVENT_SKILL_DOUBLEHIT )

	def doVictimOnDoubleHit( self, caster, damageType ):
		"""
		�ڱ�������ʱ��������˺�����ʱ�˿����Ѿ����ˣ�������
		@param skill:����ʵ��
		@type skill: SKILL
		@param caster:ʩ����
		@type caster: ENTITY
		"""
		CombatUnit.doVictimOnDoubleHit( self, caster, damageType )
		self.doAllEventAI( csdefine.AI_EVENT_SKILL_RECEIVE_DOUBLEHIT )

	def doAttackerOnResistHit( self, receiver, damageType ):
		"""
		��Ŀ���мܳɹ�ʱ��������˺�����ʱ�˿����Ѿ����ˣ�������
		@param skill:����ʵ��
		@type skill: SKILL
		@param caster:ʩ����
		@type caster: ENTITY
		"""
		CombatUnit.doAttackerOnResistHit( self, receiver, damageType )
		self.doAllEventAI( csdefine.AI_EVENT_SKILL_RESISTHIT )

	def spellTarget( self, skillID, targetID ):
		"""
		��һ��entityʩ��
		@param  skillID: ������ʶ��
		@type   skillID: INT16
		@param targetID: Ŀ��entityID
		@type  targetID: OBJECT_ID
		"""
		if self.getSubState() == csdefine.M_SUB_STATE_GOBACK:	# ����״̬�²���ʩ��
			return csstatus.SKILL_NO_MSG

		return CombatUnit.spellTarget( self, skillID, targetID )

	#-----------------------------------------------------------------------------------------------------
	# ������������
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

		�������鴦��
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
		MONSTER_CORPSE_DELAY_TIMER_CBID��callback������
		"""
		self.destroy()

	def onDestroy( self ):
		"""
		entity ���ٵ�ʱ����BigWorld.Entity�Զ�����
		"""
		self.doAllEventAI( csdefine.AI_EVENT_ENTITY_ON_DESTROY )
		NPCObject.onDestroy( self )


	#-----------------------------------------------------------------------------------------------------
	# ����ս��Ʒ���
	#-----------------------------------------------------------------------------------------------------
	def getBootyOwner( self ):
		"""
		���ս��Ʒ��ӵ����
		"""
		return self.getScript().getBootyOwner( self )

	def calculateBootyOwner( self ):
		"""
		ȡ��ս��Ʒ��ӵ���ߣ�
		�����ڹ�������ʱ������onDie()ʱ���ٵ��ô˷������������ӵ���߲����ڵĻ���������Ľ�����ܻ��Ǵ���ġ�

		@return: ��
		"""
		if len( self.bootyOwner ) <= 0:
			self.bootyOwner = ( 0, 0 )
		# �������Ȩ�Ƕ���
		elif self.bootyOwner[1]  != 0:
			entities = self.searchTeamMember( self.bootyOwner[1], Const.TEAM_GAIN_EXP_RANGE )
			# ��ʾ�����ɢ��
			if len( entities ) == 0:
				# ������Ȩ
				self.bootyOwner = ( 0, 0 )

		# �������Ȩ�Ǹ��ˣ��ж��Ƿ��ڶ��飬�ƽ�����Ȩ
		elif self.bootyOwner[0] != 0:
			try:
				entity = BigWorld.entities[self.bootyOwner[0]]
			except KeyError:
				ERROR_MSG( "I hav firstAttacker(%i), but it not exsit." % self.bootyOwner[0] )
				self.bootyOwner = ( 0, 0 )
			else:
				if entity.isEntityType( csdefine.ENTITY_TYPE_PET ) or entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or  entity.isEntityType( csdefine.ENTITY_TYPE_SLAVE_MONSTER ) or entity.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ) or entity.isEntityType( csdefine.ENTITY_TYPE_CALL_MONSTER ) or entity.isEntityType( csdefine.ENTITY_TYPE_PANGU_NAGUAL ):
					if entity.isInTeam():
						self.bootyOwner = ( self.bootyOwner[0], entity.getTeamMailbox().id )	# ָ������ID
				if entity.isEntityType( csdefine.ENTITY_TYPE_PET ) or entity.isEntityType( csdefine.ENTITY_TYPE_SLAVE_MONSTER ) or entity.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ) or entity.isEntityType( csdefine.ENTITY_TYPE_CALL_MONSTER ) or entity.isEntityType( csdefine.ENTITY_TYPE_PANGU_NAGUAL ):
					self.bootyOwner = ( entity.ownerID, self.bootyOwner[1] )

	def onBootyOwnerChanged( self ) :
		"""
		�������Ȩ�ı�
		"""
		self.calculateBootyOwner()
		self.doAllEventAI( csdefine.AI_EVENT_BOOTY_OWNER_CHANGED )
		self.planesAllClients( "onSetBootyOwner", ( self.bootyOwner, ) )	# ��ͻ��˹㲥

	def queryBootyOwner( self, scrEntityID ) :
		"""
		Exposed method
		�ͻ��������ѯ����Ĺ���Ȩ
		"""
		player = BigWorld.entities.get( scrEntityID, None )
		if player :
			player.clientEntity( self.id ).onSetBootyOwner( self.bootyOwner )


	#-----------------------------------------------------------------------------------------------------
	# ���������������
	#-----------------------------------------------------------------------------------------------------
	def gainReward( self, entity, exp, pot, accum ,daohengAch, campMorale ):
		"""
		��þ���ֵ��Ǳ�ܡ����ˡ�����
		ע��:�ýӿ��ǶԵ��˽��еȼ�������;���ӳɵĺ�ʵ�ʼӵ��g�����ϵľ���ֵ,���ʱ��������ӵ�����ͼӳɺ�,ʹ�øýӿڲ��ܼ�����ӵ��������ϵ�����
		ֵ��
			@param 	entity	:	�Ӿ������
			@type 	entity	:	Entity
			@param 	exp		:	����ֵ
			@type 	exp		:	int
		"""
		if entity is None : return

		offset = self.getScript().getExpAmendRate( entity.level - self.level )
		# ����ֵƫ�Ƽ���
		dat = int( exp * offset )
		extra_potential_percent = 0

		# ����ϵͳ�౶�������
		if BigWorld.globalData.has_key( "AS_SysMultExp" ) and BigWorld.globalData[ "AS_SysMultExp" ] > 0:
			sysExtraExp = int( BigWorld.globalData[ "AS_SysMultExp" ] * dat )
			dat += sysExtraExp
			extra_potential_percent = BigWorld.globalData[ "AS_SysMultExp" ]

		# �����ɫ�����õĶ౶�������
		if entity.multExp > 0:
			extraExp = int( entity.multExp * dat )
			dat += extraExp

		if dat > 0:
			entity.addKillMonsterExp( dat )
			if entity.kaStone_SpellID > 0:
				# ��¼���侭������ ������Ҫ���������������ǵ�����
				entity.setTemp( "bootyOwnerCount", self.popTemp( "bootyOwnerCount", 1 ) )
				self.spellTarget( entity.kaStone_SpellID,  entity.id )

		# ������㾭��ֻ�ͳ����й�
		actPet = entity.pcg_getActPet()
		if actPet and actPet.etype != "MAILBOX" :
			dat = exp
			if abs( actPet.entity.level - self.level ) > 30:
				dat = exp * 0.5

			# ����ϵͳ�౶�������
			if BigWorld.globalData.has_key( "AS_SysMultExp" ) and BigWorld.globalData[ "AS_SysMultExp" ] > 0:
				sysExtraExp = int( BigWorld.globalData[ "AS_SysMultExp" ] * dat )
				dat += sysExtraExp
			# �����ɫ�����õĶ౶�������
			if entity.multExp > 0:
				extraExp = int( entity.multExp * dat )
				dat += extraExp

			actPet.entity.addEXP( int( dat ) )

		# Ǳ�ܽ���ƫ�Ƽ���
		pdat = int( pot * offset )
		if pdat > 0:
			pdat = int( math.ceil( pdat * ( 1 + entity.potential_percent + extra_potential_percent ) ) )
			entity.addPotential( pdat )
			entity.addPotentialBook( pdat )

		# ����
		spaceKey = entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )
		if accum> 0 and spaceScript.canGetAccum:											# ֻ������canGetAccumΪ1�ĵ�ͼ���ܻ������ֵ
			accumOffset = self.getScript().getAccumAmemdRate( entity.level - self.level )	# �ȼ�����
			entity.addAccumPoint( accum *  accumOffset * entity.extraAccumRate )			# ����ֵ = ����ӵ������ֵ * �������ϵ�� * �ȼ�����ϵ�� * �Ѷ�����ϵ��
			
		# ����
		adjust_param = Const.DAOHENG_AMEND_RATE      # ���е���ֵ���߻�����
		n = entity.getDaoheng() / g_daoheng.get( entity.getLevel() )
		daoheng_n =  adjust_param /(math.log( ( 1 + adjust_param ), math.e ) )  * pow( ( 1+ adjust_param ), -n )  # ��������ֵ���㹫ʽk(n)=(a/ln(1+a)) * (1/(1+a)^n)
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
		��õ���ɱ�־���
		"""
		killers = []

		try:
			expEntity = BigWorld.entities[ gainEntityID ]
		except:
			WARNING_MSG( "allot Exp ! not find entity. entity id = ", gainEntityID )
		else:
			if not expEntity.state == csdefine.ENTITY_STATE_DEAD:
				# �������߲����辭��
				if expEntity.isEntityType( csdefine.ENTITY_TYPE_PET ) :
					owner = expEntity.getOwner()
					if owner.etype != "MAILBOX" :
						self.gainReward( owner.entity, self.exp, self.potential, self.accumPoint, self.daohengAch, self.campMorale )				# ������ľ���ָ����(���˾���Ļ�ȡ)
						killers = [owner.entity]
				if expEntity.isEntityType( csdefine.ENTITY_TYPE_PANGU_NAGUAL ) :
					owner = expEntity.getOwner()
					if not hasattr( owner, "cell" ) :
						self.gainReward( owner, self.exp, self.potential, self.accumPoint, self.daohengAch, self.campMorale )				# ���̹��ػ��ľ���ָ����(���˾���Ļ�ȡ)
						killers = [ owner ]
				elif expEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
					self.gainReward( expEntity, self.exp, self.potential, self.accumPoint, self.daohengAch, self.campMorale )					# ������ľ���ָ����(���˾���Ļ�ȡ)
					killers = [ expEntity ]
		return killers

	def calcTeamMemberTongExpRate( self, entities ):
		"""
		��������е������Ա���¾���ӳɵı���
		"""
		expRates = {}
		tongs = []

		# �ҳ����еİ��
		for e in entities:
			if e.tong_dbID > 0:
				tongs.append( e.tong_dbID )

		for e in entities:
			expRate = 0.0
			if e.tong_dbID != 0:
				# �жϰ��������߻��涨��������1��ͬ����Ա����3%����
				fc = tongs.count( e.tong_dbID ) - 1
				if fc > 0:
					expRate += fc * 0.03

			expRates[ e.id ] = expRate
		return expRates

	def gainTeamReward( self, entities ):
		"""
		��ӻ�þ���ֵ
			@param 	entities	:	�Ӿ������
			@type 	entities	:	list
			@param 	exp			:	����ֵ
			@type 	exp			:	int
		��Ӻ�ľ����Ǳ��ϵ��������:2������0.7��3������0.6��4������0.55��5������0.52
		��Ӻ������ֵϵ��Ϊ��2������0.5��3������0.35��4������0.25��5������0.20
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

		# ���˵��Ѿ���������
		for idx in xrange( len( entities ) - 1, -1, -1 ):
			if entities[ idx ].state == csdefine.ENTITY_STATE_DEAD:
				entities.pop( idx )

		count = len( entities )
		if count == 0:
			return

		tongExpRates = self.calcTeamMemberTongExpRate( entities )

		#���ڻ���ʯ���꼼�ܼ�����Ҫ��õ�ǰ������������, ��������������Ǽ�¼��������
		self.setTemp( "bootyOwnerCount", count )

		for e in entities:
			#offset = AmendExp.instance().getLevelRate( e.level - self.level )#�Ͳ߻����ۺ�����ȼ��������Ӿ�����㿼�ǵķ�Χ����Ӿ���ļ���,Ӧ��
			#ֻ������ӷ���Ծ����Ӱ�죬���ȼ������ڸ��˶Ի�ȡ�����Ӱ�졣�������Զ��������˾�������ģ�飬�������Ӿ�������໥ǣ��. by---hd
			#��Ӻ�ľ����Ǳ��ϵ��������:2������0.7��3������0.6��4������0.55��5������0.52
			#gexp = (( count - 1 ) * 0.1 + 1 ) * exp 		#* offset	# û�мӳ�ǰ�ľ���
			#gpot = (( count - 1 ) * 0.1 + 1 ) * pot 		#* offset	# û�мӳ�ǰ��Ǳ��
			gexp = expRateDict[ count ] * self.exp
			gpot = expRateDict[ count ] * self.potential
			accum = accumRateDict[ count ] * self.accumPoint

			idList = [ mb.id for mb in e.getTeamMemberMailboxs() ]

			# �����Ҵ���ʦ����������ʦͽ��Ӷ��⾭�������������Ҽ�����Ӧ����
			teachExp = 0.0

			# �����ӳ����ӽ�ȥ
			tongExp = int( gexp * tongExpRates[ e.id ] )

			# ����Ҽ���ʦͽ��Ӷ��⾭��,gexp * 20%
			if e.hasMaster():
				masterMB = e.getMasterMB()
				if masterMB and masterMB.id in idList:
					master = BigWorld.entities.get( masterMB.id )
					if gexp and master and e.position.flatDistTo( master.position ) <= csconst.TEACH_TEAM_KILL_BENEFIT_DISTANCE and e.spaceID == master.spaceID:
						teachExp = gexp * csconst.TEACH_TEAM_EXP_ADDITIONAL_PERCENT

			# �����ҷ�����ӣ���÷��޾���ӳ�,gexp * %10
			loveExp = 0.0
			if e.hasCouple():
				for tempID in idList:
					if e.isCouple( tempID ):
						loveExp = gexp * csconst.COUPLE_TEAM_EXP_PERCENT
						break

			# ��ҽ�ݹ�ϵ�ӳ�
			allyExp = 0
			if e.hasAllyRelation():
				for tempID in idList:
					if e.checkAllyByID( tempID ):
						allyExp = gexp * csconst.ALLY_TEAM_EXP_PERCENT
						break

			#����ͼ�������ܵ���ӷ��ޡ���ᡢʦͽ����ݵ�Ӱ��
			gexp = gexp + teachExp + loveExp + tongExp + allyExp
			self.gainReward( e, gexp, gpot, accum , self.daohengAch, self.campMorale )

	def queryRelation( self, entity ):
		"""
		"""
		return self.getScript().queryRelation( self, entity )

	def calcMoveSpeed( self ):
		"""
		virtual method.
		�ƶ��ٶ�
		"""
		# �����ƶ��ٶȼ��㺯�������ٶȸı�ʱ���½��е�ǰ���ƶ�(��������ƶ�)
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
			self.think( 0.5 )			# ������ʱthink,��Ϊ�յ������Ϣʱself.isWitnessed����ֵ��û�ı����

	def wieldExcData( self ):
		"""
		������װ���ϸ�������

		@param dataID: ������������ID
		@type  dataID: INT32
		"""
		# �߻��õ���չ���ԣ������������ָ��NPC������
		# ����ɵĹ���װ������
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
		���ù���ȼ�
		"""
		if level == 0:
			self.level = 1
		else:
			self.level = min( self.getScript().maxLv, level )
		
		self.exp = int( g_npcExp.get( self.level ) * self.getScript()._expRate )
		self.potential = int( g_npcPotential.get( self.level ) * self.getScript()._potentialRate )
		self.accumPoint = int( g_npcAccum.get( self.level ) * self.getScript()._accumRate )
		self.daohengAch = float( g_daohengAch.get( self.level ) * self.getScript()._daohengRate )   # �����ɱ���н���
		self.campMorale = float( g_campMorale[ self.level ] * self.getScript()._campMoraleRate )   # �����ɱ���н���
		#���õ���ֵ
		dh_l = g_daoheng.get( self.level )
		dh = self.getScript()._daohengAtt * dh_l
		dh = max( 1, dh )
		self.setDaoheng( dh )
		#��������ֵ����һЩ����ֵ�߻���Ҫ���������
		attrs = g_monsterIntensifyAttr.getAttrs( self.className, self.level )
		if attrs:
			for i in attrs:
				if hasattr( self, i ):
					setattr( self, i, attrs[i] )
		#������������������ӵ�˵��д�ȼ�Ϊ-1ʱ�������������еȼ��Ĺ��������ֵ
		attr_accum = g_monsterIntensifyAttr.getAttr( self.className, -1, "accumPoint" )
		if attr_accum:
			setattr( self, "accumPoint", attr_accum )

		# ���ʵȻ������Եļ��������ں��棬��ΪbaseAtt��excAtt����Ҳ�п��ܱ�����
		dic = g_npcBaseAttr.get( self.getClass(), self.level )
		self.strength_base = dic[ "strength_base" ] * self.baseAtt
		self.dexterity_base = dic[ "dexterity_base" ] * self.baseAtt
		self.intellect_base = dic[ "intellect_base" ] * self.baseAtt
		self.corporeity_base = dic[ "corporeity_base" ] * self.baseAtt
		self.wieldExcData()    # ��ʼ������װ������,����ĳ�ֱ�Ӵ�NPCExcData�л�ȡ����
		# ���¼�������
		self.calcDynamicProperties()
		# ��Ѫ��ħ
		self.full()

	#-----------------------------------------------------------------------------------------------------
	# Ѳ�����  kb
	#-----------------------------------------------------------------------------------------------------
	def onPatrolToPointOver( self, command ):
		"""
		virtual method.
		����onPatrolToPointFinish()������ECBExtendģ���еĻص�����

		@param command: Ѳ�ߵ�һ�������õ����������
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
	# �����ص����  kb
	#-----------------------------------------------------------------------------------------------------
	def onMovedOver( self, state ):
		"""
		virtual method.
		ʹ��gotoPosition()�ƶ�����ͨ��
		@param state: �ƶ��������ʾ�Ƿ�ɹ�
		@type  state: bool
		@return:      None
		"""
		AmbulantObject.onMovedOver( self, state )
		subState = self.subState
		self.changeSubState( csdefine.M_SUB_STATE_NONE )

		# changeSubState ���ܻᴥ��AI������entity
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
			self.randomWalkTime = random.randint( 0, 10 )	# ����߶�������ԭ��һ��ʱ��������
			return
		elif subState == csdefine.M_SUB_STATE_GOBACK:
			if not state:										# ����߲���ȥ��ֱ������
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
			self.activeTriggerTrap()	# ���߽�������������������
		elif subState == csdefine.M_SUB_STATE_FLEE:
			self.onFleeOver()

	# ׷�������¼�
	def onChaseOver( self, entity, state ):
		"""
		virtual method.
		ʹ��chaseEntity()�ƶ�����ͨ��
		@param   entity: ��׷�ϵ�Ŀ�꣬����ڽ���ʱĿ���Ҳ�������Ŀ����ʧ�ˣ����ֵΪNone
		@type    entity: Entity
		@param    state: �ƶ��������ʾ�Ƿ�ɹ�
		@type     state: bool
		@return:         None
		"""
		AmbulantObject.onChaseOver( self, entity, state )
		# ���ڽ��һ�ѹ���׷��ͬһ��Ŀ��ʱ�ص���һ������⡣
		self.setTemp( "firstAttackAfterChase", 0 )	# ֵΪ0��ʾ��׷���ս���
		self.think(0.1)

	# �ͷż�������¼�
	def onSkillCastOver( self, spellInstance, target ):
		"""
		virtual method.
		�ͷż�����ɡ�

		@param  spellInstance: ����ʵ��
		@type   spellInstance: SPELL
		@param  target: ����Ŀ��
		@type   target: SkillImplTargetObj
		"""
		CombatUnit.onSkillCastOver( self, spellInstance, target )
		self.setTemp( "last_use_spell", spellInstance.getID() )
		self.doAllEventAI( csdefine.AI_EVENT_SPELL_OVER )

	# ���ܱ�����¼�
	def onSpellInterrupted( self ):
		"""
		��ʩ�������ʱ��֪ͨ��
		����ͨ��self.attrIntonateTargetID��self.attrIntonatePosition��self.attrIntonateSkill��õ�ǰ��ʩ��Ŀ�ꡢλ���Լ�����ʵ��
		"""
		CombatUnit.onSpellInterrupted( self )
		self.updateTopSpeed()
		self.doAllEventAI( csdefine.AI_EVENT_SPELL_INTERRUPTED )
		# �����ж�
		#self.think()

	# ���ܽ����¼�
	def onFleeOver( self ):
		"""
		���ܽ���
		"""
		pass

	def onFirstBruise( self, killerEntity, damage, skillID ):
		"""
		��һ���ܻ��¼�

		@param killerEntity: ��������˺�����
		@type  killerEntity: Entity
		@param       damage: �˺�
		@type        damage: int
		@param      skillID: ����ID
		@type       skillID: INT
		@return:             ��
		"""
		if self.isMoving():
			self.stopMoving()

	def onStateChanged( self, old, new ):
		"""
		״̬�л���
			@param old	:	������ǰ��״̬
			@type old	:	integer
			@param new	:	�����Ժ��״̬
			@type new	:	integer
		"""
		CombatUnit.onStateChanged( self, old, new )
		self.getScript().onStateChanged( self, old, new )

		# ����ǵ�һ�ι�������¼��սλ�ã�����ս����ɺ�ص���λ
		if new == csdefine.ENTITY_STATE_FIGHT:
			self.rotateToTarget()
			self.resetAI()
			self.doAllEventAI( csdefine.AI_EVENT_STATE_CHANGED )
			self.move_speed_base = self.runSpeed
			self.calcMoveSpeed()
			self.think(0.5)
			return
		elif new == csdefine.ENTITY_STATE_FREE:
			if old == csdefine.ENTITY_STATE_FIGHT:					# ���ս���������ı�״̬Ϊ����״̬
				self.doAllEventAI( csdefine.AI_EVENT_STATE_CHANGED )
				self.doGoBack()
				return
			if old == csdefine.ENTITY_STATE_ENVIRONMENT_OBJECT:
				self.castTrap = True
		self.doAllEventAI( csdefine.AI_EVENT_STATE_CHANGED )
		if new == csdefine.ENTITY_STATE_DEAD:
			if self.isMoving():										# ����ƶ���ֹͣ
				self.stopMoving()

	def onEnemyListChange( self, entityID ):
		"""
		ս����Ϣ���иĶ�֪ͨ
		"""
		self.aiTargetID = entityID
		self.doAllEventAI( csdefine.AI_EVENT_ENEMY_LIST_CHANGED )
		self.aiTargetID = 0

	def onDamageListChange( self, entityID ):
		"""
		�˺���Ϣ���иĶ�֪ͨ
		"""
		self.aiTargetID = entityID
		self.doAllEventAI( csdefine.AI_EVENT_DAMAGE_LIST_CHANGED )
		self.aiTargetID = 0

	def onCureListChange( self, entityID ):
		"""
		������Ϣ���иĶ�֪ͨ
		"""
		self.aiTargetID = entityID
		self.doAllEventAI( csdefine.AI_EVENT_CURE_LIST_CHANGED )
		self.aiTargetID = 0

	def onFriendListChange( self, entityID ):
		"""
		�ѷ���Ϣ���иĶ�֪ͨ
		"""
		self.aiTargetID = entityID
		self.doAllEventAI( csdefine.AI_EVENT_FRIEND_LIST_CHANGED )
		self.aiTargetID = 0

	def onHPChanged( self ):
		"""
		HP���ı�ص�
		"""
		CombatUnit.onHPChanged( self )
		self.doAllEventAI( csdefine.AI_EVENT_HP_CHANGED )
		self.getScript().onHPChanged( self )

	def onMPChanged( self ):
		"""
		MP���ı�ص�
		"""
		CombatUnit.onMPChanged( self )
		self.doAllEventAI( csdefine.AI_EVENT_MP_CHANGED )

	#----------------------------------------------�����ǿ���Ե��ں�-------------------------------------------

	def calcPhysicsDPSBase( self ):
		"""
		��������DPS_baseֵ
		"""
		pass

	def calcHPMaxBase( self ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
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
		��������ֵ����ֵ
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "MP_Max_base" )
		if val != None:
			self.MP_Max_base = val
			return
		CombatUnit.calcMPMaxBase( self )

	def calcStrengthBase( self ):
		"""
		������������ֵ
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "strength_base" )
		if val != None:
			self.strength_base = val
			return
		CombatUnit.calcStrengthBase( self )

	def calcDexterityBase( self ):
		"""
		�������ݻ���ֵ
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "dexterity_base" )
		if val != None:
			self.dexterity_base = val
			return
		CombatUnit.calcDexterityBase( self )

	def calcIntellectBase( self ):
		"""
		������������ֵ
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "intellect_base" )
		if val != None:
			self.intellect_base = val
			return
		CombatUnit.calcIntellectBase( self )

	def calcCorporeityBase( self ):
		"""
		�������ʻ���ֵ
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "corporeity_base" )
		if val != None:
			self.corporeity_base = val
			return
		CombatUnit.calcCorporeityBase( self )

	def calcDamageMinBase( self ):
		"""
		������С�������� ����ֵ
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "damage_min_base" )
		if val != None:
			self.damage_min_base = val
			return
		CombatUnit.calcDamageMinBase( self )

	def calcDamageMaxBase( self ):
		"""
		��������������� ����ֵ
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "damage_max_base" )
		if val != None:
			self.damage_max_base = val
			return
		CombatUnit.calcDamageMaxBase( self )

	def calcMagicDamageBase( self ):
		"""
		virtual method
		����������
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "magic_damage_base" )
		if val != None:
			self.magic_damage_base = val
			return
		CombatUnit.calcMagicDamageBase( self )

	def calcDodgeProbabilityBase( self ):
		"""
		������ ����ֵ
		��ɫ����Է������ļ��ʡ���ͨ���������Ա����ܡ������ܹ����ͷ������ܹ������ܱ����ܡ����ܳɹ��󣬱����������ι��������κ��˺���
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "dodge_probability_base" )
		if val != None:
			self.dodge_probability_base = val
			return
		CombatUnit.calcDodgeProbabilityBase( self )

	def calcArmorBase( self ):
		"""
		virtual method
		�������ֵ	��ʾ����ɫ�ܵ�������ʱ���ܶԴ�������������������������
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "armor_base" )
		if val != None:
			self.armor_base = val
			return
		CombatUnit.calcArmorBase( self )

	def calcMagicArmorBase( self ):
		"""
		virtual method
		��������ֵ	��ʾ����ɫ�ܵ���������ʱ���ܶԴ˷�������������������������
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "magic_armor_base" )
		if val != None:
			self.magic_armor_base = val
			return
		CombatUnit.calcMagicArmorBase( self )

	def calcDoubleHitProbabilityBase( self ):
		"""
		��������
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "double_hit_probability_base" )
		if val != None:
			self.double_hit_probability_base = val
			return
		CombatUnit.calcDoubleHitProbabilityBase( self )

	def calcMagicDoubleHitProbabilityBase( self ):
		"""
		����������
		"""
		val = g_monsterIntensifyAttr.getAttr( self.className, self.level, "magic_double_hit_probability_base" )
		if val != None:
			self.magic_double_hit_probability_base = val
			return
		CombatUnit.calcMagicDoubleHitProbabilityBase( self )

	def changeToNPC( self ):
		"""
		���NPC
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
		��ɹ������Ѿ����NPC��˵�ģ�
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
		�ͻ���������Я���ȼ�����
		"""
		player = BigWorld.entities.get( srcEntityID )
		if player is None or not self.hasFlag( csdefine.ENTITY_FLAG_CAN_CATCH ):
			return
		player.clientEntity( self.id ).receiveTakeLevel( self.getScript().takeLevel )

	def setLeftHandNumber( self, modelNumber ):
		"""
		define method.
		��������ģ��
		"""
		self.lefthandNumber = modelNumber
		self.planesAllClients( "onSetLeftHandNumber", ( modelNumber, ) )

	def setRightHandNumber( self, modelNumber ):
		"""
		define method.
		��������ģ��
		"""
		self.righthandNumber = modelNumber
		self.planesAllClients( "onSetRightHandNumber", ( modelNumber, ) )


	def farDestroy( self ):
		"""
		define method
		Զ������
		"""
		self.resetEnemyList()
		self.destroy()

	def setBattleCamp( self, battleCamp ):
		"""
		define method
		�����Ӫ���ı�
		"""
		self.battleCamp = battleCamp
		self.doAllEventAI( csdefine.AI_EVENT_CHANGE_BATTLECAMP )


	def intonate( self, skill, target, time ):
		"""
		�ù���ȥ����һ�����ܣ����㲥��allClients��

		@param    skill: instance of Spell
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: BOOL������Ѿ��������򷵻�False�����򷵻�True
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
		# ��¼intonate��������Ҫ�õ��Ĳ���
		self.attrIntonateSkill = skill
		self.attrIntonateTarget = target
		self.setTemp( "RANDOM_WALK_RANGE", self.randomWalkRange )
		self.randomWalkRange = 0 #����δ����ս��״̬ʹ���������� ���ƶ�
		self.stopMoving()

		self.planesAllClients( "intonate", ( skill.getID(), intonateTime, target ) )
		return True

	def onIntonateOver( self, controllerID, userData ):
		"""
		timer callback.
		see also Entity.onTimer() method.

		�ڴ˴���������Ҫ�ҵ���Ӧ��skill��������skill.use()��������ʩ�ŷ�����
		"""
		target = self.attrIntonateTarget

		#INFO_MSG( "--> %i: spellID = %i, targetID = %i, position =" % ( self.id, self.attrIntonateSkill.getID(), targetID ), position  )
		skill = self.attrIntonateSkill
		state = skill.castValidityCheck( self, target )
		if state != csstatus.SKILL_GO_ON:
			self.interruptSpell( state )
			return

		# ����attrIntonateSkill(����)���ܣ�
		# ����attrIntonateTarget�������ƺ�Ҳ���ԣ�������ʱû��������Щ���ԡ�
		self.attrIntonateSkill = None
		self.attrIntonateTimer = 0
		range = self.queryTemp( "RANDOM_WALK_RANGE", 0 )
		self.removeTemp( "RANDOM_WALK_RANGE")
		self.randomWalkRange = range
		self.updateTopSpeed()

		# ��ʼʩ��Ч��
		skill.cast( self, target )

	def rotateToTarget( self ):
		"""
		ת��ǰĿ��
		"""
		target = BigWorld.entities.get( self.targetID )
		if not target:
			return
		if self.hasFlag( csdefine.ENTITY_FLAG_CANT_ROTATE_IN_FIGHT_STATE ):
			return

		effectState = csdefine.EFFECT_STATE_FIX | csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_SLEEP
		if not (self.effect_state & effectState) == 0: #��ֹת����ж�
			return
		
		disPos = target.position - self.position
		if math.fabs( disPos.yaw ) > 0.0:
			self.rotateToPos( target.position )

	def moveToPosFC( self, endDstPos, targetMoveSpeed, targetMoveFace ):
		"""
		�����ƶ�
		"""
		if self.hasFlag(csdefine.ENTITY_VOLATILE_ALWAYS_CLOSE):return
		self.position = endDstPos
		self.planesAllClients( "moveToPosFC", ( endDstPos, targetMoveSpeed, targetMoveFace ) )
		
	def getOwner( self ):
		"""
		���������
		"""
		return self.getScript().getOwner( self )
		
	def getOwnerID( self ):
		"""
		���������ID
		"""
		return self.getScript().getOwnerID( self )
		
	def setOwner( self, owner ):
		"""
		����������
		"""
		self.getScript().setOwner( self, owner )

	def setThinkSpeed( self, delay = 0 ):
		"""
		���������ٶ�
		"""
		if len( self.nextAIInterval):
			delay = max( self.nextAIInterval )
			if delay > 0:
				self.thinkSpeed = delay
				self.nextAIInterval = []
				return
			self.nextAIInterval = []

		# ս��״̬��
		if self.state == csdefine.ENTITY_STATE_FIGHT:
			self.thinkSpeed = 1.0
		else:
			#��ս��״̬�£������ٶȽ���
			if self.noFightStateAICount == 0:
				self.thinkSpeed = 5.0
			else:
				self.thinkSpeed = 1.0

	def changeRelationMode( self, type ):
		"""
		���ڹ�����ͨ������ս��ģʽ�������ģ�����Ҫ�ı����ľ�̬��ս��ģʽ������ֱ��pass
		"""
		pass
		
	def queryGlobalCombatConstraint( self, entity ):
		"""
		��ѯȫ��ս��Լ��
		"""
		return self.getScript().queryGlobalCombatConstraint( self, entity )
		
# Monster.py
