# -*- coding: gb18030 -*-
#
# $Id: RoleTradeWithNPC.py,v 1.23 2008-08-08 06:49:52 kebiao Exp $

"""
"""

import BigWorld
import csdefine
import csconst
import csstatus
from bwdebug import *
from MsgLogger import g_logger
import ItemTypeEnum
import items
import sys
from TongItemResearchData import TongItemResearchData

tongItemResearchData = TongItemResearchData.instance()
g_item = items.instance()


def priceCarry( price ):
	"""
	2008-11-4 11:42 yk
	策划规则是：如果价钱小于1，就算1
	如果大于1，则取整
	"""
	if price < 1:
		return 1
	return int( price )

def darkPriceCarry( price ):
	"""
	四舍五入取整
	"""
	return int( price + 0.5 )

JuanZhou = 50101025

class RoleTradeWithNPC:
	"""
	与NPC商人交易
	"""

	#self.redeemItems = []		# 可赎回物品列表

	def calcCastellanPriceRebate( self, money ):
		"""
		计算NPC所在城市的城市主人(当某帮会占领的该城市后)的购物打折
		"""
#		if self.tong_dbID > 0 and self.tong_holdCity == self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ):
#			return money * 0.9
		return money

	def sellToNPC( self, chapmanEntity, argUid, argAmount ):
		"""
		玩家卖物品
		@param chapmanEntity: 商人NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param   argUid: 物品的唯一ID
		@type    argUid: INT64
		@param   argAmount: 要买的数量
		@type    argAmount: UINT16
		@return: 			无
		"""
		# 包裹不能上锁
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return
		# 取得所要卖的物品
		currItem = self.getItemByUid_( argUid )
		if currItem is None:
			ERROR_MSG( "%s(%i): I no such item(argUid = %i)" % (self.playerName, self.id, argUid) )
			return
		# 不能卖的不可以出售
		if not currItem.canSell():
			ERROR_MSG( "%s(%i): item(name = %s) can't sell." % (self.playerName, self.id, currItem.name) )
			return
		# 判断物品是否被冻结。没有做这个判断的话，可以复制物品使用效果。复制条件是，物品可被出售给npc商人，物品技能有吟唱时间。
		# 复制方法：宠物蛋为例，使用物品吟唱时将物品出售给npc，使用成功获得宠物，此时再赎回物品，此物品又可被使用。
		# 15:06 2009-10-20，wsf
		if currItem.isFrozen():
			return
		# 骗人，玩家身上根本没这么多
		if currItem.getAmount() < argAmount:
			ERROR_MSG( "%s(%i): not more item(name = %s), current amount = %i, sell amount = %i." % (self.playerName, self.id, currItem.name, currItem.getAmount(), argAmount) )
			return
		chapmanEntity = BigWorld.entities[ chapmanEntity.id ]
		buyMoney = priceCarry( currItem.getPrice() * chapmanEntity.invBuyPercent ) * argAmount

		# 开卖了。。。
		if self.testAddMoney( buyMoney ) > 0:
			# 玩家身上钱太多了
			ERROR_MSG( "%s(%i): 现金太多了" % (self.playerName) )
			return

		# 在删除物品之前把物品加入可赎回物品列表
		if currItem.amount == argAmount:
			# 如果是整组物品卖出去
			tempItem = currItem
		else:
			# 不是整组物品卖出去，我们需要用new()复制一个新的物品出来
			# 这样可以保证赎回的时候，物品UID不一样
			# 保证不会有相同uid的物品加入到背包中，从而引起一些奇怪的错误
			tempItem = currItem.new()
			tempItem.setAmount( argAmount )
		tempItem.setPrice( buyMoney )		# 设置物品的价格

		self._addRedeemItem( tempItem )

		# 减少玩家身上物品的数量
		#currItem.setAmount( currItem.getAmount() - argAmount, self )
		self.removeItemByUid_( argUid, argAmount, csdefine.DELETE_ITEM_SELLTONPC )

		# 给钱玩家
		self.gainMoney( int(buyMoney), csdefine.CHANGE_MONEY_SELLTONPC )
		# 写日志
		try:
			g_logger.tradeNpcSellLog( self.databaseID, self.getName(), currItem.id, currItem.name(), currItem.getAmount(), self.grade, chapmanEntity.className )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	### end of buyFrom() method ###

	def sellArrayToNPC( self, chapmanEntity, argUidList, argAmountList ):
		"""
		define method
		玩家卖物品

		@param  chapmanEntity: 商人NPC entity or mailbox
		@type   chapmanEntity: MAILBOX
		@param  argUidList: 要买的哪个商品
		@type   argUidList: ARRAY OF INT64
		@param  argAmountList: 要买的数量
		@type   argAmountList: ARRAY OF UINT16
		@return:               无
		"""
		# 包裹不能上锁
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return

		chapmanEntity = BigWorld.entities.get( chapmanEntity.id, None )
		if chapmanEntity is None:
			return

		# 检查所有要卖的商品的存在与否以及汇总出售后金额
		moneys = 0
		invoiceList = zip( argUidList, argAmountList )
		items = []		# 记录每一个物品
		moneyList = []	# 记录每一个物品的卖出价格
		for argUid, argAmount in invoiceList:
			currItem = self.getItemByUid_( argUid )
			if currItem is None:
				ERROR_MSG( "%s(%i): no such item(argUid = %i)" % (self.playerName, self.id, argUid) )
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# 出售失败
				return
			if not currItem.canSell():	# 不能卖的不可以出售
				self.statusMessage( csstatus.NPC_TRADE_ITEM_NOT_SELL )
				ERROR_MSG( "%s(%i): item(name = %s) can't sell." % (self.playerName, self.id, currItem.name) )
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# 出售失败
				return
			# 判断物品是否被冻结。没有做这个判断的话，可以复制物品使用效果。复制条件是，物品可被出售给npc商人，物品技能有吟唱时间。
			# 复制方法：宠物蛋为例，使用物品吟唱时将物品出售给npc，使用成功获得宠物，此时再赎回物品，此物品又可被使用。
			# 15:06 2009-10-20，wsf
			if currItem.isFrozen():
				self.statusMessage( csstatus.NPC_TRADE_ITEM_NOT_SELL )
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# 出售失败
				return
			if currItem.getAmount() < argAmount:		# 骗人，玩家身上根本没这么多
				ERROR_MSG( "%s(%i): not more item(name = %s), current amount = %i, sell amount = %i." % (self.playerName, self.id, currItem.name, currItem.getAmount(), argAmount) )
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# 出售失败
				return
			#moneys += int( currItem.getPrice() * chapmanEntity.invBuyPercent ) * argAmount

			currMoney = priceCarry( currItem.getPrice() * chapmanEntity.invBuyPercent ) * argAmount
			moneys += currMoney
			moneyList.append( currMoney )
			items.append( currItem )

		# 开卖了。。。
		if self.testAddMoney( moneys ) > 0:
			# 玩家身上钱太多了
			ERROR_MSG( "%s(%i): 现金太多了" % (self.playerName, self.id) )
			self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# 出售失败
			return
		for item, argAmount, money, argUid in zip( items, argAmountList, moneyList, argUidList ):
			# 在删除物品之前把物品加入可赎回物品列表
			if item.amount == argAmount:
				# 如果是整组物品卖出去
				tempItem = item
			else:
				# 不是整组物品卖出去，我们需要用new()复制一个新的物品出来
				# 这样可以保证赎回的时候，物品UID不一样
				# 保证不会有相同uid的物品加入到背包中，从而引起一些奇怪的错误
				tempItem = item.new()
				tempItem.setAmount( argAmount )
			tempItem.setPrice( money )		# 设置物品的价格
			self._addRedeemItem( tempItem )
			#item.setAmount( item.getAmount() - argAmount, self )
			self.removeItemByUid_( argUid, argAmount, csdefine.DELETE_ITEM_SELLTONPC )

			LOG_MSG( "databaseID(%i), playerName(%s), NPCClass(%s), NPCName(%s), itemID(%s), itemName(%s), itemAmount(%i)"\
				%( self.databaseID, self.getName(), chapmanEntity.className, chapmanEntity.getName(), tempItem.id, tempItem.name(), tempItem.amount ) )
				
			try:
				g_logger.tradeNpcSellLog( self.databaseID, self.getName(), item.uid, item.name(), item.getAmount(), self.grade, chapmanEntity.className )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

		# 给钱玩家
		self.gainMoney( int(moneys), csdefine.CHANGE_MONEY_SELLTONPC )
		self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 1 )	# 出售成功




	def buyFromNPC( self, chapmanEntity, newInvoice, argIndex, argAmount ):
		"""
		玩家买物品

		@param chapmanEntity: 商人NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param  newInvoice: 要买的商品
		@type   newInvoice: INVOICEITEM
		@param   argIndex: 要买的哪个商品
		@type    argIndex: UINT16
		@param   argAmount: 要买的数量
		@type    argAmount: UINT16
		@return:              无
		"""
		# 包裹不能上锁
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return
		if not self.checkItemFromNKCK_( newInvoice.getSrcItem(), invoiceAmount ):
			self.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		chapmanEntity = BigWorld.entities[ chapmanEntity.id ]

		status = newInvoice.checkRequire( self, chapmanEntity, argAmount )
		if status != csstatus.NPC_TRADE_CAN_BUY:
			self.statusMessage( status )
			return
		newInvoice.doTrade(  self, chapmanEntity, argAmount )
		chapmanEntity.sellToCB( argIndex, argAmount, self.id )

	def haveEnoughCredit( self , item ):
		"""
		玩家是否含有足够的声望
		@param  item : 物品实例
		@type   item : ITEME
		@RETURN bool : 是否满足声望的需求
		"""
		creditDic = item.credit()
		for key in creditDic:
			value = self.getPrestige( key )
			if value is None or value < creditDic[key]:
				return False
		return True

	def buyArrayFromNPC( self, chapmanEntity, invoiceArray, argIndices, argAmountList ):
		"""
		Define method.
		玩家买物品

		@param chapmanEntity: 商人NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param  invoiceArray: 要买的商品实例数组
		@type   invoiceArray: ARRAY OF ITEM
		@param argIndices: 要买的哪个商品
		@type  argIndices: ARRAY OF UINT16
		@param argAmountList: 要买的数量
		@type  argAmountList: ARRAY OF UINT16
		@return:              无
		"""
		# 包裹不能上锁
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return
		zipInvoiceArray = zip( invoiceArray, argAmountList )
		items = []
		for invoiceItem, amount in zipInvoiceArray:
			item = invoiceItem.getSrcItem()
			item.setAmount( amount )
			items.append( item )
		kitbagState = self.checkItemsPlaceIntoNK_( items )
		if kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			self.statusMessage( csstatus.NPC_TRADE_SPACE_NOT_ENOUGH )
			return
		if kitbagState == csdefine.KITBAG_ITEM_COUNT_LIMIT:
			self.statusMessage( csstatus.NPC_TRADE_ITEM_LIMIT_COUNT )
			return

		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		chapmanEntity = BigWorld.entities[ chapmanEntity.id ]
		self.beginArrayBuyFromNPC()
		for invoiceItem, amount in zipInvoiceArray:
			status = invoiceItem.checkRequireArrayInvoice( self, chapmanEntity, amount )
			if status != csstatus.NPC_TRADE_CAN_BUY:
				self.statusMessage( status )
				self.endArrayBuyFromNPC()
				return
		for invoiceItem, amount in zipInvoiceArray:
			invoiceItem.doTrade(  self, chapmanEntity, amount )
			chapmanEntity.sellToCB( argIndices.pop( 0 ), amount, self.id )
		self.endArrayBuyFromNPC()

	def beginArrayBuyFromNPC( self ):
		"""
		开始批量购买物品初始化
		"""
		self.setTemp( "npc_trade_money", 0 )
		self.setTemp( "npc_trade_need_items", {} )
		self.setTemp( "npc_trade_need_dancePoint", 0 )
		self.setTemp( "npc_trade_need_tongContribute", 0 )
		self.setTemp( "npc_trade_need_personalScore", 0 )
		self.setTemp( "npc_trade_need_teamCompetitionPoint",0 )
		self.setTemp( "npc_trade_need_accumPoint",0 )

	def endArrayBuyFromNPC( self ):
		"""
		批量购买物品结束临时变量的清理工作
		"""
		self.removeTemp( "npc_trade_money" )
		self.removeTemp( "npc_trade_need_items" )
		self.removeTemp( "npc_trade_need_dancePoint" )
		self.removeTemp( "npc_trade_need_tongContribute" )
		self.removeTemp( "npc_trade_need_personalScore" )
		self.removeTemp( "npc_trade_need_teamCompetitionPoint" )
		self.removeTemp( "npc_trade_need_accumPoint" )

	# -------------------------------------------------------------------------------
	# 买卖商品赎回功能接口
	# -------------------------------------------------------------------------------
	def _addRedeemItem( self, item ):
		"""
		往可赎回列表里增加一个物品

		param item:	玩家卖出的物品
		type item:	ITEM
		"""
		if len( self.redeemItems ) < csconst.REDEEM_ITEM_MAX_COUNT:	# 把物品放进可赎回物品列表
			self.redeemItems.append( item )
		else:		# 把最旧的数据删除
			self.redeemItems.pop( 0 )
			self.redeemItems.append( item )

		self.client.addRedeemItemUpdate( item )	# 通知client更新可赎回列表数据


	def redeemItem( self, srcEntityID, uid, entityID ):
		"""
		Exposed method.
		赎回物品的接口

		param uid:	物品的唯一标识
		type uid:	INT64
		param entityID:	商人npc的id
		type entityID:	OBJECT_ID
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % ( srcEntityID, self.id ) )
			return
		npc = BigWorld.entities.get( entityID )
		if npc == None:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return

		# 判断是否在允许交易范围内
		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )
			DEBUG_MSG( "too far from trade npc: %i. ( srcEntityID: %s )" % ( entityID, self.playerName ) )
			return

		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return

		# 会有统一的判断对应的交易npc的做法

		tempItem = None
		for item in self.redeemItems:
			if item.getUid() == uid:
				tempItem = item
				index = self.redeemItems.index( item )
				break
		if tempItem is None:
			HACK_MSG( "请求的物品不存在。" )
			return

		# 赎物品直接读取物品记录的价格就可以
		# 而不需要进行什么额外的计算
		money = tempItem.getRecodePrice()
		if money > self.money:
			DEBUG_MSG( "玩家的钱不足以赎回此物品。" )
			return

		# 刷新一遍物品的价格
		tempItem.updatePrice()

		if not self.addItemAndNotify_( tempItem, csdefine.ADD_ITEM_REDEEMITEM ):	# 把赎回的物品加入背包
			DEBUG_MSG( "物品加入背包失败，可能是因为背包中无空位。" )
			return
		self.redeemItems.pop( index )		# 从可赎回列表中删除物品
		self.payMoney( money, csdefine.CHANGE_MONEY_REDEEMITEM )				# 扣除玩家相应金钱

		self.client.delRedeemItemUpdate( uid )	# 更新client数据

		LOG_MSG( "databaseID(%i), playerName(%s), NPCClass(%s), NPCName(%s), itemID(%s), itemName(%s), itemAmount(%i)"\
			%( self.databaseID, self.getName(), npc.className, npc.getName(), tempItem.id, tempItem.name(), tempItem.amount ) )

	def sellToDarkTrader( self, chapmanEntity, argUid, argAmount ):
		"""
		玩家卖物品给投机商人
		@param chapmanEntity: 投机商人NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param   argUid: 要卖的哪个商品
		@type    argUid: INT64
		@param   argAmount: 要卖的数量
		@type    argAmount: UINT16
		@return: 			无
		"""
		# 取得所要卖的物品
		currItem = self.getItemByUid_( argUid )
		if currItem is None:
			ERROR_MSG( "%s(%i): I no such item(argUid = %i)" % (self.playerName, self.id, argUid) )
			return
		# 骗人，玩家身上根本没这么多
		if currItem.getAmount() < argAmount:
			ERROR_MSG( "%s(%i): not more item(name = %s), current amount = %i, sell amount = %i." % (self.playerName, self.id, currItem.name, currItem.getAmount(), argAmount) )
			return
		itemPrice = currItem.getPrice()
		sellMoney = darkPriceCarry(  itemPrice * chapmanEntity.invBuyPercent ) * argAmount

		# 玩家出售的东西并不是投机商人所收购的
		if currItem.id != chapmanEntity.currentGoodID:
			self.statusMessage( csstatus.NOT_DARK_TRADER_ITEM )
			return

		# 开卖了。。。
		if self.testAddMoney( sellMoney ) > 0:
			# 玩家身上钱太多了
			ERROR_MSG( "%s(%i): 现金太多了" % (self.playerName) )
			return

		# 减少玩家身上物品的数量
		self.removeItemByUid_( argUid, argAmount, csdefine.DELETE_ITEM_SELLTONPC )

		# 给钱玩家
		self.gainMoney( int( sellMoney ), csdefine.CHANGE_MONEY_SELLTONPC )

	def sellArrayToDarkTrader( self, chapmanEntity, argUidList, argAmountList ):
		"""
		玩家卖物品

		@param  chapmanEntity: 商人NPC entity or mailbox
		@type   chapmanEntity: MAILBOX
		@param  argUidList: 要买的哪个商品
		@type   argUidList: ARRAY OF INT64
		@param  argAmountList: 要买的数量
		@type   argAmountList: ARRAY OF UINT16
		@return:               无
		"""
		# 检查所有要卖的商品的存在与否以及汇总出售后金额
		moneys = 0
		invoiceList = zip( argUidList, argAmountList )
		items = []		# 记录每一个物品
		moneyList = []	# 记录每一个物品的卖出价格
		for argUid, argAmount in invoiceList:
			currItem = self.getItemByUid_( argUid )
			if currItem is None:
				ERROR_MSG( "%s(%i): no such item(argUid = %i)" % (self.playerName, self.id, argUid) )
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# 出售失败
				return
			if currItem.getAmount() < argAmount:		# 骗人，玩家身上根本没这么多
				ERROR_MSG( "%s(%i): not more item(name = %s), current amount = %i, sell amount = %i." % (self.playerName, self.id, currItem.name, currItem.getAmount(), argAmount) )
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# 出售失败
				return
			# 玩家出售的东西并不是投机商人所收购的
			if currItem.id != chapmanEntity.currentGoodID:
				self.statusMessage( csstatus.NOT_DARK_TRADER_ITEM )
				return

			itemPrice = currItem.getPrice()
			currMoney = darkPriceCarry( itemPrice * chapmanEntity.invBuyPercent ) * argAmount
			moneys += currMoney
			moneyList.append( currMoney )
			items.append( currItem )

		# 开卖了。。。
		if self.testAddMoney( moneys ) > 0:
			# 玩家身上钱太多了
			ERROR_MSG( "%s(%i): 现金太多了" % (self.playerName, self.id) )
			self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# 出售失败
			return
		for item, argAmount, money, argUid in zip( items, argAmountList, moneyList, argUidList ):
			# 在删除物品之前把物品加入可赎回物品列表
			self.removeItemByUid_( argUid, argAmount, csdefine.DELETE_ITEM_SELLTONPC )	# 移除卖出的物品
			LOG_MSG( "databaseID(%i), playerName(%s), NPCClass(%s), NPCName(%s), itemID(%s), itemName(%s), itemAmount(%i)"\
				%( self.databaseID, self.getName(), chapmanEntity.className, chapmanEntity.getName(), item.id, item.name(), item.amount ) )
		# 给钱玩家
		self.gainMoney( int(moneys), csdefine.CHANGE_MONEY_SELLTONPC )
		self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 1 )	# 出售成功

	def buyFromDarkTrader( self, chapmanEntity, itemInstance, argIndex, argAmount ):
		"""
		玩家买物品

		@param chapmanEntity: 商人NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param  itemInstance: 要买的物品实例
		@type   itemInstance: ITEM
		@param   argIndex: 要买的哪个商品
		@type    argIndex: UINT16
		@param   argAmount: 要买的数量
		@type    argAmount: UINT16
		@return:              无
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		chapmanEntity = BigWorld.entities[ chapmanEntity.id ]
		# 确保是int类型的
		moneys = priceCarry(self.calcCastellanPriceRebate( itemInstance.getPrice() * chapmanEntity.invSellPercent ) ) * itemInstance.getAmount()

		# 钱不够
		if moneys > self.money:
			ERROR_MSG( "%s(%i): no enough money." % (self.playerName, self.id) )
			return
		# 商会卷轴不够
		if not self.checkItemFromNKCK_( JuanZhou, argAmount ):
			self.statusMessage( csstatus.NOT_ENOUGH_DARK_TRADER_JUANZHOU )
			return

		if not self.addItemAndNotify_( itemInstance, csdefine.ADD_ITEM_BUYFROMDARKTRADER ):
			self.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return

		# 玩家给钱
		self.payMoney( moneys, csdefine.CHANGE_MONEY_BUY_FROM_DARKTRADER )
		# 消耗玩家商会卷轴
		self.removeItemTotal( JuanZhou, argAmount, csdefine.DELETE_ITEM_BUYFROMDARKTRADER )
		chapmanEntity.sellToCB( argIndex, argAmount, self.id )
		try:
			g_logger.tradeNpcBuyLog( self.databaseID, self.getName(), itemInstance.uid, itemInstance.name(), itemInstance.getAmount(), self.grade, chapmanEntity.className, player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def buyArrayFromDarkTrader( self, chapmanEntity, itemArray, argIndices, argAmountList ):
		"""
		玩家买物品

		@param chapmanEntity: 商人NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param  itemArray: 要买的物品实例数组
		@type   itemArray: ARRAY OF ITEM
		@param argIndices: 要买的哪个商品
		@type  argIndices: ARRAY OF UINT16
		@param argAmountList: 要买的数量
		@type  argAmountList: ARRAY OF UINT16
		@return:              无
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		chapmanEntity = BigWorld.entities[ chapmanEntity.id ]
		moneys = 0
		juanzhouAmount = 0
		for itemInstance in itemArray:
			# 确保是int类型的
			moneys += priceCarry( self.calcCastellanPriceRebate( itemInstance.getPrice() * chapmanEntity.invSellPercent ) ) * itemInstance.getAmount()
			juanzhouAmount += itemInstance.getAmount()

		if moneys > self.money:
			ERROR_MSG( "%s(%i): no enough money." % (self.playerName, self.id) )
			return

		if not self.haveEnoughCredit( itemArray[0] ): #使用itemArray[0]是因为LIST中都是相同的物品,LIST一定不会为空
			ERROR_MSG( "%s(%i): no enough credit." % (self.playerName, self.id) )
			return

		# 商会卷轴不够
		if not self.checkItemFromNKCK_( JuanZhou, juanzhouAmount ):
			self.statusMessage( csstatus.NOT_ENOUGH_DARK_TRADER_JUANZHOU )
			return

		kitbagState = self.checkItemsPlaceIntoNK_( itemArray )

		if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			self.statusMessage( csstatus.NPC_TRADE_SPACE_NOT_ENOUGH )
			return
		if kitbagState == csdefine.KITBAG_ITEM_COUNT_LIMIT:
			self.statusMessage( csstatus.NPC_TRADE_ITEM_LIMIT_COUNT )
			return

		for itemInstance in itemArray:
			if not self.addItemAndNotify_( itemInstance, csdefine.ADD_ITEM_BUYFROMDARKTRADER ):
				ERROR_MSG( "%s(%i): 严重错误：'%s' 不能放入背包中；理论与实际产生不同结果。" % (self.playerName, self.id, itemInstance.id) )
				moneys -= priceCarry(itemInstance.getPrice() * chapmanEntity.invSellPercent) * itemInstance.getAmount()
			try:
				g_logger.tradeNpcBuyLog( self.databaseID, self.getName(), itemInstance.uid, itemInstance.name(), itemInstance.getAmount(), self.grade, chapmanEntity.className, player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
		
		# 玩家给钱
		self.payMoney( moneys, csdefine.CHANGE_MONEY_BUY_FROM_DARKTRADER )
		# 消耗玩家卷轴
		self.removeItemTotal( JuanZhou, juanzhouAmount, csdefine.DELETE_ITEM_BUYFROMDARKTRADER )
		# 到了这一步，不管购买成功失败，都当作成功
		for argIndex, argAmount in zip( argIndices, argAmountList ):
			chapmanEntity.sellToCB( argIndex, argAmount, self.id )

	#--------------------------------帮会擂台-----------------------------------------
	def tongAbaBuyFromNPC( self, chapmanEntity, itemInstance, argIndex, argAmount ):
		"""
		玩家买帮会擂台物品

		@param chapmanEntity: 商人NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param  itemInstance: 要买的物品实例
		@type   itemInstance: ITEM
		@param   argIndex: 要买的哪个商品
		@type    argIndex: UINT16
		@param   argAmount: 要买的数量
		@type    argAmount: UINT16
		@return:              无
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		chapmanEntity = BigWorld.entities[ chapmanEntity.id ]
		spaceType = self.getCurrentSpaceType()
		if spaceType != csdefine.SPACE_TYPE_TONG_ABA:
			return False

		# 确保是int类型的
		mark = priceCarry(itemInstance.getWarIntegral() * chapmanEntity.invSellPercent) * itemInstance.getAmount()
		self.setTemp( "onTongAbabuyData", ( chapmanEntity, itemInstance, argIndex, argAmount ) )
		spaceBase = self.getCurrentSpaceBase()
		spaceEntity = BigWorld.entities.get( spaceBase.id )
		if spaceEntity and spaceEntity.isReal():
			spaceEntity.getScript().onNPCDealItemChangeAbaMark( spaceEntity, self, self.databaseID, mark, 0 )
		else:
			spaceBase.cell.remoteScriptCall( "onNPCDealItemChangeAbaMark", ( self, self.databaseID, mark, 0, ) )

	def onTongAbaBuyFromNPCCallBack( self, state ):
		"""
		购买帮会擂台物品的回调
		"""
		spaceType = self.getCurrentSpaceType()
		if spaceType != csdefine.SPACE_TYPE_TONG_ABA:
			return False

		if state == 1:
			chapmanEntity, itemInstance, argIndex, argAmount = self.popTemp( "onTongAbabuyData" )
			if not self.addItemAndNotify_( itemInstance, csdefine.ADD_ITEM_TONGABABUYFROMNPC ):
				self.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
				return
						
			mark = priceCarry(itemInstance.getWarIntegral() * chapmanEntity.invSellPercent) * itemInstance.getAmount()
			chapmanEntity.sellToCB( argIndex, argAmount, self.id )
			tong = self.tong_getTongEntity( self.tong_dbID )
			tong.onWarBuyItemsMessage( self.databaseID, argAmount, itemInstance.name(), mark )
			#写日志
			try:
				g_logger.tradeNpcBuyLog( self.databaseID, self.getName(), itemInstance.uid, itemInstance.name(), itemInstance.getAmount(), self.grade, chapmanEntity.className, player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
		else:
			self.statusMessage( csstatus.TONG_WAR_BUY_INVALID )

	def tongAbaBuyArrayFromNPC( self, chapmanEntity, itemArray, argIndices, argAmountList ):
		"""
		玩家买帮会擂台物品
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		chapmanEntity = BigWorld.entities[ chapmanEntity.id ]
		spaceType = self.getCurrentSpaceType()
		if spaceType != csdefine.SPACE_TYPE_TONG_ABA:
			return False

		mark = 0
		for itemInstance in itemArray:
			# 确保是int类型的
			mark += priceCarry(itemInstance.getWarIntegral() * chapmanEntity.invSellPercent) * itemInstance.getAmount()

		self.setTemp( "onTongAbabuyData", ( chapmanEntity, itemArray, argIndices, argAmountList ) )
		spaceBase = self.getCurrentSpaceBase()
		spaceEntity = BigWorld.entities.get( spaceBase.id )
		if spaceEntity and spaceEntity.isReal():
			spaceEntity.getScript().onNPCDealItemChangeAbaMark( spaceEntity, self, self.databaseID, mark, 1 )
		else:
			spaceBase.cell.remoteScriptCall( "onNPCDealItemChangeAbaMark", ( self, self.databaseID, mark, 1, ) )

	def onTongAbaBuyArrayFromNPCCallBack( self, state ):
		"""
		购买帮会战场物品的回调
		"""
		spaceType = self.getCurrentSpaceType()
		if spaceType != csdefine.SPACE_TYPE_TONG_ABA:
			return False

		if state == 1:
			mark = 0
			tong= self.tong_getTongEntity( self.tong_dbID )
			chapmanEntity, itemArray, argIndices, argAmountList = self.popTemp( "onTongAbabuyData" )

			for itemInstance in itemArray:
				# 确保是int类型的
				mark += priceCarry(itemInstance.getWarIntegral() * chapmanEntity.invSellPercent) * itemInstance.getAmount()
			kitbagState = self.checkItemsPlaceIntoNK_( itemArray )

			if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
				self.statusMessage( csstatus.NPC_TRADE_SPACE_NOT_ENOUGH )
				return
			if kitbagState == csdefine.KITBAG_ITEM_COUNT_LIMIT:
				self.statusMessage( csstatus.NPC_TRADE_ITEM_LIMIT_COUNT )
				return

			for itemInstance in itemArray:
				if not self.addItemAndNotify_( itemInstance, csdefine.ADD_ITEM_TONGABABUYFROMNPC ):
					ERROR_MSG( "%s(%i): 严重错误：'%s' 不能放入背包中；理论与实际产生不同结果。" % (self.playerName, self.id, itemInstance.id) )
					mark -= priceCarry(itemInstance.getWarIntegral() * chapmanEntity.invSellPercent) * itemInstance.getAmount()
				else:
					# tong.onWarBuyItemsMessage( self.databaseID, itemInstance.amount, itemInstance.name(), mark )
					pass
				LOG_MSG( "databaseID(%i), playerName(%s), NPCClass(%s), NPCName(%s), itemID(%s), itemName(%s), itemAmount(%i)"\
					%( self.databaseID, self.getName(), chapmanEntity.className, chapmanEntity.getName(), itemInstance.id, itemInstance.name(), itemInstance.amount ) )
				try:
					g_logger.tradeNpcBuyLog( self.databaseID, self.getName(), itemInstance.uid, itemInstance.name(), itemInstance.getAmount(), self.grade, chapmanEntity.className, player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )
				
			# 到了这一步，不管购买成功失败，都当作成功
			for argIndex, argAmount in zip( argIndices, argAmountList ):
				chapmanEntity.sellToCB( argIndex, argAmount, self.id )
			tong = self.tong_getTongEntity( self.tong_dbID )
			tong.onWarBuyItemsMessage( self.databaseID, argAmount, itemInstance.name(), mark )
		else:
			self.statusMessage( csstatus.TONG_WAR_BUY_INVALID )

	def sellTongAbaItemArrayToNPC( self, chapmanEntity, argUidList, argAmountList ):
		"""
		玩家卖物品

		@param  chapmanEntity: 商人NPC entity or mailbox
		@type   chapmanEntity: MAILBOX
		@param  argUidList: 要买的哪个商品
		@type   argUidList: ARRAY OF INT64
		@param  argAmountList: 要买的数量
		@type   argAmountList: ARRAY OF UINT16
		@return:               无
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		chapmanEntity = BigWorld.entities[ chapmanEntity.id ]
		# 检查所有要卖的商品的存在与否以及汇总出售后金额
		moneys = 0
		invoiceList = zip( argUidList, argAmountList )
		items = []		# 记录每一个物品
		moneyList = []	# 记录每一个物品的卖出价格

		for argUid, argAmount in invoiceList:
			currItem = self.getItemByUid_( argUid )
			if currItem is None:
				ERROR_MSG( "%s(%i): no such item(argUid = %i)" % (self.playerName, self.id, argUid) )
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# 出售失败
				return
			if not currItem.canSell():	# 不能卖的不可以出售
				ERROR_MSG( "%s(%i): item(name = %s) can't sell." % (self.playerName, self.id, currItem.name) )
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# 出售失败
				return
			# 判断物品是否被冻结。没有做这个判断的话，可以复制物品使用效果。复制条件是，物品可被出售给npc商人，物品技能有吟唱时间。
			# 复制方法：宠物蛋为例，使用物品吟唱时将物品出售给npc，使用成功获得宠物，此时再赎回物品，此物品又可被使用。
			# 15:06 2009-10-20，wsf
			if currItem.isFrozen():
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# 出售失败
				return
			if currItem.getAmount() < argAmount:		# 骗人，玩家身上根本没这么多
				ERROR_MSG( "%s(%i): not more item(name = %s), current amount = %i, sell amount = %i." % (self.playerName, self.id, currItem.name, currItem.getAmount(), argAmount) )
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# 出售失败
				return
			currMoney = priceCarry( currItem.getPrice() * chapmanEntity.invBuyPercent ) * argAmount
			moneys += currMoney
			moneyList.append( currMoney )
			items.append( currItem )

		# 开卖了。。。
		if self.testAddMoney( moneys ) > 0:
			# 玩家身上钱太多了
			ERROR_MSG( "%s(%i): 现金太多了" % (self.playerName, self.id) )
			self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# 出售失败
			return

		for item, argAmount, money, argUid in zip( items, argAmountList, moneyList, argUidList ):
			# 在删除物品之前把物品加入可赎回物品列表
			if item.amount == argAmount:
				# 如果是整组物品卖出去
				tempItem = item
			else:
				# 不是整组物品卖出去，我们需要用new()复制一个新的物品出来
				# 这样可以保证赎回的时候，物品UID不一样
				# 保证不会有相同uid的物品加入到背包中，从而引起一些奇怪的错误
				tempItem = item.new()
				tempItem.setAmount( argAmount )
			tempItem.setPrice( money )		# 设置物品的价格
			self._addRedeemItem( tempItem )
			#item.setAmount( item.getAmount() - argAmount, self )
			self.removeItemByUid_( argUid, argAmount, csdefine.DELETE_ITEM_SELLTONPC )

			LOG_MSG( "databaseID(%i), playerName(%s), NPCClass(%s), NPCName(%s), itemID(%s), itemName(%s), itemAmount(%i)"\
				%( self.databaseID, self.getName(), chapmanEntity.className, chapmanEntity.getName(), tempItem.id, tempItem.name(), tempItem.amount ) )

		# 给钱玩家
		self.gainMoney( int(moneys), csdefine.CHANGE_MONEY_SELLTONPC )
		self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 1 )	# 出售成功

	def sellTongAbaItemToNPC( self, chapmanEntity, argUid, argAmount ):
		"""
		玩家卖物品
		@param chapmanEntity: 商人NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param   argUid: 要买的哪个商品
		@type    argUid: INT64
		@param   argAmount: 要买的数量
		@type    argAmount: UINT16
		@return: 			无
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		chapmanEntity = BigWorld.entities[ chapmanEntity.id ]
		# 取得所要卖的物品
		currItem = self.getItemByUid_( argUid )
		if currItem is None:
			ERROR_MSG( "%s(%i): I no such item(argUid = %i)" % (self.playerName, self.id, argUid) )
			return
		# 不能卖的不可以出售
		if not currItem.canSell():
			ERROR_MSG( "%s(%i): item(name = %s) can't sell." % (self.playerName, self.id, currItem.name) )
			return
		# 判断物品是否被冻结。没有做这个判断的话，可以复制物品使用效果。复制条件是，物品可被出售给npc商人，物品技能有吟唱时间。
		# 复制方法：宠物蛋为例，使用物品吟唱时将物品出售给npc，使用成功获得宠物，此时再赎回物品，此物品又可被使用。
		# 15:06 2009-10-20，wsf
		if currItem.isFrozen():
			self.statusMessage( csstatus.NPC_TRADE_ITEM_NOT_SELL )
			return
		# 骗人，玩家身上根本没这么多
		if currItem.getAmount() < argAmount:
			ERROR_MSG( "%s(%i): not more item(name = %s), current amount = %i, sell amount = %i." % (self.playerName, self.id, currItem.name, currItem.getAmount(), argAmount) )
			return
		buyMoney = priceCarry( currItem.getPrice() * chapmanEntity.invBuyPercent ) * argAmount

		# 开卖了。。。
		if self.testAddMoney( buyMoney ) > 0:
			# 玩家身上钱太多了
			ERROR_MSG( "%s(%i): 现金太多了" % (self.playerName) )
			return

		# 在删除物品之前把物品加入可赎回物品列表
		if currItem.amount == argAmount:
			# 如果是整组物品卖出去
			tempItem = currItem
		else:
			# 不是整组物品卖出去，我们需要用new()复制一个新的物品出来
			# 这样可以保证赎回的时候，物品UID不一样
			# 保证不会有相同uid的物品加入到背包中，从而引起一些奇怪的错误
			tempItem = currItem.new()
			tempItem.setAmount( argAmount )
		tempItem.setPrice( buyMoney )		# 设置物品的价格

		self._addRedeemItem( tempItem )

		# 减少玩家身上物品的数量
		#currItem.setAmount( currItem.getAmount() - argAmount, self )
		self.removeItemByUid_( argUid, argAmount, csdefine.DELETE_ITEM_SELLTONPC )
		
		# 给钱玩家
		self.gainMoney( int(buyMoney), csdefine.CHANGE_MONEY_SELLTONPC )


	
	# ----------------------------------------------------------------
	# 英雄联盟版失落宝藏副本NPC装备交易功能
	# ----------------------------------------------------------------
	def buyYXLMEquipFromNPC( self, chapmanEntity, newInvoice, argIndex, argAmount ):
		"""
		玩家够买英雄联盟副本的装备
		@param chapmanEntity: 商人NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param  newInvoice: 要买的商品
		@type   newInvoice: INVOICEITEM
		@param   argIndex: 要买的哪个商品
		@type    argIndex: UINT16
		@param   argAmount: 要买的数量
		@type    argAmount: UINT16
		@return:              无
		"""
		chapmanEntity = BigWorld.entities.get( chapmanEntity.id )
		if chapmanEntity is None or chapmanEntity.isDestroyed :
			ERROR_MSG("Chapman(ID %i) is lose." % chapmanEntity.id)
			return
		status = newInvoice.checkRequire( self, chapmanEntity, argAmount )
		if status != csstatus.NPC_TRADE_CAN_BUY:
			self.statusMessage( status )
			return
		newInvoice.doTrade(  self, chapmanEntity, argAmount )
		chapmanEntity.sellToCB( argIndex, argAmount, self.id )

	def sellYXLMEquipToNPC( self, chapmanEntity, argUid, argAmount ) :
		"""
		玩家出售卖英雄联盟副本的装备
		@param chapmanEntity: 商人NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param   argUid: 物品的唯一ID
		@type    argUid: INT64
		@param   argAmount: 要买的数量
		@type    argAmount: UINT16
		@return: 			无
		"""
		equip = self.getYXLMEquipByUid( argUid )
		if equip :
			if equip.getAmount() < argAmount:
				ERROR_MSG( "%s(%i): not more item(name = %s), current amount = %i, sell amount = %i." % \
					(self.playerName, self.id, equip.name, equip.getAmount(), argAmount) )
				return
			chapmanEntity = BigWorld.entities[ chapmanEntity.id ]
			income = priceCarry( equip.getPrice() * chapmanEntity.invBuyPercent ) * argAmount
			self.addAccumPoint( income )
			self.removeYXLMEquip( argUid )
			currSpace = self.getCurrentSpaceBase().cell
			if hasattr( currSpace, "onPlayerRemoveEquip" ) :
				currSpace.onPlayerRemoveEquip( self.databaseID, argUid )
		else :
			ERROR_MSG( "Player(name:%s) don't have yxlm equip of uid %i" % ( self.playerName, argUid ) )

	def gainYXLMEquipFromNPC( self, chapmanEntity, equipItem ) :
		"""
		支付灵魂币购买英雄联盟副本的装备
		这里不会判断是否够钱，因为前面的流程已经做了判断
		"""
		if self.addYXLMEquip( equipItem ):
			currSpace = self.getCurrentSpaceBase().cell
			if hasattr( currSpace, "onPlayerAddEquip" ) :
				currSpace.onPlayerAddEquip( self.databaseID, equipItem )
			return True
		return False
	
	def addYXLMEquip( self, equipItem ) :
		"""
		<Define method>
		添加一件英雄联盟副本的装备
		@type	equipItem : ITEM
		@param	equipItem : 继承于CItemBase的物品实例
		"""
		if self.storeYXLMEquip( equipItem ) :
			if self.putOnYXLMEquip( equipItem ) :
				self.client.onAddYXLMEquip( equipItem )
				return True
			else :
				self.dropYXLMEquip( equipItem.uid )
				return False
		else :
			return False

	def removeYXLMEquip( self, equipUid ) :
		"""
		<Define method>
		@type	equipUid : UID
		@param	equipUid : 物品实例的UID
		"""
		equipID = self.getYXLMEquipIDByUid( equipUid )
		self.putOffYXLMEquip( equipUid )
		self.dropYXLMEquip( equipUid )
		self.refreshYXLMEquips( equipID )		# 删除一件装备后，相同ID装备添加的buff也会被删除，所以重新刷新相同ID的装备
		self.client.onRemoveYXLMEquip( equipUid )

	def putOnYXLMEquip( self, equipItem ):
		"""
		穿上英雄联盟副本的装备
		"""
		useResult = equipItem.use( self, self )
		if useResult != csstatus.SKILL_GO_ON and useResult is not None:
			self.statusMessage( useResult )
			return False
		return True

	def putOffYXLMEquip( self, equipUid ):
		"""
		脱下英雄联盟副本的装备
		"""
		self.removeAllBuffsBySkillID( self.querySpellIDByYXLMEquipUid( equipUid ), [csdefine.BUFF_INTERRUPT_NONE] )

	def storeYXLMEquip( self, equipItem ) :
		"""
		收藏英雄联盟副本的装备
		"""
		yxlmEqBag = self.getYXLMEquipBag( True )
		if len( yxlmEqBag ) >= csdefine.YXLM_MAX_EQUIP_AMOUNT :
			self.statusMessage( csstatus.YXLM_EQUIP_BAG_FULL )
			return False
		else :
			yxlmEqBag[equipItem.uid] = equipItem
			return True

	def dropYXLMEquip( self, equipUid ) :
		"""
		丢弃英雄联盟副本的装备
		"""
		yxlmEqBag = self.getYXLMEquipBag()
		if yxlmEqBag and equipUid in yxlmEqBag :
			del yxlmEqBag[equipUid]

	def refreshYXLMEquips( self, equipID ):
		"""
		刷新所有ID是equipID的装备
		"""
		for equip in self.getYXLMEquipsByID(equipID):
			self.putOnYXLMEquip(equip)

	def getYXLMEquipByUid( self, equipUid ) :
		"""
		根据uid获取身上的英雄联盟副本装备
		"""
		yxlmEqBag = self.getYXLMEquipBag()
		if yxlmEqBag and equipUid in yxlmEqBag :
			return yxlmEqBag[equipUid]
		else :
			return None

	def getYXLMEquipsByID( self, equipID ):
		"""
		根据uid获取身上的英雄联盟副本装备
		"""
		result = []
		yxlmEqBag = self.getYXLMEquipBag()
		if yxlmEqBag:
			for equip in yxlmEqBag.itervalues():
				if equip.id == equipID:
					result.append( equip )
		return result

	def getYXLMEquipIDByUid( self, equipUid ):
		"""
		根据uid获取身上的英雄联盟副本装备的ID
		"""
		equip = self.getYXLMEquipByUid( equipUid )
		if equip:
			return equip.id
		else:
			return None

	def querySpellIDByYXLMEquipUid( self, equipUid ) :
		"""
		查询英雄联盟装备对应的技能ID
		"""
		equip = self.getYXLMEquipByUid( equipUid )
		if equip :
			return equip.getSpellID()
		else :
			return 0

	def getYXLMEquipBag( self, createIfNotExist=False ) :
		"""
		获取英雄联盟副本装备的包裹
		"""
		yxlmEqBag = self.queryTemp( "YXLM_EQUIPS_BAG" )
		if yxlmEqBag :
			return yxlmEqBag
		elif createIfNotExist :
			yxlmEqBag = {}
			self.setTemp( "YXLM_EQUIPS_BAG", yxlmEqBag )
			return yxlmEqBag
		else :
			return None

	def hasYXLMEquip( self, equipUid ) :
		"""
		是否拥有指定uid的英雄联盟装备
		"""
		return self.getYXLMEquipByUid(equipUid) is not None




	# ---------------------------------------------帮会特殊商城------------------------------------------
	def buyTongSpecialArrayFromNPC( self, chapman, memberDBID, invoiceIDs, amountList ):
		"""
		购买帮会特殊商品
		@param chapmanEntity: 商人NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@ param memberDBID: 帮会成员的dbid
		@type  memberDBID: BASE_DBID
		@param  itemArray: 要买的物品实例数组
		@type   itemArray: ARRAY OF ITEM
		@param argIndices: 要买的哪个商品
		@type  argIndices: ARRAY OF UINT16
		@param argAmountList: 要买的数量
		@type  argAmountList: ARRAY OF UINT16
		@return:              无
		"""
		chapman = BigWorld.entities.get( chapman.id, None )
		if chapman is None:
			return
		zipInvoiceArray = zip( invoiceIDs, amountList )
		for invoiceID, amount in zipInvoiceArray:
			chapman.sellToCB( memberDBID, invoiceID, amount, self.id )
