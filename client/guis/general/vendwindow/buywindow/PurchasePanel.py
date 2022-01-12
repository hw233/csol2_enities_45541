#-*- coding: gb18030 -*-
#
# implement the vend buy PurchasePanel
# written by ganjinxing 2010-01-22

from guis import *
from guis.controls.BaseObjectItem import BaseObjectItem
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Align import PL_Align
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.general.vendwindow.PurchaseInputBox import PurchaseInputBox
from ItemsFactory import ObjectItem
from ItemsPanel import VendBuyItem
from ItemsPanel import BaseItemsPanel
from OwnCollectionItem import OwnCollectionItem
from config.client.msgboxtexts import Datas as mbmsgs
from LabelGather import labelGather
from guis.MLUIDefine import QAColor, ItemQAColorMode
import items
itemsFactory = items.instance()
NEWLINE = PL_NewLine.getSource
import csstatus


class BasePurchasePanel( BaseItemsPanel ) :

	def __init__( self, panel, pyBinder = None ) :
		BaseItemsPanel.__init__( self, panel, pyBinder )

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setLabel( panel.st_buyDsp, "vendwindow:BasePurchasePanel", "stBuyDsp" )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def initPagesPanel_( self, tabPanel, viewSize = ( 6, 1 ) ) :
		"""
		��ʼ����ҳ�ؼ���ͨ���ı�Ĭ�ϲ���ֵ�ķ�ʽ�������Զ����ʼ��
		"""
		BaseItemsPanel.initPagesPanel_( self, tabPanel, viewSize )

	def initItem_( self, pyViewItem ) :
		"""
		��ʼ����ӵļ����б���
		"""
		pyBuyItem = VendPurchaseItem()
		pyViewItem.pyBuyItem = pyBuyItem
		pyViewItem.addPyChild( pyBuyItem )
		pyBuyItem.left = 0
		pyBuyItem.top = 0

		pyViewItems = self.pyPagesPanel_.pyViewItems							# ��ʼ����Ӧ�ĳ��۰�ť
		index = pyViewItems.index( pyViewItem )
		relatedBtn = getattr( self.gui, "sellBtn_" + str( index ) )
		pyBtn = HButtonEx( relatedBtn )
		pyBtn.setExStatesMapping( UIState.MODE_R4C1 )
		pyBtn.onLClick.bind( self.onSellItem_ )
		pyBtn.index = index
		labelGather.setPyBgLabel( pyBtn, "vendwindow:BasePurchasePanel", "btnSell" )
		pyViewItem.pyRelatedBtn = pyBtn

	def drawItem_( self, pyViewItem ) :
		BaseItemsPanel.drawItem_( self, pyViewItem )
		pyRelatedBtn = pyViewItem.pyRelatedBtn
		pyRelatedBtn.enable = pyViewItem.pageItem is not None

	def onSellItem_( self, pyBtn ) :
		index = pyBtn.index
		sellItem = self.getViewItemByIndex_( index )
		if sellItem is None : return
		def sellConfirm( res ) :
			if res == RS_OK :
				# "�ɹ�����XXX"
				self.showMsg( 0x0a81, MB_OK, lambda res : True )			# ������Ʒ�Ľӿ��ڴ����
		name = sellItem.name()
		# "ȷ������%s��%s��"
		msg = mbmsgs[0x0a82] % ( sellItem.amount, sellItem.name() )
		self.showMsg( msg, MB_OK_CANCEL, sellConfirm )

	def getViewItemByIndex_( self, index ) :
		pyViewItems = self.pyPagesPanel_.pyViewItems
		careViewItem = pyViewItems[ index ]
		return careViewItem.pageItem

	def purchaseItem2ItemInfo_( self, purchaseItem ) :
		"""
		���չ���Ʒת��Ϊ�����������Ʒ��Ϣʵ��
		"""
		itemID = purchaseItem.itemID
		itemAmount = self.getPurchaseRemainAmount_( purchaseItem )
		baseItem = itemsFactory.createDynamicItem( itemID, itemAmount )
		if baseItem is None :
			ERROR_MSG( "Error occur when create item of id %s" % itemID )
			return None
		baseItem.uid = purchaseItem.uid
		itemInfo = ObjectItem( baseItem )
		itemInfo.rolePrice = purchaseItem.price
		return itemInfo

	def getPurchaseRemainAmount_( self, purchaseItem ) :
		"""
		��ȡ��Ʒ��ʣ���չ�����
		"""
		return 0

	def onItemPurchased_( self, purchaseItem ) :
		"""
		���յ���������������Ʒ����
		"""
		itemInfo = self.purchaseItem2ItemInfo_( purchaseItem )
		if itemInfo is None : return
		for index, orgItemInfo in enumerate( self.pyPagesPanel_.items ) :
			if orgItemInfo.uid == itemInfo.uid :
				if itemInfo.amount < 1 :
					self.pyPagesPanel_.removeItemOfIndex( index )
				else :
					self.pyPagesPanel_.updateItem( index, itemInfo )
				break
		else :
			if itemInfo.amount > 0 :
				self.pyPagesPanel_.addItem( itemInfo )
		self.pyItemsAmount_.text = str( self.pyPagesPanel_.itemCount )

	def onPurshaseItemUpdate_( self, purchaseItem ) :
		"""
		ע�⣬purchaseItem�е�����������Ʒ����ʵ���������Ǹı��ֵ
		"""
		for index, itemInfo in enumerate( self.pyPagesPanel_.items ) :
			if itemInfo.uid == purchaseItem.uid :
				remainAmount = self.getPurchaseRemainAmount_( purchaseItem )
				if remainAmount < 1 :
					self.pyPagesPanel_.removeItemOfIndex( index )
					self.pyItemsAmount_.text = str( self.pyPagesPanel_.itemCount )
				else :
					itemInfo.rolePrice = purchaseItem.price
					itemInfo.baseItem.amount = remainAmount
					self.pyPagesPanel_.updateItem( index, itemInfo )
				break


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def reset( self ) :
		self.pyPagesPanel_.clearItems()
		self.pyItemsAmount_.text = str( self.pyPagesPanel_.itemCount )



