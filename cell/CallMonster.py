# -*- coding: gb18030 -*-

from bwdebug import *
from Monster import Monster

import csdefine
import csstatus
import BigWorld
import csconst
import ECBExtend
import Const
import random

from interface.CombatUnit import CombatUnit

# 召唤类怪物
class CallMonster( Monster ):
	def __init__( self ):
		Monster.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_CALL_MONSTER)
		if self.owner:
			# 把自己注册到主人身上
			self.owner.cell.registerCallMonster( self.base )

	def getOwner( self ):
		# 获得自己主人的baseMailBox
		owner = BigWorld.entities.get( self.owner.id )
		if owner:
			return owner
		else:
			return self.owner
		
	def setOwner( self, ownerBase ):
		# define method.
		# ownerBase : master base mailbox
		self.owner = ownerBase
		self.ownerID = ownerBase.id
		self.owner.cell.registerCallMonster( self.base ) # 重新注册自己到主人身上
		self.addCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_FRIEND_ID, ownerBase.id )
	
	def getOwnerID( self ):
		if self.owner:
			return self.owner.id
		return 0

	def queryRelation( self, entity ):
		"""
		virtual method.
		获取召唤entity与指定 entity 的关系
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

		if entity.effect_state & csdefine.EFFECT_STATE_PROWL:	# 如果entity处于潜行效果状态
			return csdefine.RELATION_NOFIGHT

		ownerEntity = BigWorld.entities.get( self.getOwnerID(), None )
		if ownerEntity == None :
			return csdefine.RELATION_NONE
		else :
			return ownerEntity.queryRelation( entity )

	def isInTeam( self ) :
		ownerEntity = BigWorld.entities.get( self.owner.id )
		if ownerEntity is None :
			return False

		return ownerEntity.isInTeam()

	def flyToMasterSpace( self ):
		"""
		define method
		飞到主人所在的位置
		"""
		self.addTimer( 2.0, 0.0, ECBExtend.FLY_TO_MASTER_CB )

	def flyToMasterCB( self, controllerID, userData ):
		# timer call back 飞到主人的位置
		if BigWorld.entities.has_key( self.getOwnerID() ):
			owner = BigWorld.entities[ self.getOwnerID() ]
			self.followMaster( int( owner.getCurrentSpaceData( csconst.SPACE_SPACEDATA_SPACE_TYPE_KEY ) ), owner, owner.position )
			if not self.isDestroyed and self.isReal():
				self.stopMoving()
		else:
			self.owner.cell.onRemoteFollowCallMonster( self.base )

	def followMaster( self, spaceType, cellMailBox, position ):
		"""
		define method
		得到主人回复提供space type, cellMailbox 和 position
		"""
		if spaceType in self.spaceEnable or len( self.spaceEnable ) == 0:
			self.teleport( cellMailBox, position + ( random.randint(-2,2), 0,random.randint(-2,2) ), ( 0, 0, 0 ) )
		else:
			self.destroy()

	def calculateBootyOwner( self ):
		# 计算战利品
		Monster.calculateBootyOwner( self )
	
	def onDestroy( self ):
		# entity 销毁的时候由BigWorld.Entity自动调用
		self.owner.cell.removeCallMonster( self.base ) # 从主人的召唤列表中移出
		self.removeCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_FRIEND_ID, self.getOwnerID() )
		Monster.onDestroy( self )

	def doGoBack( self ):
		"""
		移动回作战位置
		"""
		if self.isDestroyed or self.state == csdefine.ENTITY_STATE_DEAD:
			return
		self.resetEnemyList()

	def doRandomWalk( self ):
		"""
		"""
		pass

	def isInTeam( self ) :
		owner = BigWorld.entities.get( self.getOwnerID() )
		if not owner:
			return False
		return owner.isInTeam()

	def getTeamMailbox( self ):
		owner = BigWorld.entities.get( self.getOwnerID() )
		if not owner:
			return None
		return owner.getTeamMailbox()

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
	
	def onOwnerDestroy( self ):
		# define method
		# 如果主人下线了
		self.owner = None
		self.ownerID = 0
		if self.waitOwnerInWorld:
			self.destroy()
	
	def onOwnerCallMonster( self, entityID ):
		# define mothod.
		# 主人召唤怪物
		if self.className == entityID: # 如果主人重新召唤与自己一样的怪物，则把自己销毁
			self.destroy()
			
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
