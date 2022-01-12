# -*- coding: gb18030 -*-

# 2008-11-26 gjx&lq

import BigWorld
import ECBExtend
from bwdebug import *
from NPCObject import NPCObject
from interface.CombatUnit import CombatUnit
from interface.AmbulantObject import AmbulantObject
import csdefine
import csstatus
import Love3
from Resource.SkillLoader import g_skills
import SkillTargetObjImpl

class SkillTrap( NPCObject, CombatUnit, AmbulantObject ):
	"""
	技能陷阱
	"""
	def __init__( self ):
		NPCObject.__init__( self )
		CombatUnit.__init__( self )
		AmbulantObject.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_SKILL_TRAP )

		if self.lifetime > 0:
			self.addTimer( self.lifetime, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )

		if self.canOpenCheckTimer():
			self.addTimer( 1000, 1000, ECBExtend.AREARESTRICTTRANSDUCER_CHECK_TIMER_CBID )

		if self.repeattime > 0:
			self.addTimer( self.repeattime, self.repeattime, ECBExtend.HEARTBEAT_TIMER_CBID )

	def canOpenCheckTimer( self ):
		"""
		能否打开状态检查器
		"""
		if self.casterID > 0 and self.casterMaxDistanceLife > 0:
			return True
		return False

	def onEnterTrap( self, srcEntityID, entityID ):
		"""
		Exposed method
		有entity进入陷阱
		"""
		try:
			entity = BigWorld.entities[entityID]
		except KeyError:
			ERROR_MSG( "entity(%i) not exist in world" % entityID )
			return

		if abs( entity.position.y - self.position.y ) > self.radius:
			return 

		self.enterTrapDo( entity )

	def onLeaveTrap( self, srcEntityID, entityID ):
		"""
		Exposed method
		有entity离开陷阱
		"""
		try:
			entity = BigWorld.entities[entityID]
		except KeyError:
			ERROR_MSG( "entity(%i) not exist in world" % entityID )
			return

		self.leaveTrapDo( entity )

	def __skillCheck( self, skill, caster, target ):
		"""
		技能检查
		"""
		# 施法者检查
		state = skill.castValidityCheck( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# 检查目标是否符合法术施展
		state = skill.getCastObject().valid( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		return csstatus.SKILL_GO_ON

	def trapSpellTarget( self, skillID, caster, targetEntity ):
		skill  = g_skills[ skillID ]
		skillTarget = SkillTargetObjImpl.createTargetObjEntity( targetEntity )
		state = self.__skillCheck( skill, caster, skillTarget )
		if state == csstatus.SKILL_GO_ON:
			skill.trapCast( caster, skillTarget )

		return state

	def enterTrapDo( self, entity ):
		"""
		进入陷阱调用
		"""
		if self.isDestroyed or self.isTrigger:
			return

		if self.enterSpell > 0:
			if self.casterID > 0:
				caster = BigWorld.entities.get( self.casterID )
			else:
				caster = self

			if caster:
				if self.trapSpellTarget( self.enterSpell, caster, entity ) == csstatus.SKILL_GO_ON:
					if self.isDisposable:
						self.isTrigger = True
						self.addTimer( 0.5 , 0, ECBExtend.DESTROY_SELF_TIMER_CBID )

	def leaveTrapDo( self, entity ):
		"""
		离开陷阱调用
		"""
		if self.isDestroyed:
			return

		if self.leaveSpell > 0:
			if self.casterID > 0:
				caster = BigWorld.entities.get( self.casterID )
			else:
				caster = self
			if entity.isDestroyed :
				baseMailbox = self.getGBAE()
				if baseMailbox is None :
					ERROR_MSG( "The baseMailbox should not be None, or all of that must have been breakdown!" )
					return
				baseMailbox.castSpellBroadcast( entity.id, self.leaveSpell )
			else:
				if caster:
					self.trapSpellTarget( self.leaveSpell, caster, entity )

	def _destroy( self ) :
		"""
		销毁，需要做entity离开陷阱
		"""
		if self.destroySpell > 0:
			if self.casterID > 0:
				caster = BigWorld.entities.get( self.casterID )
			else:
				caster = self

			for entity in self.entitiesInRangeExt( self.radius, None, self.position ):
				if entity.isDestroyed:
					baseMailbox = self.getGBAE()
					if baseMailbox is None :
						ERROR_MSG( "The baseMailbox should not be None, or all of that must have been breakdown!" )
						return
					baseMailbox.castSpellBroadcast( entity.id, self.destroySpell )
				else :
					self.trapSpellTarget( self.destroySpell, caster, entity )

		self.destroy()

	def onDestroySelfTimer( self, timerID, cbID ):
		"""
		virtual method.
		删除自身
		"""
		self._destroy()

	def onAreaRestrictTransducerCheckTimer( self, timerID, cbID ):
		"""
		virtual method.
		区域限制触发器 状态检查timer
		"""
		if self.casterID > 0:
			caster = BigWorld.entities.get( self.casterID )
			if self.casterMaxDistanceLife > 0:
				if caster is None or caster.isDestroyed or self.position.flatDistTo( caster.position ) > self.casterMaxDistanceLife:
					self._destroy()
					return

	def onHeartbeat( self, timerID, cbID ):
		if self.isDestroyed:
			return

		entities = self.entitiesInRangeExt( self.radius, None, self.position )
		if self.enterSpell > 0 and len( entities ) > 0:
			for e in entities:
				if self.casterID > 0:
					caster = BigWorld.entities.get( self.casterID )
				else:
					caster = self
					
				if caster:
					self.trapSpellTarget( self.enterSpell, caster, e )
