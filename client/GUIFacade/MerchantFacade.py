
# -*- coding: gb18030 -*-
#
# $Id: MerchantFacade.py,v 1.85 2008-08-14 10:23:15 fangpengjun Exp $

"""
���˽���facade

�»���"_"��ͷ����ģ���ڲ�������������ʹ��
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
		MerchantFacade.chapman = None							# ��ǰ���ĸ�����NPC����
		MerchantFacade.invoices = []							# ������Ʒ�б�value is instance of InvoiceDataType
		MerchantFacade.itembag = []								# ���ﳵ��Ʒ�б�
		MerchantFacade.redeemItems = []							# �����Ʒ�б�
		MerchantFacade.repairType = csdefine.EQUIP_REPAIR_NORMAL
		MerchantFacade.invoiceAmount = 0

def priceCarry( price ):
	"""
	2008-11-4 11:42 yk
	�߻������ǣ������ǮС��1������1
	�������1����ȡ��
	"""
	if price < 1:
		return 1
	return int( price )

def getInvoiceAmountByUid( uid ):
	"""
	��ȡĳ����Ʒ��ʣ������
	@param	uid:	�����ΨһID
	@return:	UINT16
	"""
	for invoice in MerchantFacade.invoices:
		if invoice.uid == uid:
			return invoice.currAmount
		elif invoice.getSrcItem().uid == uid: # ��Щ����ȫ����ʾ��Ʒ��������Ʒ��NPC����ֻ�ܴ�baseItem.uid
			return invoice.currAmount
	return -1

def updateInvoiceAmount( uid, currAmount ):
	"""
	����ĳ����Ʒ��ʣ������
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
			elif tradeObject == "TongChapman": # ������˺���ͨ����û�зֿ�������Ҫ��NPC���ּ�������
				uid = invoice.getSrcItem().uid
				fireEvent( "EVT_ON_TONG_CHAPMAN_RECEIVE_GOODS_INFO_CHANGE", uid, newItemInfo, tradeObject )
			elif  tradeObject == "TongSpecialChapman":
				fireEvent( "EVT_ON_TONG_SEPCIAL_ITEM_AMOUNT_CHANGED", uid, newItemInfo, tradeObject )

def setInvoiceAmount( amount ):
	"""
	��Ʒ��������
	"""
	MerchantFacade.invoiceAmount = amount

def getTotalInvoicesAmount():
	"""
	��ȡ������Ʒ������
	"""
	return len( MerchantFacade.invoices )

def getSpecialInvoiceAmount( type ):
	"""
	��ȡ������Ʒʣ������������ĸ���
	"""
	amount = 0
	for invoice in MerchantFacade.invoices:
		if invoice.itemType == type and invoice.getAmount() > 0:
			amount += 1
	return amount

def getInvoiceAmount( type ):
	"""
	����ͬ����ȡ��Ʒ����
	"""
	sameInvoices = []
	for invoice in MerchantFacade.invoices:
		if invoice.itemType == type:
			sameInvoices.append( invoice )
	return len( sameInvoices )
# ------------------------------->
# �����õײ����
# ------------------------------->
def onTradeWithNPC( chapman ):
	"""
	��ʼ���ף������Ϣͨ����������ʾ���״���

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
	��ʼ���ز��̽��ף������Ϣͨ����������ʾ���״���

	@param chapman: Entity for trade
	"""
	if merchant is None:
		return
	MerchantFacade.chapman = merchant
	fireEvent( "EVT_ON_TOGGLE_KITBAG", True )
	fireEvent( "EVT_ON_TRADE_WITH_MERCHANT", merchant )

def onTradeWithDarkMerchant( darkMerchant ):
	"""
	��ʼ��Ͷ�����˽��ף������Ϣͨ����������ʾ���״���
	"""
	if darkMerchant is None:
		return
	MerchantFacade.chapman = darkMerchant
	fireEvent( "EVT_ON_TOGGLE_KITBAG", True )
	fireEvent( "EVT_ON_TRADE_WITH_DARK_MERCHANT", darkMerchant )

