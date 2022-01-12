# -*- coding: gb18030 -*-

# 系统技能，生成一个AreaRestrictTransducer的entity(陷阱功能entity)，在施放者位置

import BigWorld
import csdefine
import csstatus
from SpellBase import *

from Spell_Rabbit_Run import Spell_Rabbit_Run

ITEM_IDs = [50101141]
import random
import items
g_items = items.instance()

class Spell_RabbitRun_Add_Item( Spell_Rabbit_Run ):
	"""
	系统技能
	生成一个AreaRestrictTransducer的entity(陷阱功能entity)
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Rabbit_Run.__init__( self )
		self.param1 = 0		#物品ID


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Rabbit_Run.init( self, dict )
		self.param1 = int( dict["param1"] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		技能实现的目的
		"""
		item = g_items.createDynamicItem( self.param1 , 1 )
		receiver.addItem( item, csdefine.ADD_ITEM_RABBIT_RUN )
		Spell_Rabbit_Run.receive( self, caster, receiver )