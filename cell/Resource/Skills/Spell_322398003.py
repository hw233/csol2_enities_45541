# -*- coding: gb18030 -*-
"""
ʹ�ñ����ʱ��,����һ����Ʒ�ļ���
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

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		drop = random.random()

		tmpList = []
		notifyStr = ""
		gameYield = receiver.wallow_getLucreRate()
		if gameYield > 0.0:			# ����������ʱ�� ���ٵ���
			item = self.getTreasureBoxDropItems( caster )
			if item.id == 60101001: # �����Ʒ�ǽ�Ǯ
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
		��ñ���������Ʒ
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
		if dropRate > gameYield:	# ���ڷ����ԣ����Ϊ 0.0�ļ��ʣ���ô�ز��������Ϊ0.5�ģ���ô0 ~ 0.5 ������ ���Ϊ 1.0 ��ô�ص���
			return None
		return g_itemTreasureBoxMoneyItemDrop.getDropItem( boxLevel )