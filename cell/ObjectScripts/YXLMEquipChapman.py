# -*- coding: gb18030 -*-
"""
英雄联盟版失落宝藏副本的装备交易NPC
"""

import csdefine
from Chapman import Chapman

class YXLMEquipChapman( Chapman ):
	"""
	这种商人是一种特殊的商人
	这种商人出售的物品，不是用钱买，而是用灵魂币（其实就是运气值）来换取的
	"""
	def __init__( self ):
		"""
		"""
		Chapman.__init__( self )

	def onSellItem( self, selfEntity, playerEntity, newInvoice, argIndex, argAmount ):
		"""
		销售某物品事件
		"""
		playerEntity.buyYXLMEquipFromNPC( selfEntity, newInvoice, argIndex, argAmount )

	def onSellItems( self, selfEntity, playerEntity, invoiceItems, argIndices, argAmountList ):
		"""
		销售某类物品事件
		"""
		for invoice, argIndex, argAmount in zip( invoiceItems, argIndices, argAmountList ) :
			playerEntity.buyYXLMEquipFromNPC( selfEntity, invoice, argIndex, argAmount )

	def buyFrom( self, selfEntity, playerEntity, argUid, argAmount ):
		"""
		商人从玩家身上收购东西

		@param 	 selfEntity	  	: NPC自身实例
		@param   playerEntity	: 玩家
		@param   argUid			: 要买的哪个商品
		@type    argUid			: INT64
		@param   argAmount		: 要买的数量
		@type    argAmount		: UINT16
		@return					: 无
		"""
		if playerEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
			return
		playerEntity.sellYXLMEquipToNPC( selfEntity, argUid, argAmount )

	def buyArrayFrom( self, selfEntity, playerEntity, argUidList, argAmountList ):
		"""
		Exposed method
		商人从玩家身上收购大量东西；
		参数列表里的每一个元素对应一个物品所在背包、标识和数量。
		收购规则：所有物品都存在且可以卖以及卖出总价值与玩家身上金钱总和不会超过玩家允许携带的金钱总数时，允许出售，否则不允许出售。

		@param 	 selfEntity	  : NPC自身实例
		@param   playerEntity : 玩家
		@param  argUidList: 要买的哪个商品
		@type   argUidList: ARRAY OF UINT64
		@param  argAmountList: 要买的数量
		@type   argAmountList: ARRAY OF UINT16
		@return:               无
		"""
		if playerEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
			return
		for argUid, argAmount in zip( argUidList, argAmountList ):
			playerEntity.sellYXLMEquipToNPC( selfEntity, argUid, argAmount )
