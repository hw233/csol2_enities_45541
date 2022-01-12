
# -*- coding: gb18030 -*-
#
# $Id: MerchantFacade.py,v 1.85 2008-08-14 10:23:15 fangpengjun Exp $

"""
商人交易facade

下划线"_"开头的是模块内部方法，不对外使用
"""
import BigWorld
from bwdebug import *
from event.EventCenter import *
from ShoppingBag import *				# get the Buybag and Sellbag class
from ItemsFactory import ObjectItem
import csstatus
import Function
import csdefine
import csconst
import math
import csarithmetic as arithmetic
import config.client.labels.GUIFacade as lbDatas
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import g_newLine
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from guis.tooluis.richtext_plugins.PL_Align import PL_Align
from guis.general.buyconfirmbox.BuyConfirmBox import BuyConfirmBox
from ItemSystemExp import EquipQualityExp
import Language
import utils

g_midAlign = PL_Align.getSource( lineFlat = "M")

class MerchantFacade:
	@staticmethod
	def reset():
		MerchantFacade.chapman = None							# 当前与哪个商人NPC交易
		MerchantFacade.invoices = []							# 商人商品列表；value is instance of InvoiceDataType
		MerchantFacade.itembag = []								# 购物车商品列表
		MerchantFacade.redeemItems = []							# 赎回物品列表
		MerchantFacade.repairType = csdefine.EQUIP_REPAIR_NORMAL
		MerchantFacade.invoiceAmount = 0

def priceCarry( price ):
	"""
	2008-11-4 11:42 yk
	策划规则是：如果价钱小于1，就算1
	如果大于1，则取整
	"""
	if price < 1:
		return 1
	return int( price )

def getInvoiceAmountByUid( uid ):
	"""
	获取某件物品的剩余数量
	@param	uid:	货物的唯一ID
	@return:	UINT16
	"""
	for invoice in MerchantFacade.invoices:
		if invoice.uid == uid:
			return invoice.currAmount
		elif invoice.getSrcItem().uid == uid: # 有些不是全部显示商品配置中商品的NPC交易只能传baseItem.uid
			return invoice.currAmount
	return -1

def updateInvoiceAmount( uid, currAmount ):
	"""
	设置某件物品的剩余数量
	"""
	for invoice in MerchantFacade.invoices:
		if invoice.uid == uid:
			srcItem = invoice.getSrcItem()
			srcItem.setAmount( currAmount )
			invoice.setAmount( currAmount )
			newItemInfo = ObjectItem( srcItem )
			newItemInfo.update( srcItem )
			tradeObject = MerchantFacade.chapman.__class__.__name__
			if tradeObject == "DarkTrader":
				fireEvent( "EVT_ON_DARK_TRADER_RECEIVE_GOODS_INFO_CHANGE", uid, newItemInfo )
			elif tradeObject == "DarkMerchant":
				fireEvent( "EVT_ON_DARK_MERCHANT_RECEIVE_GOODS_INFO_CHANGE", uid, newItemInfo )
			elif tradeObject == "Merchant":
				fireEvent( "EVT_ON_MERCHANT_RECEIVE_GOODS_INFO_CHANGE", uid, newItemInfo )
			elif tradeObject == "TongChapman": # 帮会商人和普通商人没有分开，所以要传NPC名字加以区别
				uid = invoice.getSrcItem().uid
				fireEvent( "EVT_ON_TONG_CHAPMAN_RECEIVE_GOODS_INFO_CHANGE", uid, newItemInfo, tradeObject )
			elif  tradeObject == "TongSpecialChapman":
				fireEvent( "EVT_ON_TONG_SEPCIAL_ITEM_AMOUNT_CHANGED", uid, newItemInfo, tradeObject )

def setInvoiceAmount( amount ):
	"""
	商品数量设置
	"""
	MerchantFacade.invoiceAmount = amount

def getTotalInvoicesAmount():
	"""
	获取所有商品的总数
	"""
	return len( MerchantFacade.invoices )

def getSpecialInvoiceAmount( type ):
	"""
	获取跑商商品剩余数量大于零的个数
	"""
	amount = 0
	for invoice in MerchantFacade.invoices:
		if invoice.itemType == type and invoice.getAmount() > 0:
			amount += 1
	return amount

def getInvoiceAmount( type ):
	"""
	获相同类型取商品数量
	"""
	sameInvoices = []
	for invoice in MerchantFacade.invoices:
		if invoice.itemType == type:
			sameInvoices.append( invoice )
	return len( sameInvoices )
# ------------------------------->
# 用于让底层调用
# ------------------------------->
def onTradeWithNPC( chapman ):
	"""
	开始交易，这个消息通常是用于显示交易窗口

	@param chapman: Entity for trade
	"""
	if chapman is None:
		return
	MerchantFacade.chapman = chapman
	fireEvent( "EVT_ON_TOGGLE_KITBAG", True )
	fireEvent( "EVT_ON_ROLE_MONEY_CHANGED", 0, BigWorld.player().money )
	fireEvent( "EVT_ON_TRADE_WITH_NPC", chapman )


