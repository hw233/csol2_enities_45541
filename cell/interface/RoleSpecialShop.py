# -*- coding: gb18030 -*-
#
# $Id: RoleSpecialShop.py,v 1.1 2008-08-15 09:13:08 wangshufeng Exp $


import BigWorld
import time
from bwdebug import *
import csdefine
import csconst
import csstatus
import items
import ItemTypeEnum
import sys

g_items = items.instance()


class RoleSpecialShop:
	"""
	道具商城
	"""
	def __init__( self ):
		"""
		"""
		pass

	def spe_receiveSpecialGoods( self, itemID, amount, totalPrice, moneyType ):
		"""
		Define method.
		接收商城道具，判断是否符合买入条件，符合条件则加入物品，通知base扣除元宝；否则买卖失败。

		处理完毕后把结果通知商城管理器

		@param itemID : 物品id
		@type itemID : ITEM_ID
		@param amount : 欲购买的数量
		@type amount : INT32
		@param moneyType : 元宝类型
		@type moneyType : INT8
		"""
		if self.iskitbagsLocked():	# 背包上锁，by姜毅
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return
		needSpaces  = 0 # 需要包裹空间
		item = g_items.createDynamicItem( itemID )
		if moneyType == csdefine.SPECIALSHOP_MONEY_TYPE_SILVER:
			item.setBindType( ItemTypeEnum.CBT_PICKUP )
			
		itemStackable = item.getStackable()
		itemPiece = amount / itemStackable
		restAmount = amount % itemStackable
		itemList = []
		for piece in xrange( itemPiece ):
			tempItem = item.new()
			tempItem.setAmount( itemStackable )
			itemList.append( tempItem )
		if restAmount > 0:
			item.setAmount( restAmount )
			itemList.append( item )
			
		state = True
		kitbagState = self.checkItemsPlaceIntoNK_( itemList )
		if kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			self.statusMessage( csstatus.CIB_MSG_BAG_HAS_FULL )
			state = False
		elif kitbagState == csdefine.KITBAG_ITEM_COUNT_LIMIT:
			self.statusMessage( csstatus.NPC_TRADE_ITEM_LIMIT_COUNT )
			state = False
		else:
			price = totalPrice / amount
			for tempItem in itemList:
				self.addItemAndRadio( tempItem, ItemTypeEnum.ITEM_GET_SHOP, reason = csdefine.ADD_ITEM_RECEIVESPECIALGOODS )
	
			INFO_MSG( "player( %s ) buys item( %s ),itemAmount( %i ),totalPrice( %i ), moneyType( %i )." % ( self.getName(), item.name, amount, totalPrice, moneyType ) )
			
		self.base.spe_buyItemCB( itemID, amount, totalPrice, moneyType, state )

#
# $Log: not supported by cvs2svn $
#
