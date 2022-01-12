# -*- coding: gb18030 -*-

import BigWorld
# common
import csconst
import csdefine
# cell
from Monster import Monster

class NPCFormationServant( Monster ):
	"""
	被布阵NPC（佣人）
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		if self.owner:
			self.owner.cell.remoteScriptCall( "registerLineup", ( self.id, ) )				# 把自己放到主人的布阵列表中去

	def getOwner( self ):
		"""
		获得自己主人的baseMailBox
		"""
		owner = BigWorld.entities.get( self.getOwnerID() )
		if owner:
			return owner
		else:
			return self.owner
			
	def getOwnerID( self ):
		"""
		获得主人的ID
		"""
		return self.ownerID
		
	def setOwner( self, ownerEntity ):
		self.owner = ownerEntity
		self.ownerID = ownerEntity.id
		self.owner.remoteScriptCall( "registerLineup", ( self.id, ) )			# 把自己放到主人的布阵列表中去
		self.addCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_FRIEND_ID, self.ownerID )
	
	def setToOwnerPos( self, pos):
		"""
		define method.
		设置相对于主人的坐标
		"""
		self.toOwnerPos = tuple( pos )
	
	def gotoToOwnerPos( self ):
		"""
		走到相对于主人的位置
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
		取得自己与目标的关系

		@param entity: 任意目标entity
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
