# -*- coding: gb18030 -*-

import BigWorld
import csdefine
from bwdebug import *

from Monster import Monster
from interface.CombatUnit import CombatUnit

class MonsterBelongTeam( Monster ):
	"""
	�����������������ˢ�µ�SpawnPointBelongTeamʹ��
	"""
	def __init__( self ):
		Monster.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM )
		
	def queryRelation( self, entity ):
		"""
		virtual method.
		ȡ���Լ���Ŀ��Ĺ�ϵ
		@param entity: ����Ŀ��entity
		@return : RELATION_*
		"""
		#if self.isDestroyed or entity.isDestroyed:
		#	return csdefine.RELATION_FRIEND
		
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND

		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.queryRelation( self, entity )
			
		e = entity
		if entity.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = e.getOwner()
			if owner.etype == "MAILBOX" :
				return csdefine.RELATION_FRIEND
			e = owner.entity
			
		if not isinstance( e, CombatUnit ):
			return csdefine.RELATION_FRIEND
		elif e.isState( csdefine.ENTITY_STATE_PENDING ):
			return csdefine.RELATION_NOFIGHT
		elif e.isState( csdefine.ENTITY_STATE_QUIZ_GAME ):
			return csdefine.RELATION_NOFIGHT
		elif e.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			# GM�۲���ģʽ
			if e.effect_state & csdefine.EFFECT_STATE_WATCHER:
				return csdefine.RELATION_NOFIGHT
			
			if e.teamMailbox and self.belong == e.teamMailbox.id:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE
		elif e.isEntityType( csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM ):
			if self.belong == e.belong:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		return csdefine.RELATION_FRIEND
	
	def createObjectNear( self, npcID, position, direction, state ):
		"""
		virtual method.
		����һ��entity
		@param npcID: STRING, ����ҿ��ƶ����Ψһ��ʶ
		@param position: ������Ŀ��λ��
		@param direction: ������Ŀ�귽��
		@param state: see also: cell::BigWorld.createEntity()
		@return: new entity
		"""
		state[ "belong" ] = self.belong
		return Monster.createObjectNear( self, npcID, position, direction, state )