def onTradeWithMerchant( merchant ):
	"""
	开始与特产商交易，这个消息通常是用于显示交易窗口

	@param chapman: Entity for trade
	"""
	if merchant is None:
		return
	MerchantFacade.chapman = merchant
	fireEvent( "EVT_ON_TOGGLE_KITBAG", True )
	fireEvent( "EVT_ON_TRADE_WITH_MERCHANT", merchant )

def onTradeWithDarkMerchant( darkMerchant ):
	"""
	开始与投机商人交易，这个消息通常是用于显示交易窗口
	"""
	if darkMerchant is None:
		return
	MerchantFacade.chapman = darkMerchant
	fireEvent( "EVT_ON_TOGGLE_KITBAG", True )
	fireEvent( "EVT_ON_TRADE_WITH_DARK_MERCHANT", darkMerchant )

def onTradeWithDarkTrader( darkTrader ):
	"""
	开始与投机商人交易，这个消息通常是用于显示交易窗口

	@param chapman: Entity for trade
	"""
	if darkTrader is None:
		return
	MerchantFacade.chapman = darkTrader
	fireEvent( "EVT_ON_TOGGLE_KITBAG", True )
	fireEvent( "EVT_ON_TRADE_WITH_DARK_TRADER", darkTrader )

def onTradeWithItemChapman( chapman ):
	"""
	开始与特殊商人交易，这个消息通常是用于显示交易窗口
	特殊商人指的是用物品买东西，而不是用钱买
	比如玩家用在海滩上钓的鱼换取纪念品
	@param chapman: Entity for trade
	"""
	if chapman is None:
		return
	MerchantFacade.chapman = chapman
	fireEvent( "EVT_ON_TOGGLE_KITBAG", True )
	fireEvent( "EVT_ON_TRADE_WITH_ITEM_TRADER", chapman )

def onTradeWithPointChapman( chapman ):
	"""
	使用积分换东西，这个消息通常是用于显示交易窗口
	@param chapman: Entity for trade
	"""
	if chapman is None:
		return
	MerchantFacade.chapman = chapman
	fireEvent( "EVT_ON_TOGGLE_KITBAG", True )
	fireEvent( "EVT_ON_TRADE_WITH_POINT_TRADER", chapman )

def onTradeWithYXLMEquipChapman( chapman ):
	"""
	英雄联盟装备交易
	"""
	if chapman is None:
		return
	MerchantFacade.chapman = chapman
	fireEvent( "EVT_ON_LOLCOPY_TRADE_WND_SHOW", chapman )

def onTradeWithTongSpecialChapman( chapman ):
	"""
	帮会特殊商人交易
	"""
	if chapman is None:
		return
	MerchantFacade.chapman = chapman
	fireEvent( "EVT_ON_TRADE_WITH_TONG_SPECIAL_CHAPMAN", chapman )

def onTradeWithNPCOver():
	"""
	与NPC交易结束；
	暂时现在什么事都不做，也不产生消息
	"""
	pass

def setRepairType( type ):
	"""
	设置修理模式
	"""
	MerchantFacade.repairType = type

def getRepairType():
	"""
	获取修理模式
	"""
	return MerchantFacade.repairType

def onResetInvoices( space ):
	"""
	清空商品列表
	"""
	MerchantFacade.invoices = []
	MerchantFacade.invoiceSpaces = space
	fireEvent( "EVT_ON_INVOICES_BAG_SPACE_CHANGED", space )

def onInvoiceAdded( chapManID, invoice ):
	"""
	新增一个商品
	@param chapManID: 交易 NPC ID					（增加该参数主要是为了解决，很快地连续与两个 NPC 交流时，
													  前一个 NPC 的商品列表还在请求中，从而冲掉后一个 NPC 的商品列表的问题。hyw--2008.09.16）
	@param invoice: instance of InvoiceDataType
	"""
	if BigWorld.player().getTradeNPCID() != chapManID :		# 如果添加的商品不是当前对话的 NPC
		return												# 则，说明更改交易 NPC 了，因此返回( hyw -- 2008.09.16 )
	chapman = _getChapman()
	tradeObject = chapman.__class__.__name__

	if tradeObject == "TongChapman": # 是帮会商人的话就设置商品的剩余数量
		invoice.setAmount( invoice.getAmount() )
	# srcOrder, name, price, icon, description
	invoices = _getInvoices()
	invoices.append( invoice )
	srcItem = invoice.getSrcItem()
	itemInfo = ObjectItem( srcItem )
	itemInfo.update( srcItem )

	if tradeObject == "Chapman" or tradeObject == "EidolonNPC" or \
	tradeObject == "TongChapman":
		fireEvent( "EVT_ON_INVOICES_BAG_INFO_CHANGED", len( invoices ) - 1, itemInfo, tradeObject )
	elif tradeObject == "DarkTrader":
		fireEvent( "EVT_ON_DARKTRADER_BAG_INFO_CHANGED", len( invoices ) - 1, itemInfo )
	elif tradeObject == "DarkMerchant":
		fireEvent( "EVT_ON_DARK_MERCHANT_BAG_INFO_CHANGED", len( invoices ) - 1, itemInfo )
	elif tradeObject == "Merchant":
		fireEvent( "EVT_ON_SPECIAL_BAG_INFO_CHANGED", len( invoices ) - 1, itemInfo )
	elif tradeObject == "ItemChapman":
		fireEvent( "EVT_ON_ITEM_CHAPMAN_BAG_INFO_CHANGED", len( invoices ) - 1, itemInfo )
	elif tradeObject == "PointChapman":
		fireEvent( "EVT_ON_POINT_CHAPMAN_BAG_INFO_CHANGED", len( invoices ) - 1, itemInfo )
	elif tradeObject == "YXLMEquipChapman":
		fireEvent( "EVT_ON_YXLM_EQUIP_INFO_CHANGED", len( invoices ) - 1, itemInfo )
	elif tradeObject == "TongSpecialChapman":
		fireEvent( "EVT_ON_TONG_SEPCIAL_ITEM_ADDED",  invoice.uid, itemInfo, tradeObject )

