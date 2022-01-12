# -*- coding: gb18030 -*-

from bwdebug import *
from Monster import Monster

import csdefine
import csstatus
import BigWorld
import csconst
import ECBExtend
import Const
import random

from interface.CombatUnit import CombatUnit

# �ٻ������
class CallMonster( Monster ):
	def __init__( self ):
		Monster.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_CALL_MONSTER)
		if self.owner:
			# ���Լ�ע�ᵽ��������
			self.owner.cell.registerCallMonster( self.base )

	def getOwner( self ):
		# ����Լ����˵�baseMailBox
		owner = BigWorld.entities.get( self.owner.id )
		if owner:
			return owner
		else:
			return self.owner
		
	def setOwner( self, ownerBase ):
		# define method.
		# ownerBase : master base mailbox
		self.owner = ownerBase
		self.ownerID = ownerBase.id
		self.owner.cell.registerCallMonster( self.base ) # ����ע���Լ�����������
		self.addCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_FRIEND_ID, ownerBase.id )
	
	def getOwnerID( self ):
		if self.owner:
			return self.owner.id
		return 0

	def queryRelation( self, entity ):
		"""
		virtual method.
		��ȡ�ٻ�entity��ָ�� entity �Ĺ�ϵ
		"""
		#if self.isDestroyed or entity.isDestroyed:
		#	return csdefine.RELATION_NOFIGHT
		
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND

		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.queryRelation( self, entity )

		if not isinstance( entity, CombatUnit ):
			return csdefine.RELATION_FRIEND

		if isinstance( entity, Monster) and self.battleCamp and self.battleCamp == entity.battleCamp:			# ���Ŀ���ǹ����Ҹ��Լ�����ͬһ����Ӫ
			return csdefine.RELATION_FRIEND

		if entity.effect_state & csdefine.EFFECT_STATE_PROWL:	# ���entity����Ǳ��Ч��״̬
			return csdefine.RELATION_NOFIGHT

		ownerEntity = BigWorld.entities.get( self.getOwnerID(), None )
		if ownerEntity == None :
			return csdefine.RELATION_NONE
		else :
			return ownerEntity.queryRelation( entity )

	def isInTeam( self ) :
		ownerEntity = BigWorld.entities.get( self.owner.id )
		if ownerEntity is None :
			return False

		return ownerEntity.isInTeam()

	def flyToMasterSpace( self ):
		"""
		define method
		�ɵ��������ڵ�λ��
		"""
		self.addTimer( 2.0, 0.0, ECBExtend.FLY_TO_MASTER_CB )

	def flyToMasterCB( self, controllerID, userData ):
		# timer call back �ɵ����˵�λ��
		if BigWorld.entities.has_key( self.getOwnerID() ):
			owner = BigWorld.entities[ self.getOwnerID() ]
			self.followMaster( int( owner.getCurrentSpaceData( csconst.SPACE_SPACEDATA_SPACE_TYPE_KEY ) ), owner, owner.position )
			if not self.isDestroyed and self.isReal():
				self.stopMoving()
		else:
			self.owner.cell.onRemoteFollowCallMonster( self.base )

	def followMaster( self, spaceType, cellMailBox, position ):
		"""
		define method
		�õ����˻ظ��ṩspace type, cellMailbox �� position
		"""
		if spaceType in self.spaceEnable or len( self.spaceEnable ) == 0:
			self.teleport( cellMailBox, position + ( random.randint(-2,2), 0,random.randint(-2,2) ), ( 0, 0, 0 ) )
		else:
			self.destroy()

	def calculateBootyOwner( self ):
		# ����ս��Ʒ
		Monster.calculateBootyOwner( self )
	
	def onDestroy( self ):
		# entity ���ٵ�ʱ����BigWorld.Entity�Զ�����
		self.owner.cell.removeCallMonster( self.base ) # �����˵��ٻ��б����Ƴ�
		self.removeCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_FRIEND_ID, self.getOwnerID() )
		Monster.onDestroy( self )

	def doGoBack( self ):
		"""
		�ƶ�����սλ��
		"""
		if self.isDestroyed or self.state == csdefine.ENTITY_STATE_DEAD:
			return
		self.resetEnemyList()

	def doRandomWalk( self ):
		"""
		"""
		pass

	def isInTeam( self ) :
		owner = BigWorld.entities.get( self.getOwnerID() )
		if not owner:
			return False
		return owner.isInTeam()

	def getTeamMailbox( self ):
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
	
	def onOwnerDestroy( self ):
		# define method
		# �������������
		self.owner = None
		self.ownerID = 0
		if self.waitOwnerInWorld:
			self.destroy()
	
	def onOwnerCallMonster( self, entityID ):
		# define mothod.
		# �����ٻ�����
		if self.className == entityID: # ������������ٻ����Լ�һ���Ĺ������Լ�����
			self.destroy()
			
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
			return csdefine.RELATION_FRIEND
