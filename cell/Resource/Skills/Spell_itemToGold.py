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
	元宝票变成金元宝
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )

	def useableCheck( self, caster, target ) :
		return Spell_Item.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		value = item.query('goldYuanbao', 0 )
		caster.base.bank_item2Gold( value )
		INFO_MSG( "--->>>玩家( %s )把元宝票( 数额:%i )兑换成元宝。" % ( self.getName(), value ) )

# $Log: not supported by cvs2svn $
# Revision 1.1  2008/02/26 06:17:53  kebiao
# no message
#
#