def getRedeemItems():
	"""
	被gui\general\TradeWindow的__onShowRedeemPanel调用
	"""
	if not MerchantFacade.redeemItems:
		DEBUG_MSG( "可赎回列表空。" )
		return []
	redeemItems = []
	for item in MerchantFacade.redeemItems:
		uid = item.getUid()
		itemInfo = ObjectItem( item )
		itemInfo.update( item )
		redeemItems.append( itemInfo )
	return  redeemItems

def onSellToNPCReply( state ):
	"""
	物品出售服务器回调

	@param state: 回收状态，1 = 成功， 0 = 失败
	@type  state: UINT8
	@return: 无
	"""
	#if not state:
	#	BigWorld.player().statusMessage( csstatus.NPC_TRADE_SELL_FAILED )
	changeToSell()

# ------------------------------->
# business about
# ------------------------------->
def _getChapman():
	return MerchantFacade.chapman

def _getInvoices():
	return MerchantFacade.invoices

def _getPlayerInvoices():
	return MerchantFacade.redeemItems

def getInvoice( order ):
	"""
	取得某个商品
	"""
	invoices = _getInvoices()
	if order < 0 or order >= len( invoices ):
		return
	return invoices[order]

def calcCastellanPriceRebate( money ):
	"""
	计算NPC所在城市的城市主人(当某帮会占领的该城市后)的购物打折
	"""
	if BigWorld.player().tong_dbID > 0 and BigWorld.player().tong_holdCity == BigWorld.player().getSpaceLabel():
		return money * 0.9
	return money

def getInvoiceItemDescription( order ):
	"""
	取得某个商品的描述
	"""
	invoices = _getInvoices()
	if order < 0 or order >= len( invoices ):
		return ""
	return invoices[order].getDescription( _getChapman() )

def getDarkMerchantInvoiceDescription( order ):
	"""
	获取黑市商人物品描述
	"""
	return getMerchantItemDescription( order )

def getTongSpecialDescription( uid ):
	"""
	获取帮会商品描述
	"""
	invoices = _getInvoices()
	for invoice in invoices:
		if invoice.uid == uid:
			return invoice.getDescription( _getChapman() )
	return ""

def getMerchantItemDescription( order ):
	"""
	取得某个商品的描述
	"""
	section = Language.openConfigSection( "config/ItemYinpiaoValue.xml" )
	label = BigWorld.getSpaceDataFirstForKey( BigWorld.player().spaceID, csconst.SPACE_SPACEDATA_KEY )

	invoices = _getInvoices()
	if order < 0 or order >= len( invoices ):
		return ""
	itemInstance = invoices[order].getSrcItem()				#获取继承与cItemBase的道具实例
	des = itemInstance.description( BigWorld.player() )			#获取道具的原来的描述
	#yinpiao = itemInstance.reqYinpiao() * itemInstance.getAmount()

	msg = lbDatas.PRICE_PRODUCINGAREA % ( itemInstance.reqYinpiao() ) + PL_Image.getSource( "guis/general/specialMerchantWnd/silver.gui" )
	if itemInstance.getAmount() > 1:
		msg += g_newLine + lbDatas.TOTALPRICE_PRODUCINGAREA % ( itemInstance.reqYinpiao() * itemInstance.getAmount() ) \
			+ PL_Image.getSource( "guis/general/specialMerchantWnd/silver.gui" )

	if section[str(itemInstance.id)].readInt( label ) != 0:
		msg += g_newLine + lbDatas.PRICE_LOCAL % ( section[str(itemInstance.id)].readInt( label ) ) \
			+ PL_Image.getSource( "guis/general/specialMerchantWnd/silver.gui" )
		if itemInstance.getAmount() > 1:
			msg += g_newLine + lbDatas.TOTALPRICE_LOCAL % ( section[str(itemInstance.id)].readInt( label ) * itemInstance.getAmount() ) \
				+ PL_Image.getSource( "guis/general/specialMerchantWnd/silver.gui" )
	else:
		msg += g_newLine + lbDatas.NOMERCHANTLOCAL
	if len( msg ) > 0:
		msg = g_midAlign + PL_Font.getSource( msg, fc = ( 0, 255, 0 ) )
		des.append( msg )
	return des

