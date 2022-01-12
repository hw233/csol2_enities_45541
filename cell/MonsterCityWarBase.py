# -*- coding: gb18030 -*-

import BigWorld
import csdefine
import csconst
from bwdebug import *
from Monster import Monster

class MonsterCityWarBase( Monster ):
	"""
	帮会夺城战决赛据点（资源据点、战斗据点、插旗点、英灵碑、护旗将）
	"""
	def __init__( self ):
		Monster.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_CITY_WAR_FINAL_BASE )
		self.ownerID = 0
		self.getScript().onCreated( self )

	def onActivated( self ):
		"""
		define method
		被激活
		"""
		self.getScript().onActivated( self )

	def onOccupied( self, belong ):
		"""
		define method
		被占领
		"""
		self.belong = belong
		self.getScript().onOccupied( self, belong )
	
	def setOwner( self, ownerID ):
		"""
		define method
		设置主人（主要是针对于资源点）
		@ ownerID:	ownerID, 资源点在战斗据点附近，正常情况下是能根据ownerID找到战斗据点的
		"""
		self.ownerID = ownerID
		owner = BigWorld.entities.get( ownerID )
		if not owner:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: I ( %i, %s ) can't get the owner %i " % ( self.id, self.className, ownerID ) )
			return
		owner.registerCityWarBase( self )

	def setBelong( self, belong ):
		"""
		define method
		设置归属
		"""
		self.belong = belong

	def getBelong( self ):
		"""
		define method
		查询归属
		"""
		return self.belong

	def registerCityWarBase( self, mailBox ):
		"""
		把资源据点注册到自己身上(主要是针对战斗据点)
		"""
		resourceList = self.queryTemp( "resourceList", [] )
		if mailBox:
			resourceList.append( mailBox )
			self.setTemp( "resourceList", resourceList )

	def getResourceBaseBelong( self, belong ):
		"""
		检查资源据点的归属情况
		若一个战斗据点的两个资源据点同时属于攻城方（或守城方），返回为True
		"""
		resourceList = self.queryTemp( "resourceList", [] )
		amount = 0
		for resourceMB in resourceList:
			if resourceMB.getBelong() == belong:
				amount += 1
		
		return amount

	def provideEnergy( self ):
		"""
		define method
		资源据点给战斗据点提供能量( 根据所属的帮会不同释放不同的技能 )
		"""
		self.spellTarget( csconst.CITY_WAR_RESOURCE_BASE_SKILL[ self.belong ], self.ownerID )

	def addEnergy( self, casterID, value ):
		"""
		战斗据点添加能量{ belong: value }
		@param value: 可正可负
		"""
		caster = BigWorld.entities.get( casterID )
		if not caster or not caster.belong:
			ERROR_MSG( "TONG_CITY_WAR_FINAL:Caster has no belong or I ( %i, %s ) can't get the caster %i " % ( self.id, self.className, casterID ) )
			return
		if caster.belong not in self.energy:
			self.energy[ caster.belong ] = 0
		
		energy = self.energy[ caster.belong ] + value
		self.energy[ caster.belong ] = energy if energy <= 100 else energy % 100
		self.energy = self.energy
		self.onEnergyChanged( caster.belong )

	def onEnergyChanged( self, belong ):
		"""
		未占领状态下战斗据点能量发生变化
		"""
		if not self.belong:
			if self.energy[ belong ] > csconst.CITY_WAR_BATTLE_BASE_ACTIVATE_LIMIT:
				self.belong = belong
				self.onOccupied( belong )
		else:
			if self.energy[ belong ] < csconst.CITY_WAR_BATTLE_BASE_ACTIVATE_LIMIT:
				self.cityWarBaseReset()

	def cityWarBaseReset( self ):
		"""
		define method
		重置
		"""
		self.getScript().reset( self )

	def onReceiveSpell( self, caster, spell ):
		"""
		法术到达的回调，由某些特殊技能调用

		@param spell: 技能实例
		"""
		self.getScript().onReceiveSpell( self, caster, spell )

	def onIncreaseQuestTaskState( self, srcEntityID ):
		"""
		define method.(只在cell上被调用) 为了共用技能Spell_313100002， 屏蔽该方法
		"""
		pass

	def taskStatus( self, srcEntityID ):
		"""
		Exposed method.
		@param srcEntityID: 调用者的ID
		@type  srcEntityID: OBJECT_ID

		任务箱子进入到某玩家的视野，任务箱子向服务器乞求它于这个玩家的关系
		"""
		try:
			playerEntity = BigWorld.entities.get( srcEntityID )
		except KeyError:
			INFO_MSG( "TONG_CITY_WAR_FINAL:entity %i not exist in world" % srcEntityID )
			return

		if playerEntity.isReal():
			self.getScript().taskStatus( self, playerEntity )
		else:
			playerEntity.taskStatusForward( self )	#资源点和玩家可能不在一个cell中（参照QuestBox的处理）

	def updateSameBelongs( self, classNames ):
		"""
		define method
		更新同归属的据点className
		"""
		self.sameBelongs = classNames
		
	def getOwnerID( self ):
		"""
		获得自己主人的 id
		"""
		return self.ownerID
		
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