# -*- coding:gb18030 -*-

import csstatus
from Spell_BuffNormal import Spell_BuffNormal
from bwdebug import *

class Spell_BuffSpecific( Spell_BuffNormal ):
	"""
	该技能并不做任何事情，只是对满足血量条件的指定entity施放一个BUFF
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		self._spellClassName = ""	
		self._HP = 0
		
	def init( self, data ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_BuffNormal.init( self, data )
		self._spellClassName = str( data["param1"] )
		self._HP = int( data[ "param2" ] ) if data[ "param2" ]  else 0
		
	def useableCheck( self, caster, target ):
		"""
		"""
		if target.getObject().className != self._spellClassName :
			return csstatus.SKILL_USE_ITEM_WRONG_TARGET	

		if self._HP:
			hpPercent = float( target.getObject().HP )/ float( target.getObject().HP_Max ) * 100.0
			if self._HP < hpPercent:
				return csstatus.SKILL_TARGET_HP_TO0_HIGH
			
		return Spell_BuffNormal.useableCheck( self, caster, target )
		