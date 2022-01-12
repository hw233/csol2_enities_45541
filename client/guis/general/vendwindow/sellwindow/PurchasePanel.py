#-*- coding: gb18030 -*-
#
# written by ganjinxing 2010-01-21

from guis import *
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TabCtrl import TabPanel
from guis.controls.StaticText import StaticText
from guis.controls.RichText import RichText
from guis.controls.ODComboBox import ODComboBox
from guis.controls.BaseObjectItem import BaseObjectItem
from guis.tooluis.richtext_plugins.PL_Align import PL_Align
from guis.tooluis.inputbox.MoneyInputBox import MoneyInputBox
from guis.general.vendwindow.PurchaseInputBox import PurchaseInputBox
from config.CollectionItems import Datas as PurchaseItemDatas
from config.client.msgboxtexts import Datas as mbmsgs
from ItemsFactory import ObjectItem
from GoodsPanel import GoodsItem as BaseItem
from OwnCollectionItem import OwnCollectionItem
from LabelGather import labelGather
import items
import csdefine
itemsFactory = items.instance()


class BasePurchasePanel( TabPanel ) :

	def __init__( self, panel, pyBinder ) :
		TabPanel.__init__( self, panel, pyBinder )
		self.dropFocus = True

		self.triggers_ = {}
		self.registerTriggers_()
		self.pyItems_ = {}
		self.pyMsgBox_ = None
		self.initialize_( panel )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		for key in self.triggers_ :
			ECenter.registerEvent( key, self )

	def initialize_( self, panel ) :
		for name, item in panel.children:
			if "item_" not in name : continue
			index = int( name.split( "_" )[1] )
			pyItem = self.getInitItem_( item )
			pyItem.index = index
			pyItem.update( None )
			self.pyItems_[index] = pyItem

		self.initComboBox_( panel )

		self.pyAddBtn_ = HButtonEx( panel.addBtn )
		self.pyAddBtn_.setExStatesMapping( UIState.MODE_R4C1 )
		self.pyAddBtn_.onLClick.bind( self.addPurchaseItem_ )
		self.pyAddBtn_.enable = False

		self.pyRemoveBtn_ = HButtonEx( panel.removeBtn )
		self.pyRemoveBtn_.setExStatesMapping( UIState.MODE_R4C1 )
		self.pyRemoveBtn_.onLClick.bind( self.removeSelectedItem_ )
		self.pyRemoveBtn_.enable = False

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.pyAddBtn_, "vendwindow:SellBasePurchasePanel", "btnAdd" )
		labelGather.setPyBgLabel( self.pyRemoveBtn_, "vendwindow:SellBasePurchasePanel", "btnRemove" )

	def initComboBox_( self, panel ) :
		self.pyCBType_ = ODComboBox( panel.cb_itemType )
		self.pyCBType_.autoSelect = False
		self.pyCBType_.pyBox_.text = labelGather.getText( "vendwindow:SellBasePurchasePanel", "cbSelType" )
		self.pyCBSubType_ = ODComboBox( panel.cb_subType )
		self.pyCBSubType_.autoSelect = False
		self.pyCBSubType_.pyBox_.text = labelGather.getText( "vendwindow:SellBasePurchasePanel", "cbSelSubType" )
		self.pyCBItems_ = ODComboBox( panel.cb_itemName )
		self.pyCBItems_.autoSelect = False
		self.pyCBItems_.ownerDraw = True
		self.pyCBItems_.pyBox_.text = labelGather.getText( "vendwindow:SellBasePurchasePanel", "cbSelItem" )
		self.pyCBItems_.onViewItemInitialized.bind( self.onInitialized_ )
		self.pyCBItems_.onDrawItem.bind( self.onDrawItem_ )
		self.pyCBType_.onItemSelectChanged.bind( self.onItemTypeSelected_ )
		self.pyCBSubType_.onItemSelectChanged.bind( self.onItemSubTypeSelected_ )
		self.pyCBItems_.onItemSelectChanged.bind( self.onItemSelected_ )
		typeNames = self.getSortNames_( PurchaseItemDatas )
		self.pyCBType_.addItems( typeNames )

	def resetComboBoxs_( self ) :
		self.pyCBType_.selIndex = -1
		self.pyCBType_.pyBox_.text = labelGather.getText( "vendwindow:SellBasePurchasePanel", "cbSelType" )
		self.pyCBSubType_.pyBox_.text = labelGather.getText( "vendwindow:SellBasePurchasePanel", "cbSelSubType" )
		self.pyCBItems_.pyBox_.text = labelGather.getText( "vendwindow:SellBasePurchasePanel", "cbSelItem" )

	def getInitItem_( self, item ) :
		return PurchaseItem( item, self )

	# -------------------------------------------------
	# item oprate
	# -------------------------------------------------
	def addPurchaseItem_( self ) :
		if not self.checkOperation_() : return
		selItemDict = self.getSelPchItemDict_()
		if selItemDict is None :
			# "请先选择一个收购物品!"
			showAutoHideMessage( 3.0, 0x0ac4, mbmsgs[0x0c22] )
			return
		self.addPCHItemByDict_( selItemDict )

	def removeSelectedItem_( self ) :
		pass

	def enableUpBtn_( self ) :
		pass

	def enableDownBtn_( self ) :
		pass

	def onInitialized_( self, pyViewItem ):
		pyRText = RichText()
		pyRText.crossFocus = True
		pyRText.onMouseEnter.bind( self.__onShowItemInfos )
		pyRText.onMouseLeave.bind( self.__onHideItemInfos )
		pyViewItem.addPyChild( pyRText )
		pyViewItem.pyRText = pyRText

	def onDrawItem_( self, pyViewItem ):
		pyPanel = pyViewItem.pyPanel
		if pyViewItem.selected :
			pyViewItem.pyRText.foreColor = pyPanel.itemSelectedForeColor			# 选中状态下的前景色
			pyViewItem.color = pyPanel.itemSelectedBackColor				# 选中状态下的背景色
		elif pyViewItem.highlight :
			pyViewItem.pyRText.foreColor = pyPanel.itemHighlightForeColor		# 高亮状态下的前景色
			pyViewItem.color = pyPanel.itemHighlightBackColor				# 高亮状态下的背景色
		else :
			pyViewItem.pyRText.foreColor = pyPanel.itemCommonForeColor
			pyViewItem.color = pyPanel.itemCommonBackColor
		idStr = pyViewItem.listItem
		baseItem = itemsFactory.createDynamicItem(int( idStr ))
		pyRText = pyViewItem.pyRText
		pyRText.idStr = idStr
		pyRText.left = 3.0
		pyRText.top = 1.0
		pyRText.text = baseItem.name()

	def onItemTypeSelected_( self, index ) :
		self.pyCBSubType_.clearItems()
		self.pyCBSubType_.pyBox_.text = labelGather.getText( "vendwindow:SellBasePurchasePanel", "cbSelSubType" )
		selType = self.pyCBType_.selItem
		if selType is None : return
		subTypes = PurchaseItemDatas[selType]
		typeNames = self.getSortNames_( subTypes )
		self.pyCBSubType_.addItems( typeNames )

	def getSortNames_( self, subTypes ):
		typeNames = []
		indexList = [subData["index"] for subName, subData in subTypes.items() if subName != "index"]
		indexList.sort()
		for index in indexList:
			for subName, subType in subTypes.items():
				if subName == "index":continue
				if index == subType["index"]:
					typeNames.append( subName )
		return typeNames

	def __onShowItemInfos( self, pyRText ):
		"""
		显示物品信息
		"""
		baseItem = itemsFactory.createDynamicItem(int( pyRText.idStr ))
		itemInfo = ObjectItem( baseItem )
		toolbox.infoTip.showItemTips( pyRText, itemInfo.description )

	def __onHideItemInfos( self ):
		"""
		隐藏物品信息
		"""
		toolbox.infoTip.hide()

	def onItemSubTypeSelected_( self, index ) :
		self.pyCBItems_.clearItems()
		self.pyCBItems_.pyBox_.text = labelGather.getText( "vendwindow:SellBasePurchasePanel", "cbSelItem" )
		selType = self.pyCBType_.selItem
		selSubType = self.pyCBSubType_.selItem
		if not( selType and selSubType ) : return
		selSubIds = PurchaseItemDatas[selType][selSubType]
		idStrs = self.getSortNames_( selSubIds )
		for idStr in idStrs:
			self.pyCBItems_.addItem( idStr )

	def onItemSelected_( self, index ) :
		self.enableUpBtn_()
		selItem = self.pyCBItems_.selItem
		if selItem is None:return
		baseItem = itemsFactory.createDynamicItem(int( selItem ))
		self.pyCBItems_.pyBox_.text = baseItem.name()

	def getSelPchItemDict_( self ) :
		selType = self.pyCBType_.selItem
		selSubType = self.pyCBSubType_.selItem
		itemID = self.pyCBItems_.selItem
		if selType and selSubType and itemID :
			ItemDatas = PurchaseItemDatas[selType][selSubType]
			for idStr, itemData in ItemDatas.items():
				if idStr == itemID:
					return {"id": idStr, "maxCount": itemData[ "maxCount" ]}

	def searchPCHItem_( self, searchID ) :
		"""
		根据物品ID在收购列表中查找到该物品的数据
		"""
		for typeName, typeValues in PurchaseItemDatas.iteritems() :
			for subType, subValues in typeValues.iteritems() :
				for itemID, itemDict in subValues.iteritems() :
					if int( itemID ) == searchID :
						return { "id": itemID, "maxCount": itemDict[ "maxCount" ]}

	def createPurchaseItems_( self, CLS, itemDict, amount, price ) :
		"""
		根据物品叠加情况生成收购物品列表
		"""
		stackMax = itemDict[ "maxCount" ]
		itemID = int( itemDict[ "id" ] )
		itemList = []
		residue = amount % stackMax
		if residue > 0 :
			purchaseItem = CLS()
			purchaseItem.itemID = itemID
			purchaseItem.price = price
			purchaseItem.collectAmount = residue
			itemList.append( purchaseItem )
		amount -= residue
		while amount > 0 :
			amount -= stackMax
			purchaseItem = CLS()
			purchaseItem.itemID = itemID
			purchaseItem.price = price
			purchaseItem.collectAmount = stackMax
			itemList.append( purchaseItem )
		return itemList

	def getValidItem_( self, index = -1 ) :
		"""
		获取一个可用的格子用于更新添加物品
		@param 		index : 指定索引，若为-1表示获取第一个可用格子
		"""
		if index < 0 :
			for pyItem in self.pyItems_.itervalues() :
				if pyItem.itemInfo is None :
					return pyItem
		else :
			return self.pyItems_.get( index, None )

	def receivePurchaseItem_( self, purchaseItem, index = -1 ) :
		"""
		接收到寄售物品数据
		"""
		if not self.pyBinder.pyBinder.visible : return							# 不作这个限制可能会出现重复物品的情况
		pyValidItem = self.getPyItemByUID_( purchaseItem.uid )
		if pyValidItem is None :
			pyValidItem = self.getValidItem_( index )
			if pyValidItem is None :
				ERROR_MSG("Receive item %s from server but the panel is full!" % str( baseItem.id ))
				return
			itemID = purchaseItem.itemID
			purchaseAmount = self.getPurchaseRemainAmount_( purchaseItem )
			if purchaseAmount < 1 : return										# 物品数量小于1了，不再显示这个物品
			baseItem = itemsFactory.createDynamicItem( itemID, purchaseAmount )
			if baseItem is None :
				ERROR_MSG( "Error occur when create item of id %s" % itemID )
				return
			baseItem.uid = purchaseItem.uid
			newItemInfo = ObjectItem( baseItem )
			newItemInfo.rolePrice = purchaseItem.price
			pyValidItem.update( newItemInfo )
		else :
			itemInfo = pyValidItem.itemInfo
			itemInfo.rolePrice = purchaseItem.price
			purchaseAmount = self.getPurchaseRemainAmount_( purchaseItem )
			if purchaseAmount < 1 :
				pyValidItem.update( None )
			else :
				itemInfo.baseItem.amount = purchaseAmount
				pyValidItem.update( itemInfo )
		self.onNotifyCostChanged_()

	def getPurchaseRemainAmount_( self, purchaseItem ) :
		"""
		由于NPC和个人收购物品剩余数量的统计不一样，为了
		实现代码重用，只能实现该方法。
		"""
		return 0

	def onPurchaseItemRemove_( self, uid ) :
		pyItem = self.getPyItemByUID_( uid )
		if pyItem is not None :
			pyItem.update( None )
			self.enableDownBtn_()
			self.pyBinder.enableChangePriceBtn()
			self.onNotifyCostChanged_()

	def onGoodsUpdatePrice_( self, uid, price ) :
		pyItem = self.getPyItemByUID_( uid )
		if pyItem is not None :
			itemInfo = pyItem.itemInfo
			itemInfo.rolePrice = price
			pyItem.update( itemInfo )
			self.onNotifyCostChanged_()

	def onPurshaseItemUpdate_( self, purchaseItem ) :
		"""
		"""
		pass

	def getPyItemByUID_( self, uid ) :
		"""
		根据UID获取物品信息
		"""
		for pyItem in self.pyItems_.itervalues() :
			if pyItem.itemInfo is None : continue
			if pyItem.itemInfo.uid == uid :
				return pyItem

	def clearPanel_( self ) :
		"""
		清空面板
		"""
		for pyItem in self.pyItems_.itervalues() :
			pyItem.update( None )
		self.resetComboBoxs_()
		self.onNotifyCostChanged_()

	def showMessage_( self, msg, callback = lambda res : True ) :
		def query( result ) :
			self.pyMsgBox_ = None
			callback( result )
		if self.pyMsgBox_ is not None :
			self.pyMsgBox_.hide()
		self.pyMsgBox_ = showMessage( msg, "", MB_OK, query, self, Define.GST_IN_WORLD )

	def checkOperation_( self ) :
		return True

	# -------------------------------------------------
	# panel display
	# -------------------------------------------------
	def onItemLClick_( self, pyItem, mode ) :
		"""
		界面上某个物品被点击
		"""
		pyCurrSelItem = self.getPySelItem_()
		if pyCurrSelItem is not None :
			pyCurrSelItem.selected = False
		pyItem.selected = True
		self.enableDownBtn_()
		self.pyBinder.enableChangePriceBtn()

	def onItemRClick_( self, pyItem, mode ) :
		"""
		右击物品时将该物品移除
		"""
		pass

	def onDrop_( self, pyTarget, pyDropped ) :
		"""
		拖动的物品在此放下
		"""
		if not self.checkOperation_() : return False
		if pyDropped.dragMark != DragMark.KITBAG_WND : return False
		if pyDropped.itemInfo is None : return False
		TabPanel.onDrop_( self, pyTarget, pyDropped )
		purchaseItemDict = self.searchPCHItem_( pyDropped.itemInfo.id )
		if purchaseItemDict is None :
			# "该物品不支持收购!"
			self.showMessage_( 0x0ac1 )
		else :
			self.addPCHItemByDict_( purchaseItemDict )
		return True

	def getPySelItem_( self ) :
		"""
		获取被选中的物品
		"""
		for pyItem in self.pyItems_.itervalues() :
			if pyItem.selected :
				return pyItem

	def getPurchaseTotalPrice( self ) :
		totalPrice = 0
		for pyItem in self.pyItems_.itervalues() :
			if pyItem.itemInfo is not None :
				totalPrice += pyItem.itemInfo.rolePrice * pyItem.itemInfo.amount
		return totalPrice

	def onNotifyCostChanged_( self ) :
		"""
		通知界面总价发生变化
		"""
		purchaseTotalCost = self.getPurchaseTotalPrice()
		self.pyBinder.onUpdatePurchaseCost_( purchaseTotalCost )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getPurchaseItems( self ) :
		purchaseItems = []
		for pyItem in self.pyItems_.itervalues() :
			if pyItem.itemInfo is not None :
				purchaseItems.append( pyItem.itemInfo )
		return purchaseItems

	def canChangePrice( self ) :
		return self.getPySelItem_() is not None

	def getTotalPrice( self ) :
		"""
		收购物品不需要摊税
		"""
		return 0

	def changeItemPrice( self ) :
		pass

	def onRoleTradeStateChanged( self, state ) :
		self.enableUpBtn_()
		self.enableDownBtn_()

	def onParentShow( self ) :
		if self.visible :
			self.onShow()
		else :
			self.onHide()

	def onParentHide( self ) :
		pass

	def onShow( self ) :
		if self.pyBinder :
			self.pyBinder.onSwitchVendMode_( False )
			self.onNotifyCostChanged_()

	def onHide( self ) :
		if self.pyBinder :
			self.pyBinder.onSwitchVendMode_( True )
			self.pyBinder.onCalcuExpense_()

	def reset( self ) :
		self.clearPanel_()

	def onEvent( self, evtMacro, *args ) :
		self.triggers_[ evtMacro ]( *args )



