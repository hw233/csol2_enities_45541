# -*- coding: gb18030 -*-

# 系统技能，生成一个AreaRestrictTransducer的entity(陷阱功能entity)，在施放者位置

import BigWorld
import csdefine
import csstatus
from SpellBase import *

from Spell_BuffNormal import Spell_BuffNormal

import random
import items
g_items = items.instance()

class Spell_Add_Item( Spell_BuffNormal ):
	"""
	给受术者增加一个物品1,根据一定数量的物品1换取一个物品2
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_BuffNormal.__init__( self )
		self.param1 = 0		#物品1 ID
		self.param2 = 1		#物品1 数量
		self.param3 = 0		#物品2 ID


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_BuffNormal.init( self, dict )
		self.param1 = int( dict["param1"] )
		self.param2 = int( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0 )
		self.param3 = int( dict["param3"] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		技能实现的目的
		"""
		item = g_items.createDynamicItem( self.param1 )
		if item == None:
			Spell_BuffNormal.receive( self, caster, receiver )
			return
		receiver.addItem( item, csdefine.ADD_ITEM_REQUESTADDITEM )
		receiver.queryItemFromBagAndAddItem( self.param1, self.param2, self.param3 )
		Spell_BuffNormal.receive( self, caster, receiver )
		