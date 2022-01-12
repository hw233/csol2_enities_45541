# -*- coding: gb18030 -*-
# SlaveMonster.py
# $Id: SlaveMonster.py,v 1.1 2008-09-01 03:34:03 zhangyuxing Exp $

#################################################################################
#ӵ�����˵Ĺ����������ƣ�����Զ�ȳ���򵥣��������˿����ǹ���
#################################################################################

from bwdebug import *
from interface.CombatUnit import CombatUnit
from Monster import Monster
import csdefine
import csstatus
import BigWorld
import csconst
import cschannel_msgs
import ECBExtend
import Const
import random

class SlaveMonster( Monster ):
	"""
	�����࣬������NPC�Ϳ�ս����λ
	"""
	def __init__(self):
		Monster.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_SLAVE_MONSTER )


	def getOwner( self ):
		"""
		����Լ����˵�baseMailBox
		"""
		return self.queryTemp( "ownerBaseMailBox", None )


	def getOwnerID( self ):
		"""
		����Լ����˵� id
		"""
		return self.ownerID

	def setOwner( self, owner ):
		"""
		"""
		self.ownerID = owner.id
		#self.setTemp( "ownerName", owner.getName() )
		self.ownerName = owner.getName()
		if owner.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ):
			# ������ڵ��������ڳ����洢����������Ӧ������ҵ�
			self.ownerName = owner.ownerName
		owner.setTemp( "dart_id", self.id )	#�洢�ڳ�id���������
		self.addCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_FRIEND_ID, self.ownerID )
		if owner.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			self.setTemp( "ownerBaseMailBox", owner.base )
		else:
			if owner.queryTemp( "ownerBaseMailBox", None) is not None:
				self.setTemp( "ownerBaseMailBox", owner.queryTemp( "ownerBaseMailBox", None) )

	def queryRelation( self, entity ):
		"""
		virtual method.
		ȡ���Լ���Ŀ��Ĺ�ϵ

		@param entity: ����Ŀ��entity
		@return : RELATION_*
		"""
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.queryRelation( self, entity )
		
		if isinstance( entity, Monster) and self.battleCamp and self.battleCamp == entity.battleCamp:			# ���Ŀ���ǹ����Ҹ��Լ�����ͬһ����Ӫ
			return csdefine.RELATION_FRIEND

		slaveOwner = BigWorld.entities.get( self.ownerID )

		if slaveOwner == None or not slaveOwner.isReal():
			return csdefine.RELATION_ANTAGONIZE

		if not isinstance( entity, CombatUnit ):
			return csdefine.RELATION_FRIEND

		if isinstance( entity, SlaveMonster ) and self.ownerName == entity.ownerName:
			return csdefine.RELATION_FRIEND

		if hasattr( entity, "getName" ) and self.ownerName == entity.getName():
			return csdefine.RELATION_FRIEND

		return csdefine.RELATION_ANTAGONIZE


	def isInTeam( self ) :
		"""
		�Ƿ��ڶ�����
		"""
		owner = BigWorld.entities.get( self.getOwnerID() )
		if owner is None : return False
		return owner.isInTeam()

	def flyToMasterSpace( self ):
		"""
		define method
		�ɵ��������ڵ�λ��
		"""
		self.addTimer( 2.0, 0.0, ECBExtend.FLY_TO_MASTER_CB )

	def flyToMasterCB( self, controllerID, userData ):
		"""
		"""
		ownerID = self.getOwnerID()
		if BigWorld.entities.has_key( ownerID ):
			owner = BigWorld.entities[ ownerID ]
			self.teleport( owner, owner.position + ( random.randint(-2,2), 0,random.randint(-2,2) ), owner.direction )
			if self.isReal():
				self.stopMoving()
		else:
			self.queryTemp('ownerBaseMailBox').cell.requestTakeToMaster( self.base )


	def onReceiveMasterInfo( self, cellMailBox, position ):
		"""
		define method
		�õ����˻ظ��ṩcellMailbox �� position
		"""
		self.teleport( cellMailBox, position + ( random.randint(-2,2), 0,random.randint(-2,2) ), ( 0, 0, 0 ) )

	def calculateBootyOwner( self ):
		"""
		"""
		Monster.calculateBootyOwner( self )

	def onEnterTrapExt( self, entity, range, controllerID ):
		"""
		Entity.onEnterTrapExt( entity, range, controllerID )
		"""
		# ����entity �����������巶Χ֮�ڣ��˺����ͻᱻ����
		state = self.getState()
		#if state == csdefine.ENTITY_STATE_FIGHT:						# ��Ϣ״̬.....�ƺ�û���õ�
			# ��ս��״̬��ʱ��ȡ���ݾ�
		#	self.cancel( controllerID )
		#	return
		if self.getSubState() == csdefine.M_SUB_STATE_GOBACK:
			return

		if not hasattr( entity, "getState" ):
			return

		plState = entity.getState()
		if plState == csdefine.ENTITY_STATE_PENDING or plState == csdefine.ENTITY_STATE_DEAD or plState == csdefine.ENTITY_STATE_QUIZ_GAME:
			return												# ��Ҵ�������״̬������״̬���ʴ�״̬��ʲôҲ����

		self.aiTargetID = entity.id
		self.doAllEventAI( csdefine.AI_EVENT_SPELL_ENTERTRAP )
		self.aiTargetID = 0
		
		# ����������������ĳ�Ա���ȼ���Ѻ��������3���ڣ���һ����ȡ�ڳ����˵�buff
		if self.queryTemp( "ownerTongDBID", None ):
			if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and self.queryTemp( "ownerTongDBID" ) == entity.tong_dbID:
				ownerID = self.getOwnerID()
				if BigWorld.entities.has_key( ownerID ):
					ownerLevel = BigWorld.entities[ ownerID ].getLevel()
				else:
					ownerLevel = self.queryTemp( "level", 0 )
				if entity.getLevel() <= ownerLevel + 3 and entity.getLevel() >= ownerLevel - 3:
					self.spellTarget( 122372001, entity.id )		# ����Ҽ�һ����ȡ�Լ����˵�buff

	def dartMissionBrocad( self, killer, factionID ):
		"""
		���ڻ���ڳɹ��Ĺ㲥 by����14:10 2009-7-31
		@param missionType : ��������
		@param missonnType : UINT8
		"""
		#self.family_grade
		killer.brocastMessageSlaveDart( factionID )

	def calcKillerPkValue( self, killer ):
		"""
		����pkֵ
		@param    killer: ���Ҹɵ�����
		@type     killer: RoleEntity
		"""
		# �ж�ɱ���Ƿ���Role������ǳ��Ҫ�����˵�
		if killer == None: return
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" : return
			killer = owner.entity
		if not killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ): return
		if killer.pkState == csdefine.PK_STATE_PROTECT: return
		killer.addPkValue( 12 )


	def destoryDartEntity( self ):
		"""
		define method
		"""
		self.setTemp( 'dartQuestAbandoned', True )
		owner = self.getOwner()
		if owner:
			self.removeCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_FRIEND_ID, self.getOwnerID() )
		self.addTimer( csconst.MONSTER_CORPSE_DURATION, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )

	def doGoBack( self ):
		"""
		�ƶ�����սλ��
		"""
		self.resetEnemyList()

	def doRandomWalk( self ):
		"""
		"""
		pass

	def getTeamMailbox( self ):
		"""
		"""
		owner = BigWorld.entities.get( self.getOwnerID() )
		if not owner:
			return None
		return owner.getTeamMailbox()

	def onBootyOwnerChanged( self ) :
		"""
		virtual method
		�������û�й���Ȩ�ĸ���
		"""
		pass

	def queryBootyOwner( self, scrEntityID ) :
		"""
		Exposed method
		�ͻ��������ѯ����Ĺ���Ȩ
		"""
		pass
		
	def getRelationEntity( self ):
		"""
		��ȡ��ϵ�ж�����ʵentity
		"""
		owner = BigWorld.entities.get( self.getOwnerID() )
		if not owner:
			return None
		else:
			return owner
			
	def queryCombatRelation( self, entity ):
		owner = BigWorld.entities.get( self.getOwnerID() )
		if owner:
			return owner.queryCombatRelation( entity )
		else:
			return csdefine.RELATION_ANTAGONIZE