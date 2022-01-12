# -*- coding: gb18030 -*-
# SlaveMonster.py
# $Id: SlaveMonster.py,v 1.1 2008-09-01 03:34:03 zhangyuxing Exp $

#################################################################################
#拥有主人的怪物，与宠物类似，但是远比宠物简单，而且主人可以是怪物
#################################################################################

from bwdebug import *
from interface.CombatUnit import CombatUnit
from Monster import Monster
import csdefine
import csstatus
import BigWorld
import csconst
import cschannel_msgs
import ECBExtend
import Const
import random

class SlaveMonster( Monster ):
	"""
	怪物类，续承于NPC和可战斗单位
	"""
	def __init__(self):
		Monster.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_SLAVE_MONSTER )


	def getOwner( self ):
		"""
		获得自己主人的baseMailBox
		"""
		return self.queryTemp( "ownerBaseMailBox", None )


	def getOwnerID( self ):
		"""
		获得自己主人的 id
		"""
		return self.ownerID

	def setOwner( self, owner ):
		"""
		"""
		self.ownerID = owner.id
		#self.setTemp( "ownerName", owner.getName() )
		self.ownerName = owner.getName()
		if owner.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ):
			# 如果保镖的主人是镖车，存储的主人名字应该是玩家的
			self.ownerName = owner.ownerName
		owner.setTemp( "dart_id", self.id )	#存储镖车id到玩家身上
		self.addCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_FRIEND_ID, self.ownerID )
		if owner.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			self.setTemp( "ownerBaseMailBox", owner.base )
		else:
			if owner.queryTemp( "ownerBaseMailBox", None) is not None:
				self.setTemp( "ownerBaseMailBox", owner.queryTemp( "ownerBaseMailBox", None) )

	def queryRelation( self, entity ):
		"""
		virtual method.
		取得自己与目标的关系

		@param entity: 任意目标entity
		@return : RELATION_*
		"""
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.queryRelation( self, entity )
		
		if isinstance( entity, Monster) and self.battleCamp and self.battleCamp == entity.battleCamp:			# 如果目标是怪物且跟自己属于同一个阵营
			return csdefine.RELATION_FRIEND

		slaveOwner = BigWorld.entities.get( self.ownerID )

		if slaveOwner == None or not slaveOwner.isReal():
			return csdefine.RELATION_ANTAGONIZE

		if not isinstance( entity, CombatUnit ):
			return csdefine.RELATION_FRIEND

		if isinstance( entity, SlaveMonster ) and self.ownerName == entity.ownerName:
			return csdefine.RELATION_FRIEND

		if hasattr( entity, "getName" ) and self.ownerName == entity.getName():
			return csdefine.RELATION_FRIEND

		return csdefine.RELATION_ANTAGONIZE


	def isInTeam( self ) :
		"""
		是否在队伍中
		"""
		owner = BigWorld.entities.get( self.getOwnerID() )
		if owner is None : return False
		return owner.isInTeam()

	def flyToMasterSpace( self ):
		"""
		define method
		飞到主人所在的位置
		"""
		self.addTimer( 2.0, 0.0, ECBExtend.FLY_TO_MASTER_CB )

	def flyToMasterCB( self, controllerID, userData ):
		"""
		"""
		ownerID = self.getOwnerID()
		if BigWorld.entities.has_key( ownerID ):
			owner = BigWorld.entities[ ownerID ]
			self.teleport( owner, owner.position + ( random.randint(-2,2), 0,random.randint(-2,2) ), owner.direction )
			if self.isReal():
				self.stopMoving()
		else:
			self.queryTemp('ownerBaseMailBox').cell.requestTakeToMaster( self.base )


	def onReceiveMasterInfo( self, cellMailBox, position ):
		"""
		define method
		得到主人回复提供cellMailbox 和 position
		"""
		self.teleport( cellMailBox, position + ( random.randint(-2,2), 0,random.randint(-2,2) ), ( 0, 0, 0 ) )

	def calculateBootyOwner( self ):
		"""
		"""
		Monster.calculateBootyOwner( self )

	def onEnterTrapExt( self, entity, range, controllerID ):
		"""
		Entity.onEnterTrapExt( entity, range, controllerID )
		"""
		# 当有entity 进入怪物的陷阱范围之内，此函数就会被调用
		state = self.getState()
		#if state == csdefine.ENTITY_STATE_FIGHT:						# 休息状态.....似乎没有用到
			# 在战斗状态的时候取消陷井
		#	self.cancel( controllerID )
		#	return
		if self.getSubState() == csdefine.M_SUB_STATE_GOBACK:
			return

		if not hasattr( entity, "getState" ):
			return

		plState = entity.getState()
		if plState == csdefine.ENTITY_STATE_PENDING or plState == csdefine.ENTITY_STATE_DEAD or plState == csdefine.ENTITY_STATE_QUIZ_GAME:
			return												# 玩家处于销毁状态或死亡状态或问答状态，什么也不做

		self.aiTargetID = entity.id
		self.doAllEventAI( csdefine.AI_EVENT_SPELL_ENTERTRAP )
		self.aiTargetID = 0
		
		# 给帮会中满足条件的成员（等级在押镖者正负3级内）加一个获取镖车敌人的buff
		if self.queryTemp( "ownerTongDBID", None ):
			if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and self.queryTemp( "ownerTongDBID" ) == entity.tong_dbID:
				ownerID = self.getOwnerID()
				if BigWorld.entities.has_key( ownerID ):
					ownerLevel = BigWorld.entities[ ownerID ].getLevel()
				else:
					ownerLevel = self.queryTemp( "level", 0 )
				if entity.getLevel() <= ownerLevel + 3 and entity.getLevel() >= ownerLevel - 3:
					self.spellTarget( 122372001, entity.id )		# 给玩家加一个获取自己敌人的buff

	def dartMissionBrocad( self, killer, factionID ):
		"""
		运镖或劫镖成功的广播 by姜毅14:10 2009-7-31
		@param missionType : 任务类型
		@param missonnType : UINT8
		"""
		#self.family_grade
		killer.brocastMessageSlaveDart( factionID )

	def calcKillerPkValue( self, killer ):
		"""
		计算pk值
		@param    killer: 把我干掉的人
		@type     killer: RoleEntity
		"""
		# 判断杀手是否是Role。如果是宠物，要算主人的
		if killer == None: return
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" : return
			killer = owner.entity
		if not killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ): return
		if killer.pkState == csdefine.PK_STATE_PROTECT: return
		killer.addPkValue( 12 )


	def destoryDartEntity( self ):
		"""
		define method
		"""
		self.setTemp( 'dartQuestAbandoned', True )
		owner = self.getOwner()
		if owner:
			self.removeCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_FRIEND_ID, self.getOwnerID() )
		self.addTimer( csconst.MONSTER_CORPSE_DURATION, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )

	def doGoBack( self ):
		"""
		移动回作战位置
		"""
		self.resetEnemyList()

	def doRandomWalk( self ):
		"""
		"""
		pass

	def getTeamMailbox( self ):
		"""
		"""
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