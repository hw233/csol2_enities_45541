# -*- coding: gb18030 -*-


import BigWorld
from SpellBase import Buff


class Buff_299008( Buff ):
	
	def end( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		BigWorld.player().refurbishAroundQuestStatus()
		Buff.end( self, caster, target )