def getInvoiceItemPrice( order ):
	invoices = _getInvoices()
	if order < 0 or order >= len( invoices ):
		return
	priceList = invoices[order].getPrice( _getChapman() )
	for priceType, price in priceList:
		if priceType == csdefine.INVOICE_NEED_MONEY:	# 目前只有钱物交换、气运值换物的商人会使用此接口
			return price
	return 0

def getInvoiceItemAccum( order ):
	"""
	获取商品所需气运值
	"""
	invoices = _getInvoices()
	if order < 0 or order >= len( invoices ):
		return
	priceList = invoices[order].priceInstanceList
	accum = 0
	for priceItem in priceList:
		if priceItem.priceType == csdefine.INVOICE_NEED_SOUL_COIN:
			accum += priceItem.accumPoint
	return accum

def getInvoiceItemYinpiao( order ):
	invoices = _getInvoices()
	if order < 0 or order >= len( invoices ):
		return
	itemInstance = invoices[order].getSrcItem()
	reqYinpiao = itemInstance.reqYinpiao()
	return reqYinpiao

def getDarkMerchantInvoicePrice( order ):
	"""
	获取黑市商人物品描述
	"""
	price = -1
	invoices = _getInvoices()
	if order < 0 or order >= len( invoices ):
		return price

	itemInstance = invoices[order].getSrcItem()
	price = _getDarkMerchantGoodsPrice( itemInstance.id )
	return price

def _getDarkMerchantGoodsPrice( goodsID ) :		# 黑市商人卖的货物和特产商是一样的，但用的是金币而不是银票
	price = -1
	section = Language.openConfigSection( "config/ItemYinpiaoValue.xml" )
	try:
		price = section[str( goodsID )].readInt( 'DarkMerchant' )
	except AttributeError, err:
		ERROR_MSG( "AttributeError: %s" % err )
	return price

def getInvoicePriceDescription( order ):
	"""
	获取用商品的价格描述信息

	rType: array of STRING
	"""
	invoices = _getInvoices()
	if order < 0 or order >= len( invoices ):
		return []
	return invoices[order].getPriceDescriptions( _getChapman() )

def getPriceItem( invOrder, priceIndex ):
	"""
	获取用商品所需兑换物品
	"""
	invoices = _getInvoices()
	if invOrder < 0 or invOrder >= len( invoices ):
		return None
	priceItems = invoices[invOrder].priceInstanceList
	if priceIndex >= len( priceItems ):
		return None
	return priceItems[priceIndex]

def getPlayerInvoiceItemDescription( uid ):
	itembagRef = _getPlayerInvoices()
	des = ""
	for item in itembagRef:
		if item.getUid() == uid:
			des = item.description( BigWorld.player() )
			money = item.getRecodePrice()
			if money > 0:
				priceStr = utils.currencyToViewText( money )
				priceStr = lbDatas.PRICE_BUY + priceStr
				priceStr = g_midAlign + PL_Font.getSource( priceStr, fc = ( 0, 255, 0 ) )
				des.append( g_newLine + priceStr )
	return des

def getTongSpecialItemPrice( uid ):
	invoices = _getInvoices()
	for invoice in invoices:
		if invoice.uid == uid:
			return invoice.getPriceDescriptions( _getChapman() )
	return ""

def getItemPrice( item ):
	price = item.getPrice()
	return price

