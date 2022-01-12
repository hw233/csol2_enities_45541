# -*- coding: gb18030 -*-
#
# 2008-12-26 SongPeifang
#
from Chapman import Chapman
import csdefine

class DarkTrader( Chapman ):
	"""
	"""

	def __init__( self ):
		"""
		"""
		Chapman.__init__( self )

	def buyFrom( self, selfEntity, playerEntity, argUid, argAmount ):
		"""
		投机商人从玩家身上收购东西

		@param 	 selfEntity	  : Merchant自身实例
		@param   playerEntity : 玩家
		@param   argUid: 要买的哪个商品
		@type    argUid: INT64
		@param   argAmount: 要买的数量
		@type    argAmount: INT64
		@return: 			无
		"""
		playerEntity.sellToDarkTrader( selfEntity, argUid, argAmount )

	def buyArrayFrom( self, selfEntity, playerEntity, argUidList, argAmountList ):
		"""
		投机商人从玩家身上收购大量东西；
		参数列表里的每一个元素对应一个物品所在背包、标识和数量。
		收购规则：所有物品都存在且可以卖以及卖出总价值与玩家身上金钱总和不会超过玩家允许携带的金钱总数时，允许出售，否则不允许出售。

		@param 	 selfEntity	  : Merchant自身实例
		@param   playerEntity : 玩家
		@param  argUidList: 要买的哪个商品
		@type   argUidList: ARRAY OF INT64
		@param  argAmountList: 要买的数量
		@type   argAmountList: ARRAY OF INT64
		@return:               无
		"""
		if playerEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟Merchant对话 完成操作
			return
		playerEntity.sellArrayToDarkTrader( selfEntity, argUidList, argAmountList )

	def onSellItem( self, selfEntity, playerEntity, newInvoice, argIndex, argAmount ):
		"""
		销售某物品事件
		"""
		itemData = newInvoice.getSrcItem()
		playerEntity.buyFromDarkTrader( selfEntity, itemData, argIndex, argAmount )

	def onSellItems( self, selfEntity, playerEntity, invoiceItems, argIndices, argAmountList ):
		"""
		销售某类物品事件
		"""
		zipInvoiceArray = zip( invoiceItems, argAmountList )
		items = []
		for invoiceItem, amount in zipInvoiceArray:
			item = invoiceItem.getSrcItem()
			item.setAmount( amount )
			items.append( item )
		playerEntity.buyArrayFromDarkTrader( selfEntity, items, argIndices, argAmountList )