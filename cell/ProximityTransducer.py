# -*- coding: gb18030 -*-

# $Id: ProximityTransducer.py,v 1.4 2007-06-14 09:55:09 huangyongwei Exp $
"""
"""

import BigWorld
from bwdebug import *
from NPCObject import NPCObject
import csdefine


class ProximityTransducer( NPCObject ):
	"""
	接近触发器；
	作用：产生一个不能移动的entity，当有entity靠近的时候触发，执行一件事情
	"""
	def __init__( self ):
		NPCObject.__init__( self )

		self.setEntityType( csdefine.ENTITY_TYPE_PROXIMITY_TRANSDUCER )

		if self.radius > 0.0:
			self.proximityControlID = self.addProximityExt( self.radius, 0x01 )

	def onEnterTrapExt( self, entity, range, userData ):
		"""
		This method is associated with the Entity.addProximity method.
		It is called when an entity enters a proximity trap of this entity.

		@param entity:		The entity that has entered.
		@param range:		The range of the trigger.
		@param userData:	The user data that was passed to Entity.addProximity.
		"""
		script = self.getScript()
		if script is not None and hasattr( script, "onEnterTrapExt" ):
			script.onEnterTrapExt( self, entity, range, userData )

	def onLeaveTrapExt( self, entity, range, userData ):
		"""
		This method is associated with the Entity.addProximity method.
		It is called when an entity leaves a proximity trap of this entity.

		@param entity:		The entity that has left.
		@param range:		The range of the trigger.
		@param userData:	The user data that was passed to Entity.addProximity.
		"""
		script = self.getScript()
		if script is not None and hasattr( script, "onLeaveTrapExt" ):
			script.onLeaveTrapExt( self, entity, range, userData )
# end of ProximityTransducer.py
