# -*- coding: gb18030 -*-
#
# $Id: Spell_Item_Key.py
"""
使用物品钥匙开门
"""

from bwdebug import *
from SpellBase import *
from Spell_Item import Spell_Item
import csstatus
import BigWorld
import csconst
import csdefine

class Spell_Item_Key( Spell_Item ):
	"""
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
		self._doorID = dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else ""
		print '---------------------------here self._doorID:', self._doorID
		Spell_Item.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		spaceBase = caster.getCurrentSpaceBase()
		spaceBase.openDoor( { "entityName" : self._doorID } )		# 开启门
		spaceBase.cell.onConditionChange( {} )						# 触发进入下一环节
		
		Spell_Item.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		if caster.getCurrentSpaceType() != csdefine.SPACE_TYPE_FJSG:		# 必须在封剑神宫才可以用
			return csstatus.CIB_MSG_ITEM_NOT_USED_IN_HERE
		return Spell_Item.useableCheck( self, caster, target)