def onTradeWithDarkTrader( darkTrader ):
	"""
	��ʼ��Ͷ�����˽��ף������Ϣͨ����������ʾ���״���

	@param chapman: Entity for trade
	"""
	if darkTrader is None:
		return
	MerchantFacade.chapman = darkTrader
	fireEvent( "EVT_ON_TOGGLE_KITBAG", True )
	fireEvent( "EVT_ON_TRADE_WITH_DARK_TRADER", darkTrader )

def onTradeWithItemChapman( chapman ):
	"""
	��ʼ���������˽��ף������Ϣͨ����������ʾ���״���
	��������ָ��������Ʒ��������������Ǯ��
	����������ں�̲�ϵ����㻻ȡ����Ʒ
	@param chapman: Entity for trade
	"""
	if chapman is None:
		return
	MerchantFacade.chapman = chapman
	fireEvent( "EVT_ON_TOGGLE_KITBAG", True )
	fireEvent( "EVT_ON_TRADE_WITH_ITEM_TRADER", chapman )

def onTradeWithPointChapman( chapman ):
	"""
	ʹ�û��ֻ������������Ϣͨ����������ʾ���״���
	@param chapman: Entity for trade
	"""
	if chapman is None:
		return
	MerchantFacade.chapman = chapman
	fireEvent( "EVT_ON_TOGGLE_KITBAG", True )
	fireEvent( "EVT_ON_TRADE_WITH_POINT_TRADER", chapman )

def onTradeWithYXLMEquipChapman( chapman ):
	"""
	Ӣ������װ������
	"""
	if chapman is None:
		return
	MerchantFacade.chapman = chapman
	fireEvent( "EVT_ON_LOLCOPY_TRADE_WND_SHOW", chapman )

def onTradeWithTongSpecialChapman( chapman ):
	"""
	����������˽���
	"""
	if chapman is None:
		return
	MerchantFacade.chapman = chapman
	fireEvent( "EVT_ON_TRADE_WITH_TONG_SPECIAL_CHAPMAN", chapman )

def onTradeWithNPCOver():
	"""
	��NPC���׽�����
	��ʱ����ʲô�¶�������Ҳ��������Ϣ
	"""
	pass

def setRepairType( type ):
	"""
	��������ģʽ
	"""
	MerchantFacade.repairType = type

def getRepairType():
	"""
	��ȡ����ģʽ
	"""
	return MerchantFacade.repairType

def onResetInvoices( space ):
	"""
	�����Ʒ�б�
	"""
	MerchantFacade.invoices = []
	MerchantFacade.invoiceSpaces = space
	fireEvent( "EVT_ON_INVOICES_BAG_SPACE_CHANGED", space )

def onInvoiceAdded( chapManID, invoice ):
	"""
	����һ����Ʒ
	@param chapManID: ���� NPC ID					�����Ӹò�����Ҫ��Ϊ�˽�����ܿ������������ NPC ����ʱ��
													  ǰһ�� NPC ����Ʒ�б��������У��Ӷ������һ�� NPC ����Ʒ�б�����⡣hyw--2008.09.16��
	@param invoice: instance of InvoiceDataType
	"""
	if BigWorld.player().getTradeNPCID() != chapManID :		# �����ӵ���Ʒ���ǵ�ǰ�Ի��� NPC
		return												# ��˵�����Ľ��� NPC �ˣ���˷���( hyw -- 2008.09.16 )
	chapman = _getChapman()
	tradeObject = chapman.__class__.__name__

	if tradeObject == "TongChapman": # �ǰ�����˵Ļ���������Ʒ��ʣ������
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
	��gui\general\TradeWindow��__onShowRedeemPanel����
	"""
	if not MerchantFacade.redeemItems:
		DEBUG_MSG( "������б�ա�" )
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
	��Ʒ���۷������ص�

	@param state: ����״̬��1 = �ɹ��� 0 = ʧ��
	@type  state: UINT8
	@return: ��
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
	ȡ��ĳ����Ʒ
	"""
	invoices = _getInvoices()
	if order < 0 or order >= len( invoices ):
		return
	return invoices[order]

