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
		获得自己主人的 id
		"""
		return self.ownerID
		
	def getOwner( self ):
		"""
		获得所有者的baseMailBox
		"""
		return self.queryTemp( "npc_ownerBase", None )
		
	def queryRelation( self, entity ):
		"""
		@param entity: 任意目标entity
		@return : RELATION_*
		"""
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
		
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.queryRelation( self, entity )
		
		if isinstance( entity, Monster) and self.battleCamp and self.battleCamp == entity.battleCamp:			# 如果目标是怪物且跟自己属于同一个阵营
			return csdefine.RELATION_FRIEND
			
		if not isinstance( entity, CombatUnit ):
			return csdefine.RELATION_FRIEND
			
		if isinstance( entity, Monster):		
			if entity.flags & ( 1 << csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER ) and self.flags & ( 1 << csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER ):	# 这里用and主要是为了兼容原来的配置，只有护送怪自己身上有可被怪物攻击的标记时才能与别的怪物战斗
				return csdefine.RELATION_ANTAGONIZE
			else:
				return csdefine.RELATION_FRIEND
			
		return csdefine.RELATION_NOFIGHT

	def onBootyOwnerChanged( self ) :
		"""
		virtual method
		这类怪物没有归属权的概念
		"""
		pass

	def queryBootyOwner( self, scrEntityID ) :
		"""
		Exposed method
		客户端申请查询怪物的归属权
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
		pass	# 屏蔽随机走动功能
		
	def getRelationEntity( self ):
		"""
		获取关系判定的真实entity
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