def buyFromNPC( srcIndex,amounts ):
	"""
	buy invoices from chapman.
	"""
	invoices = _getInvoices()
	invoice = invoices[srcIndex[0]]
	srcItem = invoice.getSrcItem().copy()
	player = BigWorld.player()
	chapman = _getChapman()
	if chapman is None:
		return
	if player.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
		player.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
		return

	costMoney = 0;
	costContr = 0 # 帮会贡献度
	amount = amounts[ 0 ]
	if chapman.__class__.__name__ == "DarkMerchant" :
		costMoney = _getDarkMerchantGoodsPrice( srcItem.id ) * amount
		if player.money < costMoney :
			player.statusMessage( csstatus.NPC_TRADE_NOT_ENOUGH_MONEY )
			return
	else:
		status = invoice.checkRequire( chapman, amount )
		if status != csstatus.NPC_TRADE_CAN_BUY:
			player.statusMessage( status )
			return

		for priceType, price in invoice.getPrice( chapman ):
			if priceType == csdefine.INVOICE_NEED_MONEY:
				costMoney = amount * price
			if priceType == csdefine.INVOICE_NEED_TONG_CONTRIBUTE:
				costContr = amount * price

	# 整理需要的内容
	srcOrders = []
	itemList = []

	# 如果购买的商品多于可叠加上限，那么拆分商品
	stacknum = srcItem.getStackable()
	if amounts[ 0 ] > stacknum:
		temp = amounts[ 0 ]
		amounts = []
		leftAmount = temp % stacknum
		if 0 < leftAmount < stacknum:	# 如果不是可叠加数量得整数倍
			srcItem.setAmount( leftAmount )
			itemList.append( srcItem )
			srcOrders.append( invoice.uid )
			amounts.append( leftAmount )
			temp -= leftAmount
		while temp > 0:
			tempItem = srcItem.copy()
			tempItem.setAmount( stacknum )
			itemList.append( tempItem )
			srcOrders.append( invoice.uid )
			amounts.append( stacknum )
			temp -= stacknum
	else:
		srcItem.setAmount( amounts[ 0 ] )
		itemList.append( srcItem )
		srcOrders.append( invoice.uid )

	if len( srcOrders ) == 0:
		player.statusMessage( csstatus.NPC_TRADE_CHOICEN_WARE )
		return

	status = player.checkItemsPlaceIntoNK_( itemList )
	if status == csdefine.KITBAG_NO_MORE_SPACE:
		player.statusMessage( csstatus.NPC_TRADE_KITBAG_NEED_SPACE )
		return
	if status == csdefine.KITBAG_ITEM_COUNT_LIMIT:
		player.statusMessage( csstatus.NPC_TRADE_ITEM_LIMIT_COUNT )
		return

	# 向服务器请求开买
	msg = ""
	def confirmToBuy( result ) :
		if result :
			chapman.cell.sellArrayTo( srcOrders, amounts )		# see also Chapman.def
	if costMoney > 0:
		if costMoney / 10000 >= 1 :											# 本次购买花费超过1金
			costString = PL_Font.getSource( utils.currencyToViewText( costMoney ), fc = ( 16, 197, 165, 255 ) )
			amountStr = PL_Font.getSource( str( amount ), fc = ( 255,0,0, 255 ) )
			msg = lbDatas.BUYCONFIRM_NORMAL % ( costString, amountStr, srcItem.name() )
			BuyConfirmBox.instance().showConfirmBox( msg, chapman, confirmToBuy )
		else:
			chapman.cell.sellArrayTo( srcOrders, amounts )		# see also Chapman.def
	elif costContr > 0:
		msg = lbDatas.BUYCONFIRM_TONG %( costContr, amount, srcItem.name() )
		BuyConfirmBox.instance().showConfirmBox(msg, chapman, confirmToBuy )
	else:
		chapman.cell.sellArrayTo( srcOrders, amounts )

def buyFromMerchant( srcIndex,amounts ):
	"""
	buy invoices from merchant.
	"""
	invoices = _getInvoices()
	invoice = invoices[srcIndex[0]]
	srcItem = invoice.getSrcItem().copy()
	player = BigWorld.player()

	if player.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
		player.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
		return

	if player.money < srcItem.reqYinpiao() * amounts[ 0 ]:
		player.statusMessage( csstatus.NPC_TRADE_NOT_ENOUGH_MONEY )
		return

	#if stacknum == 1:
	#	amounts[0] = stacknum

	merchant = _getChapman()
	if merchant is None:
		return

	# 整理需要的内容
	srcOrders = []
	itemList = []

	# 如果购买的商品多于可叠加上限，那么拆分商品
	stacknum = srcItem.getStackable()
	if amounts[ 0 ] > stacknum:
		temp = amounts[ 0 ]
		amounts = []
		tempAmount = temp % stacknum
		if 0 < tempAmount < stacknum:	# 如果不是可叠加数量得整数倍
			srcItem.setAmount( tempAmount )
			itemList.append( srcItem )
			srcOrders.append( invoice.uid )
			amounts.append( tempAmount )
			temp -= tempAmount
		while temp > 0:
			tempItem = srcItem.copy()
			tempItem.setAmount( stacknum )
			itemList.append( tempItem )
			srcOrders.append( invoice.uid )
			amounts.append( stacknum )
			temp -= stacknum
	else:
		srcItem.setAmount( amounts[0] )
		itemList.append( srcItem )
		srcOrders.append( invoice.uid )

	if len( srcOrders ) == 0:
		player.statusMessage( csstatus.NPC_TRADE_CHOICEN_WARE )
		return

	status = player.checkItemsPlaceIntoNK_( itemList )
	if status == csdefine.KITBAG_NO_MORE_SPACE:
		player.statusMessage( csstatus.NPC_TRADE_KITBAG_NEED_SPACE )
		return
	if status == csdefine.KITBAG_ITEM_COUNT_LIMIT:
		player.statusMessage( csstatus.NPC_TRADE_ITEM_LIMIT_COUNT )
		return

	# 向服务器请求开买
	merchant.cell.sellArrayTo( srcOrders, amounts )		# see also Chapman.def

