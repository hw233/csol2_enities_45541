# -*- coding:gb18030 -*-

import csstatus
from Spell_BuffNormal import Spell_BuffNormal
from bwdebug import *

class Spell_BuffSpecific( Spell_BuffNormal ):
	"""
	�ü��ܲ������κ����飬ֻ�Ƕ�����Ѫ��������ָ��entityʩ��һ��BUFF
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		self._spellClassName = ""	
		self._HP = 0
		
	def init( self, data ):
		"""
		��ȡ��������
		@param dict: ��������
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
		