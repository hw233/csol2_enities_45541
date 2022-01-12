# -*- coding: gb18030 -*-
#


"""
"""

import BigWorld
import csdefine
import csconst
import csstatus
from bwdebug import *
import ItemTypeEnum
import items


g_item = items.instance()

YINPIAO = 50101024													#银票
DARK_MERCHANT_RATE = 0.25											#黑市商人回收物品价格比例

class RoleTradeWithMerchant:
	"""
	与商人交易
	"""
	def __init__( self ):
		pass

	def sellItemToMerchant( self, merchantEntity, argUidList, argAmountList ):
		"""
		define method
		玩家卖物品
		"""
		yinpiao = 0
		invoiceList = zip( argUidList, argAmountList )
		items = []		# 记录每一个物品
		yinpiaoList = []	# 记录每一个物品的卖出银票价格

		for argUid, argAmount in invoiceList:
			currItem = self.getItemByUid_( argUid )
			if currItem is None:
				ERROR_MSG( "%s(%i): no such item(argUid = %i)" % (self.playerName, self.id, argUid) )
				self.clientEntity(merchantEntity.id).onBuyArrayFromCB( 0 )	# 出售失败
				return
			#if not currItem.canSell():	# 不能卖的不可以出售
			#	ERROR_MSG( "%s(%i): item(name = %s) can't sell." % (self.playerName, self.id, currItem.name) )
			#	self.clientEntity(merchantEntity.id).onBuyArrayFromCB( 0 )	# 出售失败
			#	return
			if currItem.isFrozen():
				self.clientEntity(merchantEntity.id).onBuyArrayFromCB( 0 )	# 出售失败
				return
			if not str(currItem.id) in merchantEntity.getScript().yinpiaoSection.keys():
				# "商人不收购这个物品。"
				self.statusMessage( csstatus.MERCHANT_NO_BUY_THIS_ITEM )
				return
			if self.findItemsByIDFromNKCK( YINPIAO ) == [] :
				#跑商状态判断
				self.statusMessage( csstatus.ROLE_NOT_IN_RUN_MERCHANT )
				return
			if not self.isInMerchantQuest():
				#跑商状态判断
				self.statusMessage( csstatus.ROLE_NOT_IN_RUN_MERCHANT )
				return
			if currItem.getAmount() < argAmount:		# 骗人，玩家身上根本没这么多
				ERROR_MSG( "%s(%i): not more item(name = %s), current amount = %i, sell amount = %i." % (self.playerName, self.id, currItem.name, currItem.getAmount(), argAmount) )
				self.clientEntity(merchantEntity.id).onBuyArrayFromCB( 0 )	# 出售失败
				return
			#moneys += int( currItem.getPrice() * merchantEntity.invBuyPercent ) * argAmount
			#currMoney = priceCarry( currItem.getPrice() * merchantEntity.invBuyPercent ) * argAmount

			spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
			areaYinpiao = merchantEntity.getScript().yinpiaoSection[str(currItem.id)].readInt( spaceLabel )
			sellYinpiao = merchantEntity.getScript().yinpiaoSection[str(currItem.id)].readInt( 'sell' )

			changeValue = False
			#判断是否是高价地区出售
			if BigWorld.globalData['MerchantHighArea'] == spaceLabel:
				if BigWorld.globalData['MerchantHighItem'] == currItem.id:
					yinpiao += ( areaYinpiao - sellYinpiao ) * BigWorld.globalData['MerchantHighPercent'] + areaYinpiao * argAmount
					changeValue = True


			#判断是否是低价地区出售
			if BigWorld.globalData['MerchantLowArea'] == spaceLabel:
				if BigWorld.globalData['MerchantLowItem'] == currItem.id:
					yinpiao += ( ( areaYinpiao - sellYinpiao ) * BigWorld.globalData['MerchantLowPercent'] + areaYinpiao ) * argAmount
					changeValue = True

			if not changeValue:
				yinpiao += areaYinpiao * argAmount

			yinpiaoList.append( yinpiao )
			items.append( currItem )

		for argAmount, argUid in zip( argAmountList, argUidList ):
			self.removeItemByUid_( argUid, argAmount, csdefine.DELETE_ITEM_SELLTONPC )

		# 给钱玩家
		self.gainYinpiao( int(yinpiao) )
		self.clientEntity(merchantEntity.id).onBuyArrayFromCB( 1 )	# 出售成功


	def buyItemFromMerchant( self, merchantEntity, itemArray, argIndices, argAmountList ):
		"""
		玩家买物品

		@param merchantEntity: 商人NPC entity or mailbox
		@type  merchantEntity: MAILBOX
		@param  itemArray: 要买的物品实例数组
		@type   itemArray: ARRAY OF ITEM
		@param argIndices: 要买的哪个商品
		@type  argIndices: ARRAY OF UINT16
		@param argAmountList: 要买的数量
		@type  argAmountList: ARRAY OF UINT16
		@param	playerEntityID:	新添加的变量，用于通知客户端商品数量改变
		@type	playerEntityID:	OBJECT_ID
		@return:              无
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		merchantEntity = BigWorld.entities[ merchantEntity.id ]
		yinpiao = 0
		for itemInstance in itemArray:
			# 确保是int类型的
			yinpiao += itemInstance.reqYinpiao() * itemInstance.amount

		if yinpiao > self.getAllYinpiaoValue():
			ERROR_MSG( "%s(%i): no enough yinpiao." % (self.playerName, self.id) )
			self.statusMessage( csstatus.NPC_TRADE_NOT_ENOUGH_YINPIAO )
			return
		if not self.isInMerchantQuest():		#跑商状态判断
			self.statusMessage( csstatus.ROLE_NOT_IN_RUN_MERCHANT )
			return

		kitbagState = self.checkItemsPlaceIntoNK_( itemArray )

		if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			self.statusMessage( csstatus.NPC_TRADE_SPACE_NOT_ENOUGH )
			return
		if kitbagState == csdefine.KITBAG_ITEM_COUNT_LIMIT:
			self.statusMessage( csstatus.NPC_TRADE_ITEM_LIMIT_COUNT )
			return

		for itemInstance in itemArray:
			self.addItemAndNotify_( itemInstance, csdefine.ADD_ITEM_BUYITEMFROMMERCHANT )

		# 玩家给钱
		self.payYinpiao( yinpiao )

		# 到了这一步，不管购买成功失败，都当作成功
		for argIndex, argAmount in zip( argIndices, argAmountList ):
			merchantEntity.sellToCB( argIndex, argAmount, self.id )


	def getAllYinpiaoValue( self ):
		"""
		获取身上所有银票的数值
		"""
		itemList = self.findItemsByIDFromNKCK( YINPIAO )			# 银票ID
		if len( itemList ) <= 0 :
			return -1									# 身上没有银票时返回 -1
		yinpiao = 0
		for i in itemList:
			yinpiao += i.yinpiao()
		return yinpiao

	def payYinpiao( self, amount ):
		"""
		交付银票
		"""
		itemList = self.findItemsByIDFromNKCK( YINPIAO )			#银票ID
		for i in itemList:
			if amount > i.yinpiao():
				amount -= i.yinpiao()
				self.removeItemByUid_( i.uid, 1, csdefine.DELETE_ITEM_PAYYINPIAO )
			else:
				i.set( 'yinpiao', i.yinpiao() - amount, self )
				self.questYinpiaoValueChange( i )
		self.statusMessage( csstatus.MERCHANT_YINPIAO_SUB, amount, self.getAllYinpiaoValue() )

	def gainYinpiao( self, amount ):
		"""
		获得银票
		"""
		itemList = self.findItemsByIDFromNKCK( YINPIAO )
		itemList[0].set( 'yinpiao', ( itemList[0].yinpiao() + amount ), self )
		self.statusMessage( csstatus.MERCHANT_YINPIAO_ADD, amount, self.getAllYinpiaoValue() )
		self.questYinpiaoValueChange( itemList[0] )

	def sellItemToDarkMerchant( self, merchantEntity, argUidList, argAmountList ):
		"""
		玩家卖物品给黑市商人
		"""
		yinpiao = 0
		invoiceList = zip( argUidList, argAmountList )
		items = []		# 记录每一个物品
		moneyList = []	# 记录每一个物品的卖出银票价格

		#if self.findItemsByIDFromNKCK( YINPIAO ) == [] :
		#	return


		for argUid, argAmount in invoiceList:
			currItem = self.getItemByUid_( argUid )
			if currItem is None:
				ERROR_MSG( "%s(%i): no such item(argUid = %i)" % (self.playerName, self.id, argUid) )
				self.clientEntity(merchantEntity.id).onBuyArrayFromCB( 0 )	# 出售失败
				return
			if currItem.getAmount() < argAmount:		# 骗人，玩家身上根本没这么多
				ERROR_MSG( "%s(%i): not more item(name = %s), current amount = %i, sell amount = %i." % (self.playerName, self.id, currItem.name, currItem.getAmount(), argAmount) )
				self.clientEntity(merchantEntity.id).onBuyArrayFromCB( 0 )	# 出售失败
				return
			#moneys += int( currItem.getPrice() * merchantEntity.invBuyPercent ) * argAmount
			#currMoney = priceCarry( currItem.getPrice() * merchantEntity.invBuyPercent ) * argAmount
			#spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
			#areaYinpiao = merchantEntity.getScript().yinpiaoSection[str(currItem.id)].readInt( spaceLabel )
			sellYinpiao = 0
			try:
				sellYinpiao = merchantEntity.getScript().yinpiaoSection[str(currItem.id)].readInt( 'DarkMerchant' )
			except AttributeError, err:
				self.statusMessage( csstatus.NOT_RUN_MERCHANT_ITEM )
				ERROR_MSG( err )
				return
			if sellYinpiao == 0:
				ERROR_MSG( "Please check whether the config of item %s is wrong!" % currItem.name )
				return
			#changeValue = False
			##判断是否是高价地区出售
			#if BigWorld.globalData['MerchantHighArea'] == spaceLabel:
			#	if BigWorld.globalData['MerchantHighItem'] == currItem.id:
			#		yinpiao += ( areaYinpiao - sellYinpiao ) * BigWorld.globalData['MerchantHighPercent'] + sellYinpiao * argAmount
			#		changeValue = True


			##判断是否是低价地区出售
			#if BigWorld.globalData['MerchantLowArea'] == spaceLabel:
			#	if BigWorld.globalData['MerchantLowItem'] == currItem.id:
			#		yinpiao += ( ( areaYinpiao - sellYinpiao ) * BigWorld.globalData['MerchantLowPercent'] + sellYinpiao ) * argAmount
			#		changeValue = True

			#if not changeValue:
			#	yinpiao += sellYinpiao * argAmount

			yinpiao += sellYinpiao * DARK_MERCHANT_RATE * argAmount
			items.append( currItem )

		for argAmount, argUid in zip( argAmountList, argUidList ):
			self.removeItemByUid_( argUid, argAmount, csdefine.DELETE_ITEM_SELLTONPC )

		# 给钱玩家
		self.gainMoney( int( yinpiao ), csdefine.CHANGE_MONEY_SELLITEMTODARKMERCHANT )
		self.clientEntity( merchantEntity.id ).onBuyArrayFromCB( 1 )	# 出售成功


	def buyItemFromDarkMerchant( self, merchantEntity, itemArray, argIndices, argAmountList ):
		"""
		玩家买物品

		@param merchantEntity: 商人NPC entity or mailbox
		@type  merchantEntity: MAILBOX
		@param  itemArray: 要买的物品实例数组
		@type   itemArray: ARRAY OF ITEM
		@param argIndices: 要买的哪个商品
		@type  argIndices: ARRAY OF UINT16
		@param argAmountList: 要买的数量
		@type  argAmountList: ARRAY OF UINT16
		@param	playerEntityID:	新添加的变量，用于通知客户端商品数量改变	add by gjx 2009-1-12
		@type	playerEntityID:	OBJECT_ID
		@return:              无
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		merchantEntity = BigWorld.entities[ merchantEntity.id ]
		money = 0
		for itemInstance in itemArray:
			# 确保是int类型的
			money += merchantEntity.getScript().yinpiaoSection[str(itemInstance.id)].readInt( 'DarkMerchant' ) * itemInstance.amount

		if money > self.money:
			ERROR_MSG( "%s(%i): no enough money." % (self.playerName, self.id) )
			self.statusMessage( csstatus.NPC_TRADE_NOT_ENOUGH_MONEY )
			return

		kitbagState = self.checkItemsPlaceIntoNK_( itemArray )

		if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			self.statusMessage( csstatus.NPC_TRADE_SPACE_NOT_ENOUGH )
			return
		if kitbagState == csdefine.KITBAG_ITEM_COUNT_LIMIT:
			self.statusMessage( csstatus.NPC_TRADE_ITEM_LIMIT_COUNT )
			return

		for itemInstance in itemArray:
			self.addItemAndNotify_( itemInstance, csdefine.ADD_ITEM_BUYITEMFROMDARKMERCHANT )

		# 玩家给钱
		self.payMoney( money, csdefine.CHANGE_MONEY_BUYITEMFROMDARKMERCHANT )

		# 到了这一步，不管购买成功失败，都当作成功
		for argIndex, argAmount in zip( argIndices, argAmountList ):
			merchantEntity.sellToCB( argIndex, argAmount, self.id )