def calcCastellanPriceRebate( money ):
	"""
	����NPC���ڳ��еĳ�������(��ĳ���ռ��ĸó��к�)�Ĺ������
	"""
	if BigWorld.player().tong_dbID > 0 and BigWorld.player().tong_holdCity == BigWorld.player().getSpaceLabel():
		return money * 0.9
	return money

def getInvoiceItemDescription( order ):
	"""
	ȡ��ĳ����Ʒ������
	"""
	invoices = _getInvoices()
	if order < 0 or order >= len( invoices ):
		return ""
	return invoices[order].getDescription( _getChapman() )

def getDarkMerchantInvoiceDescription( order ):
	"""
	��ȡ����������Ʒ����
	"""
	return getMerchantItemDescription( order )

def getTongSpecialDescription( uid ):
	"""
	��ȡ�����Ʒ����
	"""
	invoices = _getInvoices()
	for invoice in invoices:
		if invoice.uid == uid:
			return invoice.getDescription( _getChapman() )
	return ""

def getMerchantItemDescription( order ):
	"""
	ȡ��ĳ����Ʒ������
	"""
	section = Language.openConfigSection( "config/ItemYinpiaoValue.xml" )
	label = BigWorld.getSpaceDataFirstForKey( BigWorld.player().spaceID, csconst.SPACE_SPACEDATA_KEY )

	invoices = _getInvoices()
	if order < 0 or order >= len( invoices ):
		return ""
	itemInstance = invoices[order].getSrcItem()				#��ȡ�̳���cItemBase�ĵ���ʵ��
	des = itemInstance.description( BigWorld.player() )			#��ȡ���ߵ�ԭ��������
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
		if priceType == csdefine.INVOICE_NEED_MONEY:	# Ŀǰֻ��Ǯ�ｻ��������ֵ��������˻�ʹ�ô˽ӿ�
			return price
	return 0

def getInvoiceItemAccum( order ):
	"""
	��ȡ��Ʒ��������ֵ
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
	��ȡ����������Ʒ����
	"""
	price = -1
	invoices = _getInvoices()
	if order < 0 or order >= len( invoices ):
		return price

	itemInstance = invoices[order].getSrcItem()
	price = _getDarkMerchantGoodsPrice( itemInstance.id )
	return price

def _getDarkMerchantGoodsPrice( goodsID ) :		# �����������Ļ�����ز�����һ���ģ����õ��ǽ�Ҷ�������Ʊ
	price = -1
	section = Language.openConfigSection( "config/ItemYinpiaoValue.xml" )
	try:
		price = section[str( goodsID )].readInt( 'DarkMerchant' )
	except AttributeError, err:
		ERROR_MSG( "AttributeError: %s" % err )
	return price

def getInvoicePriceDescription( order ):
	"""
	��ȡ����Ʒ�ļ۸�������Ϣ

	rType: array of STRING
	"""
	invoices = _getInvoices()
	if order < 0 or order >= len( invoices ):
		return []
	return invoices[order].getPriceDescriptions( _getChapman() )