def buyYXLMEquipFromNPC( invoiceIndex, amount=1 ):
	"""
	从英雄联盟副本的NPC处购买副本专用装备
	"""
	player = BigWorld.player()
	# 判断是否能跟NPC对话 完成操作
	if player.actionSign( csdefine.ACTION_FORBID_TALK ):
		player.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
		return

	# 判断货币是否足够
	chapman = _getChapman()
	invoice = _getInvoices()[invoiceIndex]
	status = invoice.checkRequire( chapman, amount )
	if status != csstatus.NPC_TRADE_CAN_BUY:
		player.statusMessage( status )
		return
	chapman.cell.sellTo( invoice.uid, amount )

def tradeOverWithNPC():
	"""
	与NPC交易结束
	"""
	player = BigWorld.player()
	if not player.isPlayer(): return

#	for index in xrange( 13 ):
	fireEvent( "EVT_ON_INVOICES_BAG_INFO_CHANGED",0, None )
	player.leaveTradeWithNPC()

def endTradeWithNPC():
	"""
	结束与NPC交易，一般调用于玩家状态行为控制限制
	"""
	fireEvent( "EVT_ON_ROLE_END_WITHNPC_TRADE")
	fireEvent( "EVT_ON_TOGGLE_KITBAG", False )
#----------------------------------------------------------------------------------------------
# SELL
#----------------------------------------------------------------------------------------------

def changeToBuy():
	"""
	转到购买界面
	"""
	pass

def changeToSell():
	"""
	转到出售界面::
		- 通知商品数量
		- 通知每个位置的商品信息
	"""
	pass

def getSellItemPrice( uid ):#get a sell item price
	"""
	get price of all invoices
	"""
	# 对要赎回来的物品而言。价格总是服务器给定好了的
	# 所以直接读取价格数据就行了，而不应该去读取客户端的 getPrice()
	itemPrice = 0
	for item in _getPlayerInvoices():
		if item.getUid() == uid:
			itemPrice = item.getRecodePrice()
			break
	return itemPrice

def getSellItemsPrice( ):
	redeemItems = _getPlayerInvoices()
	prices = 0
	for redeemItem in redeemItems :
		prices += redeemItem.getPrice()
	return prices

def sellArrayToNPC( uids, amounts ):
	"""
	卖很多物品
	"""
	player = BigWorld.player()

	if player.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
		player.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
		return
	if player.ifMoneyMax():			#如果玩家身上金钱携带量已经超过上限 那么退出
		player.statusMessage( csstatus.CIB_MSG_MONEY_OVERFLOW )
		return
	if player.testAddMoney( getSellItemsPrice() ) > 0:		#如果此次操作会造成金钱超出上限 那么退出
		player.statusMessage( csstatus.CIB_MONEY_OVERFLOW )
		return

	chapman = _getChapman()
	if chapman is None:
		return
	if chapman.__class__.__name__ == "ItemChapman" or chapman.__class__.__name__ == "PointChapman":
		player.statusMessage( csstatus.NPC_CANNOT_SELL )
		return

	# 整理需要的内容
	srcUids = []
	for uid in uids:
		invoice = player.getItemByUid_( uid )
		if invoice is None: continue
		if not invoice.canSell(): continue
		if invoice.getAmount() <= 0: continue
		srcUids.append( uid )

	if len( srcUids ) != len( amounts ): # 如果长度不一样，表示有意外发生，中断操作。
		BigWorld.player().statusMessage( csstatus.NPC_TRADE_SELL_FAILED )
		return
	# 向服务器请求开卖
	chapman.cell.buyArrayFrom( srcUids, amounts )		# see also Chapman.def

def sellToNPC( uid, amount ):
	"""
	卖单个物品
	"""
	player = BigWorld.player()

	if player.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
		player.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
		return
	if player.ifMoneyMax():			#如果玩家身上金钱携带量已经超过上限 那么退出
		player.statusMessage( csstatus.CIB_MSG_MONEY_OVERFLOW )
		return
	if player.testAddMoney( getSellItemsPrice() ) > 0:		#如果此次操作会造成金钱超出上限 那么退出
		player.statusMessage( csstatus.CIB_MONEY_OVERFLOW )
		return

	chapman = _getChapman()
	if chapman is None:
		return
	if chapman.__class__.__name__ == "ItemChapman" or chapman.__class__.__name__ == "PointChapman":
		player.statusMessage( csstatus.NPC_CANNOT_SELL )
		return

	invoice = player.getItemByUid_( uid )
	if invoice is None: return

	if not invoice.canSell() and chapman.__class__.__name__ not in ["DarkMerchant", "DarkTrader", "Merchant"]:
		player.statusMessage( csstatus.NPC_TRADE_ITEM_NOT_SELL )
		return

	if invoice.getAmount() < amount:
		player.statusMessage( csstatus.NPC_TRADE_NOT_ENOUGH_WARE )
		return

	# 向服务器请求开卖
	chapman.cell.buyFrom( uid, amount )		# see also Chapman.def

# -----------------------------------------------------------------------------------------------------------
# 修理

