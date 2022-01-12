# -*- coding:gb18030 -*-

from SpellBase import Spell
from bwdebug import *

class Spell_121094( Spell ):
	"""
	NPC技能，减少目标的技能cooldown
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.param1 = 0
		self.cooldownTypeIDs = []
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.param1 = int( dict["param1"] if len( dict["param1"] ) > 0 else 0 )			#cooldown时间减少值

	def receive( self, caster, receiver ):
		if not hasattr( receiver, "attrCooldowns" ):
			ERROR_MSG( "receiver( id:%i, name:%s ) has no attrCooldowns" % ( receiver.id, receiver.getName() ) )
			return
		DEBUG_MSG( "before...receiver.attrCooldowns", receiver.getName(), receiver.attrCooldowns.items() )
		for typeID, timeVal in receiver.attrCooldowns.iteritems():
			lastTime = receiver.attrCooldowns[typeID][0] - self.param1
			totalTime = receiver.attrCooldowns[typeID][1] - self.param1
			endTimeVal = receiver.attrCooldowns[typeID][2] - self.param1
			if lastTime <= 0:
				receiver.changeCooldown( typeID, 0, 0, 0 )
				self.cooldownTypeIDs.append( typeID )
			else:
				receiver.changeCooldown( typeID, lastTime, totalTime, endTimeVal )	# changeCooldown's param: cdTypeID, lastTime, totalTime, endTimeVal
		for typeID in self.cooldownTypeIDs:
			if receiver.attrCooldowns.has_key( typeID ):
				del receiver.attrCooldowns[typeID]
		self.cooldownTypeIDs = []
		DEBUG_MSG( "after...receiver.attrCooldowns", receiver.getName(), receiver.attrCooldowns.items() )
		