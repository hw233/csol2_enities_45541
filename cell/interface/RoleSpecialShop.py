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
	�����̳�
	"""
	def __init__( self ):
		"""
		"""
		pass

	def spe_receiveSpecialGoods( self, itemID, amount, totalPrice, moneyType ):
		"""
		Define method.
		�����̳ǵ��ߣ��ж��Ƿ�����������������������������Ʒ��֪ͨbase�۳�Ԫ������������ʧ�ܡ�

		������Ϻ�ѽ��֪ͨ�̳ǹ�����

		@param itemID : ��Ʒid
		@type itemID : ITEM_ID
		@param amount : �����������
		@type amount : INT32
		@param moneyType : Ԫ������
		@type moneyType : INT8
		"""
		if self.iskitbagsLocked():	# ����������by����
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return
		needSpaces  = 0 # ��Ҫ�����ռ�
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