# 内部函数
def calcuRepairEquipMoney( equip, repairType ):
	"""
	计算修理一个装备的价格
	@param    equip: 装备数据
	@type     equip: instance
	@param    repairType: 修理类型
	@type     repairType: UNIT8
	@return: 价格
	"""
	# 普通修理的修理费比率为 1
	if not equip.getHardinessLimit(): #戒指没有耐久度，这样是为了防止修理戒指时出错
		return 0
	if repairType == csdefine.EQUIP_REPAIR_NORMAL:
		repairCostRate = 1
	# 特殊修理的修理费比率为 3
	elif repairType == csdefine.EQUIP_REPAIR_SPECIAL:
		repairCostRate = 1.5
	else:
		assert "That is a Error!!!, use undefine repair type "
	repairRate = EquipQualityExp.instance().getRepairRateByQuality( equip.getQuality() )
	# 修理费用 = 品质系数*（1-（实际耐久度/原始最大耐久度））*道具价格 ，用去掉小数＋1的方法取整。
	repairMoney = repairRate * ( 1- float( equip.getHardiness() ) / float( equip.getHardinessLimit() ) ) * equip.getRecodePrice() * repairCostRate
	player = BigWorld.player()
	if player.tong_holdCity == BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_KEY ):
		repairMoney *= 0.9
	repairMoney = int( math.ceil( repairMoney ) )

	return repairMoney

def _getAllRepairEquip():
	"""
	返回所有背包里可修理的装备
	@return   无
	"""
	repairEquips = []
	for item in BigWorld.player().getAllItems():
		if item.isEquip():
			if item.query( "eq_hardiness" ) == item.query( "eq_hardinessLimit" ):
				continue
			repairEquips.append( item )
	return repairEquips

def calcuOneRepairPrice( equip, repairType ) :
	"""
	计算修理一件装备的费用
	"""
	# 判断是否在帮会冶炼师处修理装备，处理费用打折。但这里不会判断这个冶炼师是否是本帮会的冶炼师，
	# 因为能和帮会冶炼师对话，说明玩家就是在本帮会领地内进行的操作。
	repairMoney = calcuRepairEquipMoney( equip, repairType )
	chapman = _getChapman()
	player = BigWorld.player()
	des = ""
	if chapman is not None and \
	chapman.__class__.__name__ == "TongChapman" :
		repairMoney = int( math.ceil( repairMoney * csconst.TONG_TJP_REBATE[ player.tong_buildDatas[csdefine.TONG_BUILDING_TYPE_TJP]["level"]] ) )
	if repairMoney > 0:
		if des : des += g_newLine
		des += g_midAlign
		moneyText = utils.currencyToViewText( repairMoney )
		if repairType == csdefine.EQUIP_REPAIR_NORMAL:
			des += lbDatas.COMM_REPAIR_COSTMONEY%moneyText
		else:
			des += lbDatas.SPEC_REPAIR_COSTMONEY%moneyText

	if chapman.isJoinRevenue == True and player.tong_holdCity != player.getSpaceLabel():
		try:
			revenueRate = int(BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_CITY_REVENUE )) / 100.0
		except:
			revenueRate = 0.0

		revenue = int( repairMoney * revenueRate )
		if des : des += g_newLine
		des += g_midAlign
		des += lbDatas.REPAIR_NEEDTAX + utils.currencyToViewText( revenue )

	return des

def calcuAllRepairPrice( repairType ):
	"""
	返回修理全部物品的价格
	@param invoices: 要计算的物品
	@type  invoices: list
	@param chapman: NPC
	@type  chapman: instance
	"""
	player = BigWorld.player()
	repairMoney = 0
	des = ""
	for equip in _getAllRepairEquip():
		repairMoney += calcuRepairEquipMoney( equip, repairType )
	chapman = _getChapman()
	if chapman is not None and \
	chapman.__class__.__name__ == "TongChapman" :
		repairMoney = int( math.ceil( repairMoney * csconst.TONG_TJP_REBATE[ player.tong_buildDatas[csdefine.TONG_BUILDING_TYPE_TJP]["level"]] ) )
	if repairMoney > 0:
		if des : des += g_newLine
		des += g_midAlign
		moneyText = utils.currencyToViewText( repairMoney )
		if repairType == csdefine.EQUIP_REPAIR_NORMAL:
			des += lbDatas.COMM_REPAIR_COSTMONEY%moneyText
		else:
			des += lbDatas.SPEC_REPAIR_COSTMONEY%moneyText

	if chapman and chapman.isJoinRevenue == True and player.tong_holdCity != player.getSpaceLabel():
		try:
			revenueRate = int(BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_CITY_REVENUE )) / 100.0
		except:
			revenueRate = 0.0

		revenue = int( repairMoney * revenueRate )
		if des : des += g_newLine
		des += g_midAlign
		des += lbDatas.REPAIR_NEEDTAX + utils.currencyToViewText( revenue )
	return des