class VendPurchasePanel( BasePurchasePanel ) :

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_RECEIVE_VEND_PURCHASING_ITEM"] = self.receivePurchaseItem_
		self.triggers_["EVT_ON_REMOVE_VEND_PURCHASING_ITEM"] = self.onPurchaseItemRemove_
		self.triggers_["EVT_ON_VEND_PURCHASE_ITEM_UPDATE"] = self.onPurshaseItemUpdate_
		BasePurchasePanel.registerTriggers_( self )

	def checkOperation_( self ) :
		isVendState = BigWorld.player().state == csdefine.ENTITY_STATE_VEND
		if isVendState :
			# "请先停止摆摊再进行该操作！"
			self.showMessage_( 0x0ac2 )
			return False
		return True

	def removeSelectedItem_( self ) :
		if not self.checkOperation_() : return
		pySelItem = self.getPySelItem_()
		if pySelItem is None : return
		itemUID = pySelItem.itemInfo.uid
		BigWorld.player().cell.removeOwnCollectionItem( itemUID )

	def onPurshaseItemUpdate_( self, purchaseItem ) :
		"""
		注意，purchaseItem中的数量不是物品的真实数量，而是改变的值
		"""
		pyItem = self.getPyItemByUID_( purchaseItem.uid )
		if pyItem is None : return
		itemInfo = pyItem.itemInfo
		remainAmount = purchaseItem.collectAmount
		if remainAmount < 1 :
			pyItem.update( None )
			self.enableDownBtn_()
			self.pyBinder.enableChangePriceBtn()
		else :
			itemInfo.rolePrice = purchaseItem.price
			itemInfo.baseItem.amount = remainAmount
			pyItem.update( itemInfo )
		self.onNotifyCostChanged_()

	def getPurchaseRemainAmount_( self, purchaseItem ) :
		"""
		获取物品的剩余收购数量
		"""
		return purchaseItem.collectAmount

	def onItemRClick_( self, pyItem, mode ) :
		"""
		右击物品时将该物品移除
		"""
		if not self.checkOperation_() : return
		if pyItem.itemInfo is None : return
		itemUID = pyItem.itemInfo.uid
		BigWorld.player().cell.removeOwnCollectionItem( itemUID )

	def addPCHItemByDict_( self, itemDict ) :
		remainBlanks = len( self.pyItems_ ) - len( self.getPurchaseItems() )
		if remainBlanks == 0 :
			# "收购界面已装满!"
			showAutoHideMessage( 3.0, 0x0ac5, mbmsgs[0x0c22] )
			return
		def addItem( result, amount, price ) :
			if result == DialogResult.OK :
				if price <= 0 :
					# "该物品还没有定价!"
					showAutoHideMessage( 3.0, 0x0ac6, mbmsgs[0x0c22] )
				else :
					if not self.checkOperation_() : return
					purchaseItems = self.createPurchaseItems_( OwnCollectionItem, \
																itemDict, \
																amount, \
																price \
															)
					remainBlanks = len( self.pyItems_ ) - len( self.getPurchaseItems() )
					if remainBlanks < len( purchaseItems ) :
						# "界面空位不足!"
						showAutoHideMessage( 3.0, 0x0ac7, mbmsgs[0x0c22] )
					else :
						player = BigWorld.player()
						totalCost = self.getPurchaseTotalPrice()
						totalCost += amount * price
						if totalCost > player.money :									# 检查玩家是否够钱收购商品
							# "您没有足够的金钱收购物品。"
							self.showMessage_( 0x0ac3 )
							return
						for purchaseItem in purchaseItems :
							player.cell.addOwnCollectionItem( purchaseItem )
		purchaseInputBox = PurchaseInputBox()
		purchaseInputBox.unitPriceReadOnly = False
		purchaseInputBox.unitPrice = 0
		purchaseInputBox.amountRange = [ 1, itemDict[ "maxCount" ] * remainBlanks ]
		hintText = ( labelGather.getText( "vendwindow:VendPurchasePanel", "ipBoxPrice" ),
					 labelGather.getText( "vendwindow:VendPurchasePanel", "ipBoxPurchaseAmount" ),
					 labelGather.getText( "vendwindow:VendPurchasePanel", "ipBoxTotalPrice" )
					 )
		purchaseInputBox.show( addItem,
							labelGather.getText( "vendwindow:VendPurchasePanel", "ipBoxPurchaseSetting" ),
							self,
							hintText
							)

	def enableUpBtn_( self ) :
		isVendState = BigWorld.player().state == csdefine.ENTITY_STATE_VEND
		selItem = self.pyCBItems_.selItem
		self.pyAddBtn_.enable = selItem is not None and not isVendState

	def enableDownBtn_( self ) :
		isVendState = BigWorld.player().state == csdefine.ENTITY_STATE_VEND
		pySelItem = self.getPySelItem_()
		self.pyRemoveBtn_.enable = pySelItem is not None and not isVendState


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def changeItemPrice( self ) :
		if not self.checkOperation_() : return
		pySelItem = self.getPySelItem_()
		if pySelItem is None : return
		def changePrice( res, price ):
			if res == DialogResult.OK:
				if price <= 0:
					# "物品未定价！"
					showAutoHideMessage( 3.0, 0x0ac6, mbmsgs[0x0c22] )
				elif price != pySelItem.itemInfo.rolePrice :						# 价格有变动
					if not self.checkOperation_() : return
					itemInfo = pySelItem.itemInfo
					player = BigWorld.player()
					totalCost = self.getPurchaseTotalPrice()
					totalCost += ( price - itemInfo.rolePrice ) * itemInfo.amount
					if totalCost > player.money :									# 检查玩家是否够钱收购商品
						# "您没有足够的金钱收购物品。"
						self.showMessage_( 0x0ac3 )
						return
					itemDict = {}
					itemDict["maxCount"] = itemInfo.amount
					itemDict["id"] = itemInfo.id
					purchaseItem = self.createPurchaseItems_( OwnCollectionItem, \
																	itemDict, \
																	itemInfo.amount, \
																	price \
																)[0]
					purchaseItem.uid = itemInfo.uid
					BigWorld.player().cell.updateOwnCollectionItemInfo( purchaseItem )
		MoneyInputBox().show( changePrice,
							labelGather.getText( "vendwindow:VendPurchasePanel", "ipBoxNewPrice" ),
							self
							)



