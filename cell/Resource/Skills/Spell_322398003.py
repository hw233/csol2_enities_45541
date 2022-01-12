# -*- coding: gb18030 -*-
"""
使用宝箱的时候,爆出一地物品的技能
"""
import random
import csstatus
import csdefine
from Function import switchMoney
from bwdebug import *

from Love3 import g_itemsDict as g_items
from Spell_Item import Spell_Item
from items.ItemDropLoader import ItemDropTreasureBoxLoader

g_itemTreasureBoxMoneyItemDrop = ItemDropTreasureBoxLoader.instance()

class Spell_322398003( Spell_Item ):
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
		Spell_Item.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		drop = random.random()

		tmpList = []
		notifyStr = ""
		gameYield = receiver.wallow_getLucreRate()
		if gameYield > 0.0:			# 超过防沉迷时间 不再掉落
			item = self.getTreasureBoxDropItems( caster )
			if item.id == 60101001: # 如果物品是金钱
				moneyAmount =  int( item.getAmount() * gameYield )
				caster.gainMoney( moneyAmount, csdefine.CHANGE_MONEY_OPEN_TREASURE_BOX )
				notifyStr = switchMoney( moneyAmount )
			else:
				caster.addItemAndNotify_( item, csdefine.ADD_ITEM_TREASURE_BOX )
				notifyStr = item.name()
			caster.statusMessage( csstatus.SKILL_TREASURE_BOX_OPENED, notifyStr )
		Spell_Item.receive( self, caster, receiver )


	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return csstatus.CIB_MSG_BAG_HAS_FULL
		kitbagState = caster.checkItemsPlaceIntoNK_( [ item ] )
		if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			return csstatus.CIB_MSG_BAG_HAS_FULL
		return Spell_Item.useableCheck( self, caster, target)

	def getTreasureBoxDropItems( self, player ):
		"""
		获得宝箱掉落的物品
		@return :array of tuple, tuple like as  [(itemKeyName, {...}, owners) ,...]
		"""
		uid = player.queryTemp( "item_using" )
		item = player.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return None
		boxLevel = item.getLevel()
		gameYield = player.wallow_getLucreRate()
		dropRate = random.random()
		if dropRate > gameYield:	# 关于防沉迷，如果为 0.0的几率，那么必不掉，如果为0.5的，那么0 ~ 0.5 不掉， 如果为 1.0 那么必掉。
			return None
		return g_itemTreasureBoxMoneyItemDrop.getDropItem( boxLevel )