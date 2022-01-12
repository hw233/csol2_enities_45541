# -*- coding: gb18030 -*-

from guis import *
from CollectionItem import CollectionItem
from guis.general.vendwindow.PurchaseInputBox import PurchaseInputBox
from guis.general.vendwindow.buywindow.PurchasePanel import BasePurchasePanel
from config.client.msgboxtexts import Datas as mbmsgs
from LabelGather import labelGather
import csstatus


class PurchasePanel( BasePurchasePanel ) :

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_RECEIVE_TISHOW_PURCHASED_ITEM"] = self.onItemPurchased_
		self.triggers_["EVT_ON_TS_PURCHASED_ITEM_CLEAR"] = self.reset
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
							purchaseItem = CollectionItem()
							purchaseItem.itemID = sellItem.id
							purchaseItem.price = price
							purchaseItem.collectAmount = amount
							purchaseItem.uid = sellItem.uid
							player.cell.sellCollectionItems( [ purchaseItem,], seller.ownerDBID )					# ���鷽�����������ϰ�����
				name = sellItem.name()
				# "ȷ������%s��%s��"
				msg = mbmsgs[0x0a82] % ( amount, sellItem.name() )
				self.showMsg( msg, MB_OK_CANCEL, queryAgain )
		purchaseInputBox = PurchaseInputBox()
		purchaseInputBox.unitPriceReadOnly = True
		purchaseInputBox.unitPrice = sellItem.rolePrice
		purchaseInputBox.amountRange = [ 1, sellItem.amount ]
		hintText = (
					labelGather.getText( "commissionsale:TSBuyPurchasePenel", "ipBoxPrice" ),
					labelGather.getText( "commissionsale:TSBuyPurchasePenel", "ipBoxPurchaseAmount" ),
					labelGather.getText( "commissionsale:TSBuyPurchasePenel", "ipBoxTotalPrice" )
					)
		purchaseInputBox.show( sellConfirm,
								labelGather.getText( "commissionsale:TSBuyPurchasePenel", "ipBoxPurchaseSetting" ),
								self,
								hintText )

	def getPurchaseRemainAmount_( self, purchaseItem ) :
		"""
		��ȡ��Ʒ��ʣ���չ�����
		"""
		return purchaseItem.collectAmount - purchaseItem.collectedAmount

	def onItemPurchased_( self, purchaseItem ) :
		"""
		���յ���������������Ʒ����
		"""
		tishouNPC = self.pyBinder.trapEntity
		if tishouNPC is None or \
			tishouNPC.ownerDBID != purchaseItem.collectorDBID :		# NPC�����ڻ��߲��Ǹ�NPC���չ���Ʒ
				return
		BasePurchasePanel.onItemPurchased_( self, purchaseItem )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __queryTSPurchaseInfo( self ) :
		"""
		������������ѯ�չ���Ʒ������
		"""
		self.reset()
		def queryInfo() :
			tishouNPC = self.pyBinder.trapEntity
			if tishouNPC is not None :
				BigWorld.player().cell.queryCollectionInfo( tishouNPC.ownerDBID )
		if self.visible :
			queryInfo()
		else :
			BigWorld.callback( 0.7, queryInfo )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onParentShow( self ) :
		self.__queryTSPurchaseInfo()