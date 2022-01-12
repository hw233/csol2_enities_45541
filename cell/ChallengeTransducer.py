# -*- coding: gb18030 -*-

# $Id: ProximityTransducer.py,v 1.4 2007-06-14 09:55:09 huangyongwei Exp $
"""
"""

import BigWorld
from bwdebug import *
from ProximityTransducer import ProximityTransducer
import csdefine


class ChallengeTransducer( ProximityTransducer ):
	"""
	挑战副本陷阱
	"""
	def __init__( self ):
		ProximityTransducer.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_CHALLENGE_TRANSDUCER )
		
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
				