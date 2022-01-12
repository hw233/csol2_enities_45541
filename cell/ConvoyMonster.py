# -*- coding: gb18030 -*-

import BigWorld
from interface.CombatUnit import CombatUnit
from Monster import Monster
import csdefine

class ConvoyMonster( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_CONVOY_MONSTER )
		self.ownerID = 0
		self.ownerName = ""

	def setOwner( self, playerID ):
		"""
		"""
		self.ownerID = playerID
		owner = BigWorld.entities.get( playerID )
		self.addCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_FRIEND_ID, self.ownerID )

	def getOwnerID( self ):
		"""
		����Լ����˵� id
		"""
		return self.ownerID
		
	def getOwner( self ):
		"""
		��������ߵ�baseMailBox
		"""
		return self.queryTemp( "npc_ownerBase", None )
		
	def queryRelation( self, entity ):
		"""
		@param entity: ����Ŀ��entity
		@return : RELATION_*
		"""
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
		
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.queryRelation( self, entity )
		
		if isinstance( entity, Monster) and self.battleCamp and self.battleCamp == entity.battleCamp:			# ���Ŀ���ǹ����Ҹ��Լ�����ͬһ����Ӫ
			return csdefine.RELATION_FRIEND
			
		if not isinstance( entity, CombatUnit ):
			return csdefine.RELATION_FRIEND
			
		if isinstance( entity, Monster):		
			if entity.flags & ( 1 << csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER ) and self.flags & ( 1 << csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER ):	# ������and��Ҫ��Ϊ�˼���ԭ�������ã�ֻ�л��͹��Լ������пɱ����﹥���ı��ʱ�������Ĺ���ս��
				return csdefine.RELATION_ANTAGONIZE
			else:
				return csdefine.RELATION_FRIEND
			
		return csdefine.RELATION_NOFIGHT

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
	
	def defDestroy( self ):
		"""
		define method
		"""
		owner = self.getOwner()
		if owner:
			self.removeCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_FRIEND_ID, self.getOwnerID() )
		self.destroy()
		
	def doRandomWalk( self ):
		"""
		"""
		pass	# ��������߶�����
		
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