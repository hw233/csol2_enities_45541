# -*- coding:gb18030 -*-

#

from bwdebug import *
from Spell_Magic import Spell_Magic
import csdefine


class Spell_312639( Spell_Magic ):
	"""
	落马箭
	"""
	def receive( self, caster, receiver ):
		"""
		"""
		Spell_Magic.receive( self, caster, receiver )
		if caster.utype == csdefine.ENTITY_TYPE_ROLE :		# 如果施法者是玩家，受术者只下陆行坐骑 modify by dqh 2012-03-28
			if not bool( receiver.findBuffByBuffID( csdefine.FLYING_BUFF_ID )):
				receiver.retractVehicle( receiver.id )
		else:												# 如果施法者不是玩家,受术者下陆行、飞行坐骑
			receiver.retractVehicle( receiver.id )
