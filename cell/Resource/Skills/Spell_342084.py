# -*- coding:gb18030 -*-

from Spell_Item import Spell_Item
from bwdebug import *
import csdefine
import csconst
import csstatus

class Spell_342084( Spell_Item ):
	"""
	���˾������鵤�Ĺ�ʽ
	���뽱������ֵ=1404*��25+5*��ɫ�ȼ�^1.2��
	"""
	def init( self, dict ):
		"""
		"""
		Spell_Item.init( self, dict )
		self.param1 = float( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 )
		
	def useableCheck( self, caster, target ):
		"""
		"""
		try:
			exp = target.getObject().EXP
		except:
			ERROR_MSG( "caster( %s ) spell invalid target." % caster.getName() )
			return
		return Spell_Item.useableCheck( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		playerLevel = receiver.level
		value = int ( ( 175 * playerLevel ** 1.5 + 460 ) * self.param1 )
		receiver.addExp( value, csdefine.CHANGE_EXP_USE_ROLE_COMPETITION_ITEM )
