# -*- coding:gb18030 -*-

from Spell_Item import Spell_Item
from bwdebug import *
import csdefine
import csconst
import csstatus

class Spell_342022( Spell_Item ):
	"""
	Ǳ�ܵ��Ĺ�ʽ
	(a*5*30+a*5*4+a*20+20)*b
	����a�ǵȼ�
	b��ϵ��������СǱ�ܵ���ϵ��������3����Ǳ�ܵ���ϵ��������5
	"""
	def init( self, dict ):
		"""
		"""
		Spell_Item.init( self, dict )
		self.param1 = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 )
		
	def useableCheck( self, caster, target ):
		"""
		"""
		try:
			potential = target.getObject().potential
		except:
			ERROR_MSG( "caster( %s ) spell invalid target." % caster.getName() )
			return
		if potential >= csconst.ROLE_POTENTIAL_UPPER:
			return csstatus.SKILL_ITEM_CANT_GAIN_POTENTIAL
		return Spell_Item.useableCheck( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		itemLevel = item.getLevel()
		value = ( itemLevel ** 1.2 * 5 * 30 + itemLevel ** 1.2 * 5 * 4 + itemLevel ** 1.2 * 400 ) * self.param1
		receiver.addPotential( value, csdefine.CHANGE_POTENTIAL_USE_ITEM )
