# -*- coding: gb18030 -*-
#

"""
"""

from SpellBase import *
import csstatus
import csdefine
import Const
from bwdebug import *
from Spell_Item import Spell_Item

class Spell_itemToSilver( Spell_Item ):
	"""
	Ԫ��Ʊ�����Ԫ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )

	def useableCheck( self, caster, target ) :
		return Spell_Item.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		value = item.query('silverYuanbao', 0 )
		caster.base.remoteCall( "addSilver", ( value, csdefine.CHANGE_SILVER_ITEMTOSILVER  ) )
		INFO_MSG( "--->>>���( %s )��Ԫ��Ʊ( ����:%i )�һ�����Ԫ����" % ( self.getName(), value ) )