def getPriceItem( invOrder, priceIndex ):
	"""
	��ȡ����Ʒ����һ���Ʒ
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
	if player.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
		player.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
		return

	costMoney = 0;
	costContr = 0 # ��ṱ�׶�
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

	# ������Ҫ������
	srcOrders = []
	itemList = []

	# ����������Ʒ���ڿɵ������ޣ���ô�����Ʒ
	stacknum = srcItem.getStackable()
	if amounts[ 0 ] > stacknum:
		temp = amounts[ 0 ]
		amounts = []
		leftAmount = temp % stacknum
		if 0 < leftAmount < stacknum:	# ������ǿɵ���������������
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

	# �������������
	msg = ""
	def confirmToBuy( result ) :
		if result :
			chapman.cell.sellArrayTo( srcOrders, amounts )		# see also Chapman.def
	if costMoney > 0:
		if costMoney / 10000 >= 1 :											# ���ι��򻨷ѳ���1��
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

	if player.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
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

	# ������Ҫ������
	srcOrders = []
	itemList = []

	# ����������Ʒ���ڿɵ������ޣ���ô�����Ʒ
	stacknum = srcItem.getStackable()
	if amounts[ 0 ] > stacknum:
		temp = amounts[ 0 ]
		amounts = []
		tempAmount = temp % stacknum
		if 0 < tempAmount < stacknum:	# ������ǿɵ���������������
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

	# �������������
	merchant.cell.sellArrayTo( srcOrders, amounts )		# see also Chapman.def

def buyYXLMEquipFromNPC( invoiceIndex, amount=1 ):
	"""
	��Ӣ�����˸�����NPC�����򸱱�ר��װ��
	"""
	player = BigWorld.player()
	# �ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
	if player.actionSign( csdefine.ACTION_FORBID_TALK ):
		player.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
		return

	# �жϻ����Ƿ��㹻
	chapman = _getChapman()
	invoice = _getInvoices()[invoiceIndex]
	status = invoice.checkRequire( chapman, amount )
	if status != csstatus.NPC_TRADE_CAN_BUY:
		player.statusMessage( status )
		return
	chapman.cell.sellTo( invoice.uid, amount )

def tradeOverWithNPC():
	"""
	��NPC���׽���
	"""
	player = BigWorld.player()
	if not player.isPlayer(): return

#	for index in xrange( 13 ):
	fireEvent( "EVT_ON_INVOICES_BAG_INFO_CHANGED",0, None )
	player.leaveTradeWithNPC()

def endTradeWithNPC():
	"""
	������NPC���ף�һ����������״̬��Ϊ��������
	"""
	fireEvent( "EVT_ON_ROLE_END_WITHNPC_TRADE")
	fireEvent( "EVT_ON_TOGGLE_KITBAG", False )
#----------------------------------------------------------------------------------------------
# SELL
#----------------------------------------------------------------------------------------------

def changeToBuy():
	"""
	ת���������
	"""
	pass

def changeToSell():
	"""
	ת�����۽���::
		- ֪ͨ��Ʒ����
		- ֪ͨÿ��λ�õ���Ʒ��Ϣ
	"""
	pass

def getSellItemPrice( uid ):#get a sell item price
	"""
	get price of all invoices
	"""
	# ��Ҫ���������Ʒ���ԡ��۸����Ƿ������������˵�
	# ����ֱ�Ӷ�ȡ�۸����ݾ����ˣ�����Ӧ��ȥ��ȡ�ͻ��˵� getPrice()
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
	���ܶ���Ʒ
	"""
	player = BigWorld.player()

	if player.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
		player.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
		return
	if player.ifMoneyMax():			#���������Ͻ�ǮЯ�����Ѿ��������� ��ô�˳�
		player.statusMessage( csstatus.CIB_MSG_MONEY_OVERFLOW )
		return
	if player.testAddMoney( getSellItemsPrice() ) > 0:		#����˴β�������ɽ�Ǯ�������� ��ô�˳�
		player.statusMessage( csstatus.CIB_MONEY_OVERFLOW )
		return

	chapman = _getChapman()
	if chapman is None:
		return
	if chapman.__class__.__name__ == "ItemChapman" or chapman.__class__.__name__ == "PointChapman":
		player.statusMessage( csstatus.NPC_CANNOT_SELL )
		return

	# ������Ҫ������
	srcUids = []
	for uid in uids:
		invoice = player.getItemByUid_( uid )
		if invoice is None: continue
		if not invoice.canSell(): continue
		if invoice.getAmount() <= 0: continue
		srcUids.append( uid )

	if len( srcUids ) != len( amounts ): # ������Ȳ�һ������ʾ�����ⷢ�����жϲ�����
		BigWorld.player().statusMessage( csstatus.NPC_TRADE_SELL_FAILED )
		return
	# �������������
	chapman.cell.buyArrayFrom( srcUids, amounts )		# see also Chapman.def

def sellToNPC( uid, amount ):
	"""
	��������Ʒ
	"""
	player = BigWorld.player()

	if player.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
		player.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
		return
	if player.ifMoneyMax():			#���������Ͻ�ǮЯ�����Ѿ��������� ��ô�˳�
		player.statusMessage( csstatus.CIB_MSG_MONEY_OVERFLOW )
		return
	if player.testAddMoney( getSellItemsPrice() ) > 0:		#����˴β�������ɽ�Ǯ�������� ��ô�˳�
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

	# �������������
	chapman.cell.buyFrom( uid, amount )		# see also Chapman.def

