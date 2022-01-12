# -*- coding: gb18030 -*-
"""
"""

import BigWorld
from bwdebug import *
from NPCObject import NPCObject
import csdefine
import Function
from ProximityTransducer import ProximityTransducer
import random

class RandomProximityTransducer( ProximityTransducer ):
	"""
	玩家在随机的一处碰到陷阱，这陷阱有一定几率触发，陷阱触发后，要隔一段可配置时间再可触发
	作用：产生一个不能移动的entity，当有entity到达某一位置时，根据配置的几率，执行一件事情
	"""
	def __init__( self ):
		"""
		"""
		ProximityTransducer.__init__( self )		
		self.enterTime = 0.0
		
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
			if random.random() <= self.triggerRate and self.radius > 0.0:									# 根据触发几率，决定是否触发触发陷阱
				if BigWorld.time() - self.enterTime < self.triggerInterval:									# 如果触发陷阱的时间小于触发间隔，则不触发陷阱
					return 
				self.enterTime = BigWorld.time()																# 记录进入陷阱的时间
				script.onEnterTrapExt( self, entity, range, userData )
	
# end of RandomProximityTransducer.py
