# -*- coding: gb18030 -*-
#

"""
"""

from SpellBase import *
import csstatus
import Const
from bwdebug import *
from Spell_Item import Spell_Item

class Spell_itemToGold( Spell_Item ):
	"""
	Ԫ��Ʊ��ɽ�Ԫ��
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
		value = item.query('goldYuanbao', 0 )
		caster.base.bank_item2Gold( value )
		INFO_MSG( "--->>>���( %s )��Ԫ��Ʊ( ����:%i )�һ���Ԫ����" % ( self.getName(), value ) )

# $Log: not supported by cvs2svn $
# Revision 1.1  2008/02/26 06:17:53  kebiao
# no message
#
#