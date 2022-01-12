# -*- coding:gb18030 -*-

from bwdebug import *
from Spell_Magic import Spell_Magic

class Spell_322481( Spell_Magic ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Spell_Magic.__init__( self )
		self.hpPercent = 0
		self.mpPercent = 0
		
	def init( self, data ):
		"""
		"""
		Spell_Magic.init( self, data )
		self.hpPercent = float( data["param1"] if len( data["param1"] ) > 0 else 0 ) / 100.0
		self.mpPercent = float( data["param2"] if len( data["param2"] ) > 0 else 0 ) / 100.0
		
	def receive( self, caster, receiver ):
		"""
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		receiver.reviveOnOrigin( self.hpPercent, self.mpPercent )
		changeHP = receiver.HP_Max * self.hpPercent
		caster.doCasterOnCure( receiver, changeHP )	#治疗目标时触发
		receiver.doReceiverOnCure( caster, changeHP )   #被治疗时触发
		