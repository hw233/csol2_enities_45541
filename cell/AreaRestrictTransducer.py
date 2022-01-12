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

class AreaRestrictTransducer( NPCObject, CombatUnit, AmbulantObject ):
	"""
	�������ƴ�������
	���ã��Խ�������뿪���������ҽ���ĳЩ�������ƣ����̯���ƣ�PK����
	"""
	def __init__( self ):
		NPCObject.__init__( self )
		CombatUnit.__init__( self )
		AmbulantObject.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_PROXIMITY_TRANSDUCER )

		if self.radius > 0.0:
			self.controlID = self.addProximityExt( self.radius, 0x01 )
		
		if self.lifetime > 0:
			self.addTimer( self.lifetime, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )

		if self.canOpenCheckTimer():
			self.addTimer( 1000, 1000, ECBExtend.AREARESTRICTTRANSDUCER_CHECK_TIMER_CBID )
		
		if self.repeattime > 0:
			self.addTimer( self.repeattime, self.repeattime, ECBExtend.HEARTBEAT_TIMER_CBID )
	
	def canOpenCheckTimer( self ):
		"""
		�ܷ��״̬�����
		"""
		if self.casterID > 0 and self.casterMaxDistanceLife > 0:
			return True
		return False
		
	def onEnterTrapExt( self, entity, range, userData ):
		"""
		This method is associated with the Entity.addProximity method.
		It is called when an entity enters a proximity trap of this entity.

		@param entity:		The entity that has entered.
		@param range:		The range of the trigger.
		@param userData:	The user data that was passed to Entity.addProximity.
		"""
		if self.isDestroyed:
			return
		
		
		if self.enterSpell > 0:
			if self.casterID > 0:
				caster = BigWorld.entities.get( self.casterID )
			else:
				caster = self
				
			if caster:
				state = caster.spellTarget( self.enterSpell, entity.id )
				if state == csstatus.SKILL_GO_ON:
					if self.isDisposable:
						self.addTimer( 0.5 , 0, ECBExtend.DESTROY_SELF_TIMER_CBID )
				
	def onLeaveTrapExt( self, entity, range, userData ):
		"""
		virtual method.
		��ͨ�뿪����
		"""
		if self.leaveSpell > 0:
			if self.casterID > 0:
				caster = BigWorld.entities.get( self.casterID )
			else:
				caster = self

			caster.spellTarget( self.leaveSpell, entity.id )
	
	def onLevelTrapPickRemoteDo( self ):
		"""
		virtual method.
		�뿪�����ʱ�򣬵�entity, destroyΪTrueʱ�����Զ�̵ķ���������
		"""
		reList = []
		if self.leaveSpell > 0:
			reList.append( ( "systemCastSpell", [ self.leaveSpell, ] ) )
		
		return reList
			
	def _destroy( self ) :
		"""
		���٣���Ҫ��entity�뿪����
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
					caster.spellTarget( self.destroySpell, entity.id )
		
		self.destroy()
		
	def onDestroySelfTimer( self, timerID, cbID ):
		"""
		virtual method.
		ɾ������
		"""
		self._destroy()
		
	def onAreaRestrictTransducerCheckTimer( self, timerID, cbID ):
		"""
		virtual method.
		�������ƴ����� ״̬���timer
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
					caster.spellTarget( self.enterSpell, e.id )