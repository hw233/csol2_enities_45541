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
	元宝票变成银元宝
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
		value = item.query('silverYuanbao', 0 )
		caster.base.remoteCall( "addSilver", ( value, csdefine.CHANGE_SILVER_ITEMTOSILVER  ) )
		INFO_MSG( "--->>>玩家( %s )把元宝票( 数额:%i )兑换成银元宝。" % ( self.getName(), value ) )