def repairOneEquip( repairType, kitBagID, orderID ):
	"""
	修理一个装备
	@param    repairType: 修理类型
	@type     repairType: UINT8
	@param    kitBagID: 回收价格比
	@type     kitBagID: float
	@param    orderID: 回收价格比
	@type     orderID: float
	@return   无
	"""
	# 取得所要买的商品
	player = BigWorld.player()
	if player.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
		player.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
		return
	chapman = _getChapman()
	if chapman is None:
		ERROR_MSG("chapman not find!")
		return
	index = kitBagID * csdefine.KB_MAX_SPACE + orderID
	chapman.cell.repairOneEquip(  kitBagID, index, repairType )

def repairAllEquip( repairType ):
	"""
	修理所有背包里的装备
	"""
	# 取得所要买的商品
	player = BigWorld.player()
	if player.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
		player.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
		return
	chapman = _getChapman()
	if chapman is None:
		ERROR_MSG("chapman not find!")
		return
	if len( _getAllRepairEquip() ) == 0:
		print "No Equip need Repair"
		return
	chapman.cell.repairAllEquip( repairType )

def getInvoices( ):
	return _getInvoices()

def getChapMan():
	return _getChapman()

def getPlayerInvoices():
	return _getPlayerInvoices()

def reqInvoceAmount( merchant ):
	if merchant is None:return
	for invoice in MerchantFacade.invoices:
		if invoice.currAmount != invoice.maxAmount:
			merchant.cell.reqInvoiceAmount( invoice.uid )

# -------------------------------------------------------------------------------
# 买卖商品赎回功能接口
# -------------------------------------------------------------------------------
def redeemItem( uid ):
	"""
	赎回物品的接口，玩家使用此客户端接口向服务器发送赎回物品的请求

	param uid:	物品的唯一标识
	type uid :	INT64
	"""
	chapman = _getChapman()
	if chapman is None:
		ERROR_MSG( "找不到商人npc。" )
		return
	player = BigWorld.player()
	if player.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
		player.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
		return
	player.cell.redeemItem( uid, chapman.id )


def onDelRedeemItem( uid ): #服务器回调
	"""
	回购一个可赎回物品成功的更新函数

	param uid:	物品的唯一标识
	type uid :	INT64
	"""
	if MerchantFacade.redeemItems == []:
		ERROR_MSG( "可赎回物品列表数据出错." )
		fireEvent( "EVT_ON_REDEEM_UPDATE_LAST_SELLED", len( MerchantFacade.redeemItems ) - 1, None )
		return
	for item in MerchantFacade.redeemItems:
		if item.getUid() == uid:
			index = MerchantFacade.redeemItems.index( item )
			MerchantFacade.redeemItems.remove( item )
			fireEvent( "EVT_ON_REDEEM_REEDEM_ITEM", uid, None  )
			if len( MerchantFacade.redeemItems ) != 0 :
				tempInfo = ObjectItem( MerchantFacade.redeemItems[-1] )
				tempInfo.update( MerchantFacade.redeemItems[-1] )
				fireEvent( "EVT_ON_REDEEM_UPDATE_LAST_SELLED", len( MerchantFacade.redeemItems ) - 1, tempInfo )
			else:
				fireEvent( "EVT_ON_REDEEM_UPDATE_LAST_SELLED", -1, None )



def updateLastSellItem( ):
	if MerchantFacade.redeemItems == []:
		fireEvent( "EVT_ON_REDEEM_UPDATE_LAST_SELLED", len( MerchantFacade.redeemItems ) - 1, None )
		return
#	index = len( MerchantFacade.redeemItems ) - 1
	item = MerchantFacade.redeemItems[-1]
	itemInfo = ObjectItem( item )
	itemInfo.update( item )
	fireEvent( "EVT_ON_REDEEM_UPDATE_LAST_SELLED", len( MerchantFacade.redeemItems ) - 1, itemInfo )

def onAddRedeemItem( item ):
	"""
	可赎回物品列表数据变动的更新函数,把cell发过来的数据加入到redeemItems最后一个位置.
	如果redeemItems已有7个物品,则把头一个物品删除,然后加入新的数据

	param item:	新加入可赎回列表的物品
	type item:	ITEM
	"""
	itemInfo = ObjectItem( item )
	itemInfo.update( item )
	uid = itemInfo.uid
	if len( MerchantFacade.redeemItems ) < csconst.REDEEM_ITEM_MAX_COUNT:
		MerchantFacade.redeemItems.append( item )
		index = len( MerchantFacade.redeemItems ) -1
		fireEvent( "EVT_ON_REDEEM_INFO_CHANGED", index, itemInfo )
		fireEvent( "EVT_ON_REDEEM_UPDATE_LAST_SELLED", index, itemInfo )
	else:
		MerchantFacade.redeemItems.pop( 0 )
		MerchantFacade.redeemItems.append( item )
		index = csconst.REDEEM_ITEM_MAX_COUNT -1
		for index, iItem in enumerate( MerchantFacade.redeemItems ):
			tempItemInfo = ObjectItem( iItem )
			tempItemInfo.update( iItem )
			fireEvent( "EVT_ON_REDEEM_INFO_CHANGED", index, tempItemInfo )
		fireEvent( "EVT_ON_REDEEM_UPDATE_LAST_SELLED", index, itemInfo )
