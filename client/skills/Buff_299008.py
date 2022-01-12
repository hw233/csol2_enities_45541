# -*- coding: gb18030 -*-


import BigWorld
from SpellBase import Buff


class Buff_299008( Buff ):
	
	def end( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		BigWorld.player().refurbishAroundQuestStatus()
		Buff.end( self, caster, target )