# -*- coding: gb18030 -*-

import time

import BigWorld
import csdefine
from NPCObject import NPCObject

class TrapPickAnima( NPCObject ) :
	"""
	拾取灵气专用陷阱
	"""
	def __init__( self ) :
		NPCObject.__init__( self )
		self.addProximityExt( self.trapRange )
	
	def onEnterTrapExt( self, entity, range, controllerID ):
		"""
		触发陷阱
		"""
		if entity.getEntityType() != csdefine.ENTITY_TYPE_ROLE:
			return
			
		spaceCell = self.getCurrentSpaceCell()
		if spaceCell:
			spaceCell.onTriggerTrap( entity.planesID, entity, time.time(), self.rewardPotential )
				
		self.destroy()
	
	def onLeaveTrapExt( self, entity, range, userData ):
		"""
		This method is associated with the Entity.addProximity method.
		It is called when an entity leaves a proximity trap of this entity.

		@param entity:		The entity that has left.
		@param range:		The range of the trigger.
		@param userData:	The user data that was passed to Entity.addProximity.
		"""
		pass