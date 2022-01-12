
# -*- coding: gb18030 -*-
#
# $Id: SlaveMonster.py,v 1.1 2008-09-01 06:00:34 zhangyuxing Exp $


import csdefine
import event.EventCenter as ECenter
import BigWorld
from Monster import Monster
from NPCObject import NPCObject
from gbref import rds


class SlaveMonster( Monster ):
	"""
	怪物NPC类
	"""
	def __init__( self ):
		"""
		初始化
		"""
		Monster.__init__( self )
		
	def isOwn( self ) :
		"""
		判断宠物是否是 BigWorld.player 的宠物
		"""
		return self.ownerID == BigWorld.player().id

	def queryRelation( self, entity ):
		"""
		virtual method.
		取目标和自己的关系
		"""
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.queryRelation( self, entity )
		
		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if entity.id == self.ownerID:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_NEUTRALLY

		if entity.isEntityType( csdefine.ENTITY_TYPE_MONSTER ):
			return csdefine.RELATION_NEUTRALLY


		return csdefine.RELATION_NEUTRALLY
		
	def getRelationEntity( self ):
		"""
		获取关系判定的真实entity
		"""
		owner = BigWorld.entities.get( self.ownerID, None )
		if not owner:
			return None
		else:
			return owner
			
	def queryCombatRelation( self, entity ):
		owner = BigWorld.entities.get( self.ownerID, None )
		if not owner:
			return csdefine.RELATION_ANTAGONIZE
		else:
			return owner.queryCombatRelation( entity )
			