class PurchaseItem( BaseItem ) :

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def getIconItem_( self, item ) :
		return IconItem( item, self )

	def onRClick_( self, mode ) :
		"""
		右键点击物品时通知服务器玩家要取回该物品
		"""
		self.pyBinder.onItemRClick_( self, mode )



class IconItem( BaseObjectItem ) :

	def __init__( self, item, pyBinder = None ) :
		BaseObjectItem.__init__( self, item, pyBinder )
		self.focus = False

		self.dragMark = DragMark.VEND_PURCHASE_PANEL


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onDrop_( self, pyTarget, pyDropped ) :
		BaseObjectItem.onDrop_( self, pyTarget, pyDropped )
		dragMark = pyDropped.dragMark
		if dragMark == self.dragMark :										# 交换物品位置
			self.pyBinder.swapItemInfo_( pyDropped.pyBinder )
		elif dragMark == DragMark.KITBAG_WND :								# 从背包拖放物品
			self.pyBinder.pyBinder.onDrop_( pyTarget, pyDropped )
		return True


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getDescription( self ) :
		if self.itemInfo is None : return []
		dsp = BaseObjectItem._getDescription( self )[:]
		unitPrice = self.itemInfo.rolePrice
		totalPrice = unitPrice * self.itemInfo.amount
		costStr = utils.currencyToViewText( unitPrice )
		costStr = PL_Align.getSource( lineFlat = "M" ) + costStr
		costStr += PL_Align.getSource( "L" )
		costStr = labelGather.getText( "vendwindow:VendPurchaseIconItem", "dspUnitPrice" ) + costStr
		dsp.append( costStr )
		totalCostStr = utils.currencyToViewText( totalPrice )
		totalCostStr = PL_Align.getSource( lineFlat = "M" ) + totalCostStr
		totalCostStr += PL_Align.getSource( "L" )
		totalCostStr = labelGather.getText( "vendwindow:VendPurchaseIconItem", "dspTotalPrice" ) + totalCostStr
		dsp.append( totalCostStr )
		return dsp

	description = property( _getDescription, BaseObjectItem._setDescription )