class PurchasePanel( BasePurchasePanel ) :

	def __init__( self, panel, pyBinder = None ) :
		BasePurchasePanel.__init__( self, panel, pyBinder )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_RECEIVE_VEND_PURCHASED_ITEM"] = self.onItemPurchased_
		self.triggers_["EVT_ON_VEND_PURCHASE_ITEM_UPDATE"] = self.onPurshaseItemUpdate_
		self.triggers_["EVT_ON_CLEAR_VEND_PURCHASED_ITEM"] = self.__onClearPanel
		BasePurchasePanel.registerTriggers_( self )

	def onSellItem_( self, pyBtn ) :
		index = pyBtn.index
		sellItem = self.getViewItemByIndex_( index )
		if sellItem is None : return
		def sellConfirm( res, amount, price ) :
			if res == DialogResult.OK :
				def queryAgain( res ) :
					if res == RS_OK :
						player = BigWorld.player()
						if not player.checkItemFromNKCK_( sellItem.id, amount ) :
							# "��û���㹻����Ʒ���ۣ�"
							self.showMsg( 0x0a91 )
							return
						if player.intonating() or player.isInHomingSpell :
							player.statusMessage( csstatus.TI_SHOU_SELL_FORBIDDEN_IN_INTONATING )
							return
						seller = self.pyBinder.trapEntity
						if seller :
							purchaseItem = OwnCollectionItem()
							purchaseItem.itemID = sellItem.id
							purchaseItem.price = price
							purchaseItem.collectAmount = amount
							purchaseItem.uid = sellItem.uid
							seller.cell.sellOwnCollectionItem( purchaseItem )
				name = sellItem.name()
				# "ȷ������%s��%s��"
				msg = mbmsgs[0x0a82] % ( amount, sellItem.name() )
				self.showMsg( msg, MB_OK_CANCEL, queryAgain )
		purchaseInputBox = PurchaseInputBox()
		purchaseInputBox.unitPriceReadOnly = True
		purchaseInputBox.unitPrice = sellItem.rolePrice
		player = BigWorld.player()
		sellerAmount = player.countItemTotal_( sellItem.id )		# ��������ӵ�е���Ʒ����
		if sellerAmount > sellItem.amount:
			purchaseInputBox.amountRange = [ 1, sellItem.amount ]
		else:
			purchaseInputBox.amountRange = [ 1, sellerAmount ]
		hintText = ( labelGather.getText( "vendwindow:BuyPurchasePanel", "phIBox_UnitPrice" ),
					 labelGather.getText( "vendwindow:BuyPurchasePanel", "phIBox_SellAmount" ),
					 labelGather.getText( "vendwindow:BuyPurchasePanel", "phIBox_TotalEarn" ),
					)
		purchaseInputBox.show( sellConfirm,
								labelGather.getText( "vendwindow:BuyPurchasePanel", "phIBox_Title" ),
								self,
								hintText
							)

	def getPurchaseRemainAmount_( self, purchaseItem ) :
		"""
		��ȡ��Ʒ��ʣ���չ�����
		"""
		return purchaseItem.collectAmount

	def onItemPurchased_( self, purchaseItem, sellerID ) :
		"""
		���յ���������������Ʒ����
		"""
		seller = self.pyBinder.trapEntity
		if seller is None or seller.id != sellerID : return		# ���Ҳ����ڻ��߲��Ǹ����ҵ��չ���Ʒ
		BasePurchasePanel.onItemPurchased_( self, purchaseItem )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onClearPanel( self ) :
		"""
		����չ�����
		"""
		self.reset()


