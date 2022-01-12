# -*- coding: gb18030 -*-
#
# $Id: Spell_ItemTeleport.py,v 1.9 2008-08-09 01:53:04 wangshufeng Exp $

"""
传送技能基础
"""

from SpellBase import *
import csstatus
import csdefine
import csconst
from Spell_Item import Spell_Item
from Spell_TeleportBase import Spell_TeleportBase

class Spell_TeleportTong( Spell_Item, Spell_TeleportBase ):
	"""
	帮会传送
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )
		Spell_TeleportBase.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		Spell_TeleportBase.init( self, dict )

	def useableCheck( self, caster, target ) :
		"""
		"""
		state = Spell_TeleportBase.useableCheck( self, caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state
			
		if not caster.isJoinTong():
			return csstatus.SKILL_CANT_HAS_TONG
			
		return Spell_Item.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		receiver.gotoSpace( "fu_ben_bang_hui_ling_di", ( 0,0,0 ),( 0,0,0 ) )

# $Log: not supported by cvs2svn $
#
#