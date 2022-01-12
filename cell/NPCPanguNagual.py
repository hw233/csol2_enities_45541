# -*- coding: gb18030 -*-

# added by dqh

# python
import random
# bigworld
import math
import Math
import BigWorld
# common
import csconst
import csdefine
import csstatus
from bwdebug import *
# cell
from Monster import Monster
from ObjectScripts.GameObjectFactory import g_objFactory
from interface.CombatUnit import CombatUnit

class NPCPanguNagual( Monster ):
	"""
	盘古守护
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_PANGU_NAGUAL )
		
		self.__isForceFollow = False
		
		if self.owner:
			self.owner.cell.registerPGNagual( self.attackType, self.id )				# 把自己注册到主人身上

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
		
	def setOwner( self, ownerBase ):
		# define method.
		# ownerBase : master base mailbox
		self.owner = ownerBase
		self.ownerID = ownerBase.id
		self.owner.cell.registerPGNagual( self.attackType, self.id )				 # 重新注册自己到主人身上
		self.addCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_FRIEND_ID, self.ownerID )
	
	def setToOwnerPos( self, xPos, angle ):
		"""
		define method.
		"""
		self.toOwnerDis = xPos
		self.toOwnerAngle = angle

	def isInTeam( self ):
		"""
		判断主人是否在队伍中
		"""
		owner = BigWorld.entities.get( self.getOwnerID() )
		if not owner:
			return False
		return owner.isInTeam()

	def getTeamMailbox( self ):
		"""
		"""
		owner = BigWorld.entities.get( self.getOwnerID() )
		if not owner:
			return None
		return owner.getTeamMailbox()

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
			
		if not isinstance( entity, CombatUnit ):
			return csdefine.RELATION_FRIEND
			
		if isinstance( entity, Monster) and self.battleCamp and self.battleCamp == entity.battleCamp:			# 如果目标是怪物且跟自己属于同一个阵营
			return csdefine.RELATION_FRIEND
	
		if entity.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ):
			return csdefine.RELATION_NOFIGHT

		ownerID = self.getOwnerID()
		if ownerID is 0:
			return csdefine.RELATION_ANTAGONIZE
			
		if BigWorld.entities.has_key( ownerID ):	#判定守护主人的敌对关系
			return BigWorld.entities[ownerID].queryRelation( entity )
			
		return csdefine.RELATION_ANTAGONIZE
		
	def addEnemyCheck( self, entityID ):
		"""
		"""
		if not Monster.addEnemyCheck( self, entityID ):
			return False
		
		entity = BigWorld.entities.get(self.getOwnerID())
		if not entity:
			return False
		
		return False


	def onAddEnemy( self, enemyID ):
		"""
		extend method.
		"""
		Monster.onAddEnemy( self, enemyID )
		owner = BigWorld.entities.get(self.getOwnerID())
		if owner:
			g_fightMgr.buildEnemyRelation( owner ,enemy )
			
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
			return csdefine.RELATION_ANTAGONIZE
			