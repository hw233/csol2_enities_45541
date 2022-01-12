# -*- coding: gb18030 -*-

import BigWorld
# common
import csconst
import csdefine
# cell
from Monster import Monster

class NPCFormationServant( Monster ):
	"""
	������NPC��Ӷ�ˣ�
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		if self.owner:
			self.owner.cell.remoteScriptCall( "registerLineup", ( self.id, ) )				# ���Լ��ŵ����˵Ĳ����б���ȥ

	def getOwner( self ):
		"""
		����Լ����˵�baseMailBox
		"""
		owner = BigWorld.entities.get( self.getOwnerID() )
		if owner:
			return owner
		else:
			return self.owner
			
	def getOwnerID( self ):
		"""
		������˵�ID
		"""
		return self.ownerID
		
	def setOwner( self, ownerEntity ):
		self.owner = ownerEntity
		self.ownerID = ownerEntity.id
		self.owner.remoteScriptCall( "registerLineup", ( self.id, ) )			# ���Լ��ŵ����˵Ĳ����б���ȥ
		self.addCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_FRIEND_ID, self.ownerID )
	
	def setToOwnerPos( self, pos):
		"""
		define method.
		������������˵�����
		"""
		self.toOwnerPos = tuple( pos )
	
	def gotoToOwnerPos( self ):
		"""
		�ߵ���������˵�λ��
		"""
		ownerEntity = self.getOwner()
		if not ownerEntity:
			return
			
		pos = ownerEntity.position + self.toOwnerPos
		if abs(pos.x - self.position.x) > 0.5 or  abs(pos.z - self.position.z) > 0.5:
			posList = BigWorld.collide( self.spaceID, ( pos.x, pos.y+10, pos.z ), ( pos.x, pos.y-10, pos.z ) )
			if posList == None:
				pos = self.position
			else:
				pos = posList[0]

			self.gotoPosition( pos )

	def queryRelation( self, entity ):
		"""
		virtual method.
		ȡ���Լ���Ŀ��Ĺ�ϵ

		@param entity: ����Ŀ��entity
		@return : RELATION_*
		"""
		#if self.isDestroyed or entity.isDestroyed:
		#	return csdefine.RELATION_NOFIGHT
		
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.queryRelation( self, entity )
		
		if entity.id == self.ownerID:
			return csdefine.RELATION_FRIEND
			
		return Monster.queryRelation( self, entity )
		
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