# -----------------------------------------------------------------------------------------------------------
# ����

# �ڲ�����
def calcuRepairEquipMoney( equip, repairType ):
	"""
	��������һ��װ���ļ۸�
	@param    equip: װ������
	@type     equip: instance
	@param    repairType: ��������
	@type     repairType: UNIT8
	@return: �۸�
	"""
	# ��ͨ���������ѱ���Ϊ 1
	if not equip.getHardinessLimit(): #��ָû���;öȣ�������Ϊ�˷�ֹ�����ָʱ����
		return 0
	if repairType == csdefine.EQUIP_REPAIR_NORMAL:
		repairCostRate = 1
	# �������������ѱ���Ϊ 3
	elif repairType == csdefine.EQUIP_REPAIR_SPECIAL:
		repairCostRate = 1.5
	else:
		assert "That is a Error!!!, use undefine repair type "
	repairRate = EquipQualityExp.instance().getRepairRateByQuality( equip.getQuality() )
	# ������� = Ʒ��ϵ��*��1-��ʵ���;ö�/ԭʼ����;öȣ���*���߼۸� ����ȥ��С����1�ķ���ȡ����
	repairMoney = repairRate * ( 1- float( equip.getHardiness() ) / float( equip.getHardinessLimit() ) ) * equip.getRecodePrice() * repairCostRate
	player = BigWorld.player()
	if player.tong_holdCity == BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_KEY ):
		repairMoney *= 0.9
	repairMoney = int( math.ceil( repairMoney ) )

	return repairMoney

def _getAllRepairEquip():
	"""
	�������б�����������װ��
	@return   ��
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
	��������һ��װ���ķ���
	"""
	# �ж��Ƿ��ڰ��ұ��ʦ������װ����������ô��ۡ������ﲻ���ж����ұ��ʦ�Ƿ��Ǳ�����ұ��ʦ��
	# ��Ϊ�ܺͰ��ұ��ʦ�Ի���˵����Ҿ����ڱ��������ڽ��еĲ�����
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
	��������ȫ����Ʒ�ļ۸�
	@param invoices: Ҫ�������Ʒ
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
	����һ��װ��
	@param    repairType: ��������
	@type     repairType: UINT8
	@param    kitBagID: ���ռ۸��
	@type     kitBagID: float
	@param    orderID: ���ռ۸��
	@type     orderID: float
	@return   ��
	"""
	# ȡ����Ҫ�����Ʒ
	player = BigWorld.player()
	if player.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
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
	�������б������װ��
	"""
	# ȡ����Ҫ�����Ʒ
	player = BigWorld.player()
	if player.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
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
# ������Ʒ��ع��ܽӿ�
# -------------------------------------------------------------------------------
def redeemItem( uid ):
	"""
	�����Ʒ�Ľӿڣ����ʹ�ô˿ͻ��˽ӿ�����������������Ʒ������

	param uid:	��Ʒ��Ψһ��ʶ
	type uid :	INT64
	"""
	chapman = _getChapman()
	if chapman is None:
		ERROR_MSG( "�Ҳ�������npc��" )
		return
	player = BigWorld.player()
	if player.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
		player.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
		return
	player.cell.redeemItem( uid, chapman.id )


def onDelRedeemItem( uid ): #�������ص�
	"""
	�ع�һ���������Ʒ�ɹ��ĸ��º���

	param uid:	��Ʒ��Ψһ��ʶ
	type uid :	INT64
	"""
	if MerchantFacade.redeemItems == []:
		ERROR_MSG( "�������Ʒ�б����ݳ���." )
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
	�������Ʒ�б����ݱ䶯�ĸ��º���,��cell�����������ݼ��뵽redeemItems���һ��λ��.
	���redeemItems����7����Ʒ,���ͷһ����Ʒɾ��,Ȼ������µ�����

	param item:	�¼��������б����Ʒ
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
