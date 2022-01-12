# -*- coding: gb18030 -*-
# $Id: NPC108Star.py,v 1.11 2008-08-21 03:26:27 kebiao Exp $


import math
import Math
import BigWorld

from bwdebug import *
import Language
import csdefine
import csstatus
import random
import csconst
import ECBExtend
import csarithmetic
from interface.CombatUnit import CombatUnit
from ObjectScripts.GameObjectFactory import g_objFactory
from Resource.Skills.SpellBase.CombatSpell import *

from Monster import Monster



class MonsterCityWar( Monster ):
	"""
	������ս ���� ͳ˧��С�ֵ�...
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_TONG_CITYWAR_MONSTER )
		self.think( 0.1 )

	def isChildMonster( self ):
		return self.monsterType == csdefine.TONG_CW_FLAG_MONSTER

	def isXJ( self ):
		return self.monsterType == csdefine.TONG_CW_FLAG_XJ

	def isLP( self ):
		return self.monsterType == csdefine.TONG_CW_FLAG_LP

	def isTower( self ):
		return self.monsterType == csdefine.TONG_CW_FLAG_TOWER

	def isFriend( self, player ):
		return self.belong == player.tong_dbID
		
	def doGoBack( self ):
		"""
		"""
		if self.isTower():
			self.changeSubState( csdefine.M_SUB_STATE_GOBACK )
			if self.isDestroyed or self.state == csdefine.ENTITY_STATE_DEAD:
				return	
			Monster.onMovedOver( self, False )
		else:
			Monster.doGoBack( self )

	def canThink( self ):
		"""
		virtual method.
		�ж��Ƿ����think
		"""
		if self.state == csdefine.ENTITY_STATE_DEAD or self.isDestroyed: 										# ������ֹͣthink
			return False
		elif self.getSubState() == csdefine.M_SUB_STATE_GOBACK: 					# ���Ŀǰû����ҿ����һ����ڻ��ߣ���ô�ҽ�ֹͣthink
			return False
		return True

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
			if self.isFriend( e ):
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE
		elif e.isEntityType( csdefine.ENTITY_TYPE_TONG_CITYWAR_MONSTER ):
			if self.belong == e.belong:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		return csdefine.RELATION_FRIEND

	def doRandomWalk( self ):
		"""
		���ת�ƴ���
		"""
		if self.isTower() or self.isLP() or self.isXJ():
			return
		Monster.doRandomWalk( self )
	
	def receiveDamage( self, casterID, skillID, damageType, damage ):
		# �ܵ��˺�
		Monster.receiveDamage( self, casterID, skillID, damageType, damage )
		entity = BigWorld.entities.get( casterID )
		
		if entity:
			if self.damageToIntegral and entity.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
				integral = damage / self.damageToIntegral
				self.getCurrentSpaceBase().cell.addTongIntegral( entity.tong_dbID, integral )
	
	def full( self ):
		# ��ս�������������ս�������
		if self.HP != 0:
			return
		
		Monster.full( self )