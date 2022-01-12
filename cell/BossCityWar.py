# -*- coding: gb18030 -*-
# $Id: NPC108Star.py,v 1.11 2008-08-21 03:26:27 kebiao Exp $

import BigWorld
from Monster import Monster
from bwdebug import *
import Language
import csdefine
import csstatus
from ObjectScripts.GameObjectFactory import g_objFactory
import random
import ECBExtend
from interface.CombatUnit import CombatUnit
from Resource.Skills.SpellBase.CombatSpell import *


class BossCityWar( Monster ):
	"""
	������ս ͳ˧��...
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_TONG_CITYWAR_MONSTER )		
		self.think( 0.1 )

	def receiveDamage( self, casterID, skillID, damageType, damage ):
		"""
		boss�ܵ��˺�
		"""
		Monster.receiveDamage( self, casterID, skillID, damageType, damage )
		entity = BigWorld.entities.get( casterID )
		if self.damageToIntegral and entity.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
			integral = damage / self.damageToIntegral
			self.getCurrentSpaceBase().cell.addTongIntegral( entity.tong_dbID, integral )

	def afterDie( self, killerID ):
		"""
		virtual method.

		������ص���ִ��һЩ�����ڹ�����������������顣
		"""
		Monster.afterDie( self, killerID )
		spaceBase = self.getCurrentSpaceBase()
		spaceEntity = None

		try:
			spaceEntity = BigWorld.entities[ spaceBase.id ]
		except:
			DEBUG_MSG( "not find the spaceEntity!" )

		if spaceEntity and spaceEntity.isReal():
			spaceEntity.getScript().onBossDied( spaceEntity )
		elif spaceBase:
			spaceBase.cell.remoteScriptCall( "onBossDied", [] )
			
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
			if self.belong == e.tong_dbID:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE
		elif e.isEntityType( csdefine.ENTITY_TYPE_TONG_CITYWAR_MONSTER ):
			if self.belong == e.belong:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		return csdefine.RELATION_FRIEND

	def canThink( self ):
		"""
		virtual method.
		�ж��Ƿ����think
		"""
		if self.state == csdefine.ENTITY_STATE_DEAD or self.isDestroyed: 									# ������ֹͣthink
			return False
		if self.getSubState() == csdefine.M_SUB_STATE_GOBACK: 					# ���Ŀǰû����ҿ����һ����ڻ��ߣ���ô�ҽ�ֹͣthink
			return False
		return True
	
	def full( self ):
		# ��ս�������������ս�������
		if self.HP != 0:
			return
		
		Monster.full( self )