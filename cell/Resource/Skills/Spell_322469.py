# -*- coding:gb18030 -*-

from bwdebug import *
from Spell_BuffNormal import Spell_BuffNormal
import csstatus

class Spell_322469( Spell_BuffNormal ):
	"""
	嗜血狂怒 血量低于20%时不可使用
	"""
	def __init__( self ):
		Spell_BuffNormal.__init__( self )
		self.param1 = 0			# 可以使用此技能的生命值比例条件
		
	def init( self, data ):
		"""
		"""
		Spell_BuffNormal.init( self, data )
		self.param1 = float( data["param1"] if len( data["param1"] ) > 0 else 0 ) / 100.0
		
	def useableCheck( self, caster, target ):
		"""
		"""
		if float( caster.HP ) / caster.HP_Max < self.param1:
			return csstatus.SKILL_HP_CANT_USE
		return Spell_BuffNormal.useableCheck( self, caster, target )
		
	