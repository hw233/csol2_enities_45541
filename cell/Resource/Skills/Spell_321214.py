# -*- coding:gb18030 -*-

from bwdebug import *
from Spell_BuffNormal import Spell_BuffNormal
import csstatus

class Spell_321214( Spell_BuffNormal ):
	"""
	疯魔乱舞
	
	当战士生命在30%以下时，伤痛会让他进入绝对疯狂状态。对目标造成巨大物理伤害。
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
		if float( caster.HP ) / caster.HP_Max >= self.param1:
			return csstatus.SKILL_HP_CANT_USE
		return Spell_BuffNormal.useableCheck( self, caster, target )
		
		