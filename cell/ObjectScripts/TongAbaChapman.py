# -*- coding: gb18030 -*-

"""
商人全局实例基础类
"""

import Language
import cschannel_msgs
import ShareTexts as ST
import items
import InvoiceDataType
from bwdebug import *
import Chapman
from Resource.GoodsLoader import GoodsLoader

g_goods = GoodsLoader.instance()
g_items = items.instance()

class TongAbaChapman( Chapman.Chapman ):
	"""
	商人全局实例基础类 for cell。

	@ivar      attrInvoices: 货物列表
	@type      attrInvoices: dict
	"""

	def __init__( self ):
		"""
		"""
		Chapman.Chapman.__init__( self )

	def onSellItem( self, selfEntity, playerEntity, newInvoice, argIndex, argAmount ):
		"""
		销售某物品事件
		"""
		itemData = newInvoice.getSrcItem()
		playerEntity.tongAbaBuyFromNPC( selfEntity, itemData, argIndex, argAmount )

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
		playerEntity.tongAbaBuyArrayFromNPC( selfEntity, items, argIndices, argAmountList )

	def buyFrom( self, selfEntity, playerEntity, argUid, argAmount ):
		"""
		商人从玩家身上收购东西

		@param 	 selfEntity	  : NPC自身实例
		@param   playerEntity : 玩家
		@param   argUid: 要卖的哪个商品
		@type    argUid: INT64
		@param   argAmount: 要买的数量
		@type    argAmount: UINT16
		@return: 			无
		"""
		playerEntity.sellTongAbaItemToNPC( selfEntity, argUid, argAmount )

	def buyArrayFrom( self, selfEntity, playerEntity, argUidList, argAmountList ):
		"""
		商人从玩家身上收购大量东西；
		参数列表里的每一个元素对应一个物品所在背包、标识和数量。
		收购规则：所有物品都存在且可以卖以及卖出总价值与玩家身上金钱总和不会超过玩家允许携带的金钱总数时，允许出售，否则不允许出售。

		@param 	 selfEntity	  : NPC自身实例
		@param   playerEntity : 玩家
		@param  argUidList: 要买的哪个商品
		@type   argUidList: ARRAY OF INT64
		@param  argAmountList: 要买的数量
		@type   argAmountList: ARRAY OF UINT16
		@return:               无
		"""
		playerEntity.sellTongAbaItemArrayToNPC( selfEntity, argUidList, argAmountList )

	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		与玩家对话；未声明(不能声明)的方法，因此重载此方法的上层如果需要访问自己的私有属性请自己判断self.isReal()。

		@param   selfEntity: 与自己对应的Entity实例，传这个参数是为了方便以后的扩充
		@type    selfEntity: Entity
		@param playerEntity: 说话的玩家
		@type  playerEntity: Entity
		@param       dlgKey: 对话关键字
		@type        dlgKey: str
		@return: 无
		"""
		if dlgKey == "Talk":
			if selfEntity.isReal():
				self.checkPlayerIsRight( selfEntity, playerEntity, playerEntity.queryTemp( "aba_right", False )  )
			else:
				selfEntity.remoteScriptCall( "checkPlayerIsRight", ( playerEntity.base, playerEntity.queryTemp( "aba_right", False ) ) )
		elif dlgKey == "NO":
			playerEntity.setGossipText(cschannel_msgs.NIU_MO_WANG_VOICE_9)
			playerEntity.sendGossipComplete( selfEntity.id )
		elif dlgKey == "OK":
			Chapman.Chapman.gossipWith( self, selfEntity, playerEntity, "Talk" )
		else:
			Chapman.Chapman.gossipWith( self, selfEntity, playerEntity, dlgKey )

	def checkPlayerIsRight( self, selfEntity, playerEntity, isRight ):
		"""
		检查玩家是否是防守方 然后做对应的操作
		"""
		if selfEntity.queryTemp( "isRight", False ) == isRight:
			selfEntity.gossipWith( playerEntity.id, "OK" )
		else:
			selfEntity.gossipWith( playerEntity.id, "NO" )
#