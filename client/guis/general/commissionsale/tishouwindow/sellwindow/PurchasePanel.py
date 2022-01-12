# -*- coding: gb18030 -*-

# implement the TSPurchasePanel class
# written by ganjinxing 2010-01-27

from guis import *
from guis.tooluis.inputbox.MoneyInputBox import MoneyInputBox
from guis.general.vendwindow.PurchaseInputBox import PurchaseInputBox
from guis.general.vendwindow.sellwindow.PurchasePanel import BasePurchasePanel
from config.client.msgboxtexts import Datas as mbmsgs
from CollectionItem import CollectionItem
from LabelGather import labelGather


class TSPurchasePanel( BasePurchasePanel ) :

	def __init__( self, panel, pyBinder = None ) :
		BasePurchasePanel.__init__( self, panel, pyBinder )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __queryTSPurchaseInfo( self ) :
		"""
		������������ѯ�չ���Ʒ������
		"""
		self.reset()
		def queryInfo() :
			tishouNPC = self.pyBinder.pyBinder.tishouNPC
			if tishouNPC is not None :
				BigWorld.player().cell.queryCollectionInfo( tishouNPC.ownerDBID )
		if self.visible :
			queryInfo()
		else :
			BigWorld.callback( 0.7, queryInfo )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_RECEIVE_TISHOU_PURCHASING_ITEM"] = self.receivePurchaseItem_
		self.triggers_["EVT_ON_REMOVE_TISHOU_PURCHASING_ITEM"] = self.onPurchaseItemRemove_
		self.triggers_["EVT_ON_TS_PURCHASING_ITEM_CLEAR"] = self.reset
		BasePurchasePanel.registerTriggers_( self )

	def checkOperation_( self ) :
		tishouNPC = self.pyBinder.pyBinder.tishouNPC
		if tishouNPC is None :
			# "δ�ҵ�����NPC��"
			self.showMessage_( 0x0b01 )
			return False
		isTishouState = tishouNPC.tsState
		if isTishouState :
			# "����ֹͣ�����ٽ��иò�����"
			self.showMessage_( 0x0b02 )
			return False
		return True

	def removeSelectedItem_( self ) :
		if BigWorld.player().iskitbagsLocked(): # ������������״̬
			self.showMessage_( 0x0b07 )
			return
		if not self.checkOperation_() : return
		pySelItem = self.getPySelItem_()
		if pySelItem is None : return
		itemUID = pySelItem.itemInfo.uid
		BigWorld.player().cell.removeCollectionItem( itemUID )

	def onItemRClick_( self, pyItem, mode ) :
		"""
		�һ���Ʒʱ������Ʒ�Ƴ�
		"""
		if BigWorld.player().iskitbagsLocked(): # ������������״̬
			self.showMessage_( 0x0b07 )
			return
		if not self.checkOperation_() : return
		if pyItem.itemInfo is None : return
		itemUID = pyItem.itemInfo.uid
		BigWorld.player().cell.removeCollectionItem( itemUID )

	def getPurchaseRemainAmount_( self, purchaseItem ) :
		"""
		��ȡ��Ʒ��ʣ���չ�����
		"""
		return purchaseItem.collectAmount - purchaseItem.collectedAmount

	def addPCHItemByDict_( self, itemDict ) :
		remainBlanks = len( self.pyItems_ ) - len( self.getPurchaseItems() )
		if remainBlanks == 0 :
			# "�չ�������װ��!"
			showAutoHideMessage( 3.0, 0x0b03, mbmsgs[0x0c22] )
			return
		def addItem( result, amount, price ) :
			if result == DialogResult.OK :
				if price <= 0 :
					# "����Ʒ��û�ж���!"
					showAutoHideMessage( 3.0, 0x0b04, mbmsgs[0x0c22] )
					return
				if not self.checkOperation_() :
					return
				if BigWorld.player().iskitbagsLocked(): # ������������״̬
					self.showMessage_( 0x0b07 )
					return

				purchaseItems = self.createPurchaseItems_( CollectionItem, \
															itemDict, \
															amount, \
															price \
														)
				remainBlanks = len( self.pyItems_ ) - len( self.getPurchaseItems() )
				if remainBlanks < len( purchaseItems ) :
					# "�����λ����!"
					showAutoHideMessage( 3.0, 0x0b05, mbmsgs[0x0c22] )
				else :
					player = BigWorld.player()
					totalCost = amount * price
					if totalCost > player.money :									# �������Ƿ�Ǯ�չ���Ʒ
						# "��û���㹻�Ľ�Ǯ�չ���Ʒ��"
						self.showMessage_( 0x0ac3 )
						return
					for purchaseItem in purchaseItems :
						player.cell.addCollectionItem( purchaseItem )
		purchaseInputBox = PurchaseInputBox()
		purchaseInputBox.amountRange = [ 1, itemDict[ "maxCount" ] * remainBlanks ]
		hintText = ( labelGather.getText( "commissionsale:TiShouPurchasePanel", "ipBoxPrice" ),
					 labelGather.getText( "commissionsale:TiShouPurchasePanel", "ipBoxPurchaseAmount" ),
					 labelGather.getText( "commissionsale:TiShouPurchasePanel", "ipBoxTotalPrice" )
					 )
		purchaseInputBox.show( addItem,
							labelGather.getText( "commissionsale:TiShouPurchasePanel", "ipBoxPurchaseSetting" ),
							self,
							hintText
							)

	def enableUpBtn_( self ) :
		tishouNPC = self.pyBinder.pyBinder.tishouNPC
		if tishouNPC is None : return
		isTishouState = tishouNPC.tsState
		selItem = self.pyCBItems_.selItem
		self.pyAddBtn_.enable = selItem is not None and not isTishouState

	def enableDownBtn_( self ) :
		tishouNPC = self.pyBinder.pyBinder.tishouNPC
		if tishouNPC is None : return
		isTishouState = tishouNPC.tsState
		pySelItem = self.getPySelItem_()
		self.pyRemoveBtn_.enable = pySelItem is not None and not isTishouState


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onTSNPCFlagChaned( self, oldFlag ) :
		self.enableUpBtn_()
		self.enableDownBtn_()

	def changeItemPrice( self ) :
		if not self.checkOperation_() : return
		pySelItem = self.getPySelItem_()
		if pySelItem is None : return
		def changePrice( res, price ):
			if res == DialogResult.OK:
				if BigWorld.player().iskitbagsLocked(): # ������������״̬
					self.showMessage_( 0x0b07 )
					return
				if price <= 0:
					# "��Ʒδ���ۣ�"
					showAutoHideMessage( 3.0, 0x0b06, mbmsgs[0x0c22] )
				elif price != pySelItem.itemInfo.rolePrice :			# �۸��б䶯
					if not self.checkOperation_() : return
					itemInfo = pySelItem.itemInfo
					player = BigWorld.player()
					totalCost = ( price - itemInfo.rolePrice ) * itemInfo.amount
					if totalCost > player.money :									# �������Ƿ�Ǯ�չ���Ʒ
						# "��û���㹻�Ľ�Ǯ�չ���Ʒ��"
						self.showMessage_( 0x0ac3 )
						return
					itemDict = {}
					itemDict["maxCount"] = itemInfo.amount
					itemDict["id"] = itemInfo.id
					purchaseItem = self.createPurchaseItems_( CollectionItem, \
															itemDict, \
															itemInfo.amount, \
															price \
															)[0]
					purchaseItem.uid = itemInfo.uid
					BigWorld.player().cell.updateCollectionItemInfo( purchaseItem )
		MoneyInputBox().show( changePrice,
							labelGather.getText( "commissionsale:TiShouPurchasePanel", "ipBoxNewPrice" ),
							self
							)

	def onParentShow( self ) :
		"""
		�򿪴���
		"""
		self.__queryTSPurchaseInfo()
