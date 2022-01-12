# -*- coding: gb18030 -*-



import Language
import items
import InvoiceDataType
from bwdebug import *
import Chapman
from Resource.GoodsLoader import GoodsLoader
import csstatus
import csdefine
import Language
import sys

g_goods = GoodsLoader.instance()
g_items = items.instance()

class Merchant( Chapman.Chapman ):
	"""
	"""

	def __init__( self ):
		"""
		"""
		Chapman.Chapman.__init__( self )
		self.yinpiaoSection = Language.openConfigSection( "config/ItemYinpiaoValue.xml" )
		self.attrInvoices = {}

	def initEntity( self, selfEntity ):
		"""
		virtual method.
		初始化自己的entity的数据
		"""
		Chapman.Chapman.initEntity( self, selfEntity )
		
	def initGoods( self, selfEntity ):
		"""
		初始化每个商人的商品
		"""
		argIndex = 0
		for itemID, amount, invoiceType, itemType, itemAttrs, priceData in g_goods.get( self.className ):
			item = g_items.createDynamicItem( itemID )
			if item is None:
				ERROR_MSG( "%s: no such item." % itemID )
				continue
			item.set( 'reqYinpiao', self.yinpiaoSection[str(itemID)].readInt( 'sell' ) )
			
			proPrefixID = 0
			for attrString, value in itemAttrs.iteritems():
				if attrString == "proPrefix":
					# 如果设置了物品的属性前缀，那么需要根据物品的品质、前缀、属性前缀创建物品的随机属性，但必须保证品质和前缀已经设置了
					# "proPrefix":[属性前缀id, 是否抽取套装属性]
					proPrefixID = value[0]
					isSuitEffect = value[1]
					continue
				item.set( attrString, value )
			if item.isEquip():
				item.fixedCreateRandomEffect( item.getQuality(), None, isSuitEffect )
			proPrefixID = 0
				
			argIndex += 1
			tmpInvData = InvoiceDataType.createInvoiceInstace( invoiceType )
			tmpInvData.setSrcItem( item )
			tmpInvData.setMaxAmount( amount )
			tmpInvData.setAmount( amount )
			tmpInvData.setItemType( itemType )						# 设置商品类型（08.08.09）
			for priceItem in priceData:		# 如果还没设置价格，那么用物品配置中的价格
				if priceItem["priceType"] == csdefine.INVOICE_NEED_MONEY and priceItem["price"] <= 0:
					priceItem["price"] = item.getPrice()
			tmpInvData.initPrice( priceData )
			selfEntity.attrInvoices[argIndex] = tmpInvData
			
	def sellArrayTo( self, selfEntity, playerEntity, argIndices, argAmountList ):
		"""
		商人把东西卖给玩家

		@param 	 selfEntity	  : Merchant自身实例
		@param   playerEntity : 玩家
		@param   argIndices  : 要买的哪个商品
		@type    argIndices  : ARRAY <of> UINT16	</of>
		@param   argAmountList: 要买的数量
		@type    argAmountList: ARRAY <of> UINT16	</of>
		@return: 			无
		"""
		# 取得所要买的商品
		if playerEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟Merchant对话 完成操作
			return
		items = []
		indices = []
		amountList = []
		totalAmount = {}

		for argIndex, argAmount in zip(argIndices, argAmountList):
			try:
				objInvoice = selfEntity.attrInvoices[argIndex]
			except:
				ERROR_MSG( "%s(%i): srcEntityId = %i, no such invoice(index = %i)." % (selfEntity.getName(), selfEntity.id, playerEntity.id, argIndex) )
				return
			# 统计各类物品的购买总数
			if argIndex in totalAmount:
				totalAmount[argIndex] += argAmount
			else:
				totalAmount[argIndex] = argAmount

			srcItem = objInvoice.getSrcItem()
			if srcItem.getStackable() < argAmount:
				# 无论是否可叠加的物品，如果数量大于叠加上限则出错
				ERROR_MSG( "stackable less then sell amount" )
				return
			INFO_MSG("%s try to buy %d '%s'from'%s', %d remain.it's maxAmount is %d." % ( playerEntity.getName(), totalAmount[argIndex], srcItem.name(), selfEntity.getName(), objInvoice.getAmount(), objInvoice.getMaxAmount() ) )
			if objInvoice.getMaxAmount() > 0:	# 商品有数量限制
				if objInvoice.getAmount() <= 0:
					playerEntity.client.onStatusMessage( csstatus.ITEM_ALL_SALE, str(( srcItem.name(), )) )
					selfEntity.sellToCB( argIndex, 0, playerEntity.id )	# 添加这句是为了通知客户端商品已被别人买光
					ERROR_MSG( "%s(%i): %s(%i) buy %i '%s', %i only." % ( selfEntity.getName(), selfEntity.id, playerEntity.playerName, playerEntity.id, srcItem.id, argAmount, objInvoice.getAmount() ) )
					return	# 没货，不卖
				elif totalAmount[argIndex] > objInvoice.getAmount():
					playerEntity.client.onStatusMessage( csstatus.ITEM_NO_ENOUGH, str(( srcItem.name(), )) )
					ERROR_MSG( "%s(%i): %s(%i) buy %i '%s', %i only." % ( selfEntity.getName(), selfEntity.id, playerEntity.playerName, playerEntity.id, srcItem.id, argAmount, objInvoice.getAmount() ) )
					return	# 没这么多货，不卖

			itemData = srcItem.new()
			itemData.setAmount( argAmount )
			items.append( itemData )
			indices.append( argIndex )
			amountList.append( argAmount )
		if len( items ) > 0:
			self.onSellItems( selfEntity, playerEntity, items, indices, amountList )

	def onSellItems( self, selfEntity, playerEntity, items, argIndices, argAmountList ):
		"""
		销售某类物品事件
		"""
		playerEntity.buyItemFromMerchant( selfEntity, items, argIndices, argAmountList )

	def buyFrom( self, selfEntity, playerEntity, argUid, argAmount ):
		"""
		商人从玩家身上收购东西

		@param 	 selfEntity	  : Merchant自身实例
		@param   playerEntity : 玩家
		@param   argUid: 要买的哪个商品
		@type    argUid: INT64
		@param   argAmount: 要买的数量
		@type    argAmount: UINT16
		@return: 			无
		"""
		# 卖大量跟卖一（个）组不应该用一样接口，但目前不想大改，先这样做 -pj
		playerEntity.sellItemToMerchant( selfEntity, [argUid], [argAmount] )

	def buyArrayFrom( self, selfEntity, playerEntity, argUidList, argAmountList ):
		"""
		商人从玩家身上收购大量东西；
		参数列表里的每一个元素对应一个物品所在背包、标识和数量。
		收购规则：所有物品都存在且可以卖以及卖出总价值与玩家身上金钱总和不会超过玩家允许携带的金钱总数时，允许出售，否则不允许出售。

		@param 	 selfEntity	  : Merchant自身实例
		@param   playerEntity : 玩家
		@param  argUidList: 要买的哪个商品
		@type   argUidList: ARRAY OF INT64
		@param  argAmountList: 要买的数量
		@type   argAmountList: ARRAY OF UINT16
		@return:               无
		"""
		if playerEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟Merchant对话 完成操作
			return
		playerEntity.sellItemToMerchant( selfEntity, argUidList, argAmountList )

# Chapman.py
