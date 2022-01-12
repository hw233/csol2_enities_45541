# -*- coding: gb18030 -*-

import BigWorld
import csdefine
from MonsterBelongTeam import MonsterBelongTeam
from MonsterBuilding import MonsterBuilding
from interface.CombatUnit import CombatUnit
from bwdebug import *

class MonsterYXLM( MonsterBelongTeam, MonsterBuilding ) :
	"""
	英雄联盟怪物（塔，基地）
	"""
	def __init__( self ):
		MonsterBelongTeam.__init__( self )
		MonsterBuilding.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM )
		self.getSpaceCell().registMonster( self.className, self )
	
	def getSpaceCell( self ):
		sMB = self.getCurrentSpaceBase()
		if sMB:
			try:
				return BigWorld.entities[sMB.id]
			except KeyError:
				return sMB.cell
			
	def receiveDamage( self, casterID, skillID, damageType, damage ):
		"""
		Define and virtual method.
		接受伤害。
		@param   casterID: 施法者ID
		@type    casterID: OBJECT_ID
		@param    skillID: 技能ID
		@type     skillID: INT
		@param damageType: 伤害类型；see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: INT
		@param     damage: 伤害数值
		@type      damage: INT
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_SPEAKER ):
			return
		if self.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ):		#不可被选择的怪物，允许其他怪物攻击他，不允许玩家和宠物攻击他
			obj = BigWorld.entities.get( casterID )
			if obj and ( obj.isEntityType( csdefine.ENTITY_TYPE_PET ) or obj.isEntityType( csdefine.ENTITY_TYPE_ROLE ) ):
				return

		state = self.getState()
		subState = self.getSubState()
		hasCaster = BigWorld.entities.has_key( casterID )

		# 回走状态时，无敌状态 死亡了
		if subState == csdefine.M_SUB_STATE_GOBACK or state == csdefine.ENTITY_STATE_DEAD or \
		( hasCaster and BigWorld.entities[ casterID ].getState() == csdefine.ENTITY_STATE_DEAD ):
			return

		if not( damageType & csdefine.DAMAGE_TYPE_FLAG_BUFF ) and hasCaster:	# 不是buff伤害且施法者存在
			killerEntity = BigWorld.entities[casterID]
			# 第一次增加仇恨度，自然会进入战斗状态
			if killerEntity.getState() != csdefine.ENTITY_STATE_DEAD:
				if damageType & csdefine.DAMAGE_TYPE_FLAG_BUFF != csdefine.DAMAGE_TYPE_FLAG_BUFF:
					self.addDamageList( killerEntity.id, damage )
		
			# 如果伤害大于0
			if damage > 0 and casterID != self.id:
				self.bootyOwner = ( casterID, 0 )
				if not self.firstBruise:
					self.firstBruise = 1
					self.onFirstBruise( killerEntity, damage, skillID )
		else:
			# 没有攻击源或伤害是buff产生
			pass
		# 最后通知底层，因为如果先通知了底层，那么当怪物被一击必杀的时候很可能它根本就没进入战斗状态
		# 如果是这样的话，有些东西就不可能生效或会出错。
		CombatUnit.receiveDamage( self, casterID, skillID, damageType, damage )
	
	def sendSAICommand( self, recvIDs, type, sid ):
		"""
		发送sai指令
		"""
		self.getSpaceCell().sendSAICommand( recvIDs, type, sid, self )
	
	def recvSAICommand( self, type, sid, sendEntity ):
		"""
		define method.
		接收一个entity发过来的s ai
		"""
		self.setTemp( "SEND_SAI_ENTITY", sendEntity )
		self.insertSAI( sid )

	def openVolatileInfo( self ):
		"""
		virtual method.
		打开坐标信息传送功能
		"""
		MonsterBuilding.openVolatileInfo( self )

	def closeVolatileInfo( self ):
		"""
		virtual method.
		关闭坐标信息传送功能
		"""
		MonsterBuilding.closeVolatileInfo( self )
		
	def moveToPosFC( self, endDstPos, targetMoveSpeed, targetMoveFace ):
		"""
		连击移动
		"""
		MonsterBuilding.moveToPosFC( self, endDstPos, targetMoveSpeed, targetMoveFace )
	
	def checkViewRange( self, entity ):
		"""
		virtual method
		检测entity是否在视野范围
		判断entity是否在自己的视野范围之内
		return 	:	True	在
		return	:	False	不在
		"""
		if entity.spaceID != self.spaceID:
			return False
		return True