class VendPurchaseItem( VendBuyItem ) :

	__ITEM = None

	def __init__( self ) :
		if VendPurchaseItem.__ITEM is None :
			VendPurchaseItem.__ITEM = GUI.load( "guis/general/vendwindow/buywindow/purchaseitem.gui" )
			uiFixer.firstLoadFix( VendPurchaseItem.__ITEM )
		item = util.copyGuiTree( VendPurchaseItem.__ITEM )
		VendBuyItem.__init__( self, item )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def initialize_( self, item ) :
		self.__pyResume = CSRichText( item.rt_resume1 )
		self.__pyResume.foreColor = ( 236, 218, 157, 255 )
		self.__pyResume.autoNewline = False
		self.__pyItem = BaseObjectItem( item.item.item )
		self.__pyItem.focus = False

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, pyViewItem ) :
		itemInfo = pyViewItem.pageItem
		self.__pyItem.update( itemInfo )
		if itemInfo is None :
			self.__pyResume.text = ""
			util.setGuiState( self.gui.item, ( 4, 2 ), ItemQAColorMode[0] )
			pyViewItem.focus = False
		else :
			pyViewItem.focus = True
			QALVColor = QAColor[ itemInfo.quality ]
			nameStr = PL_Font.getSource( itemInfo.name().ljust(18), fc = QALVColor )
			#amountStr = PL_Font.getSource( str( itemInfo.amount ), fc = ( 255, 255, 0, 255 ) )
			priceStr = utils.currencyToViewText( itemInfo.rolePrice )
			priceStr = PL_Font.getSource( priceStr, fc = ( 16, 197, 165, 255 ) )
			self.__pyResume.text = PL_Align.getSource( lineFlat = "M" ) \
								 + nameStr \
								 + NEWLINE(1) \
								 + labelGather.getText( "vendwindow:VendPurchaseItem", "purchasePrice" )\
								 + priceStr
			util.setGuiState( self.gui.item, ( 4, 2 ), ItemQAColorMode[itemInfo.quality] )
		if pyViewItem.selected or pyViewItem.highlight :
			self.setStateView_( UIState.HIGHLIGHT )
		else :
			self.setStateView_( UIState.COMMON )



