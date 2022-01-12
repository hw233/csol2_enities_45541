# -*- coding:gb18030 -*-

from SpellBase import Spell
from bwdebug import *

class Spell_323097( Spell ):
	"""
	GM技能，清除目标的技能cooldown
	"""
	def receive( self, caster, receiver ):
		if not hasattr( receiver, "attrCooldowns" ):
			ERROR_MSG( "receiver( id:%i, name:%s ) has no attrCooldowns" % ( receiver.id, receiver.getName() ) )
			return
		DEBUG_MSG( "before...receiver.attrCooldowns", receiver.getName(), receiver.attrCooldowns.items() )
		for typeID, timeVal in receiver.attrCooldowns.iteritems():
			receiver.changeCooldown( typeID, 0, 0, 0 )	# changeCooldown's param: cdTypeID, lastTime, totalTime, endTimeVal
		receiver.attrCooldowns.clear()
		DEBUG_MSG( "after...receiver.attrCooldowns", receiver.getName(), receiver.attrCooldowns.items() )
		