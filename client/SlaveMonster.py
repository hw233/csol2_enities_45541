
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
	����NPC��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		Monster.__init__( self )
		
	def isOwn( self ) :
		"""
		�жϳ����Ƿ��� BigWorld.player �ĳ���
		"""
		return self.ownerID == BigWorld.player().id

	def queryRelation( self, entity ):
		"""
		virtual method.
		ȡĿ����Լ��Ĺ�ϵ
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
		��ȡ��ϵ�ж�����ʵentity
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
			