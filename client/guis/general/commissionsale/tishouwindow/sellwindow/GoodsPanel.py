# -*- coding: gb18030 -*-

# implement the GoodsPanel class
# written by ganjinxing 2009-10-29

from guis import *
from guis.controls.TabCtrl import TabPanel
from guis.tooluis.inputbox.MoneyInputBox import MoneyInputBox
from guis.general.vendwindow.sellwindow.GoodsPanel import GoodsItem as BaseGoodsItem
from config.client.msgboxtexts import Datas as mbmsgs
from ItemsFactory import ObjectItem
from LabelGather import labelGather
import csdefine
import csconst
import time


class GoodsPanel( TabPanel ) :

	def __init__( self, tabPanel, pyBinder = None ):
		TabPanel.__init__( self, tabPanel, pyBinder )
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyItems = {}
		self.__pyMsgBox = None

		for name, item in tabPanel.children:
			if "item_" not in name : continue
			index = int( name.split( "_" )[1] )
			pyItem = GoodsItem( item, self )
			pyItem.index = index
			pyItem.update( None )
			self.__pyItems[index] = pyItem

	def __registerTriggers( self ):
		self.__triggers["EVT_ON_TISHOU_ITEM_SELLING"] = self.__receiveSellingItem
		self.__triggers["ON_REMOVE_COMMISSION_GOODS"] = self.__onSellingItemRemove
		self.__triggers["EVT_ON_TISHOU_ITEM_REMOVE"] = self.__onSellingItemRemove
		self.__triggers["EVT_ON_TAKE_BACK_TISHOU_ITEM"] = self.onTakeBackItem_
		self.__triggers["EVT_ON_TISHOU_ITEM_UPDATE"] = self.__onGoodsUpdatePrice
		self.__triggers["EVT_ON_ADD_TISHOU_ITEM_FROM_KITBAG"] = self.onAddSellItem_
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __getValidItem( self, index = -1 ) :
		"""
		获取一个可用的格子用于更新添加物品
		@param 		index : 指定索引，若为-1表示获取第一个可用格子
		"""
		if index < 0 :
			for pyItem in self.__pyItems.itervalues() :
				if pyItem.itemInfo is None :
					return pyItem
		else :
			return self.__pyItems.get( index, None )

	def __receiveSellingItem( self, baseItem, price ) :
		"""
		接收到服务器发来的寄售物品数据
		"""
		if not self.pyBinder.pyBinder.visible : return								# 不作这个限制可能会出现重复物品的情况
		pyValidItem = self.__getItemByUID( baseItem.uid )
		if pyValidItem is not None : return											# 物品已添在界面上，出现这种情况是因为重复快速地点击同一个NPC
		pyValidItem = self.__getValidItem()
		if pyValidItem is None :
			ERROR_MSG("Receive item %s from server but the panel is full!" % str( baseItem.id ))
			return
		newItemInfo = ObjectItem( baseItem )
		newItemInfo.rolePrice = price
		pyValidItem.update( newItemInfo )
		self.pyBinder.onCalcuExpense_()

	def __onSellingItemRemove( self, uid ) :
		pyItem = self.__getItemByUID( uid )
		if pyItem is not None :
			pyItem.update( None )
			self.pyBinder.enableChangePriceBtn()
			self.pyBinder.onCalcuExpense_()

	def __onGoodsUpdatePrice( self, uid, price ) :
		pyItem = self.__getItemByUID( uid )
		if pyItem is not None :
			itemInfo = pyItem.itemInfo
			itemInfo.rolePrice = price
			pyItem.update( itemInfo )
			self.pyBinder.onCalcuExpense_()

	def __getItemByUID( self, uid ) :
		"""
		根据UID获取物品信息
		"""
		for pyItem in self.__pyItems.itervalues() :
			if pyItem.itemInfo is None : continue
			if pyItem.itemInfo.uid == uid :
				return pyItem

	def __clearPanel( self ) :
		"""
		清空面板
		"""
		for pyItem in self.__pyItems.itervalues() :
			pyItem.update( None )
		self.pyBinder.onCalcuExpense_()
		self.pyBinder.enableChangePriceBtn()

	def __showMessage( self, msg ) :
		def query( result ) :
			self.__pyMsgBox = None
		if self.__pyMsgBox is not None :
			self.__pyMsgBox.hide()
		self.__pyMsgBox = showMessage( msg, "", MB_OK, query, None, Define.GST_IN_WORLD )

	def __checkOperation( self ) :
		tishouNPC = self.pyBinder.pyBinder.tishouNPC
		if tishouNPC is None : return
		isTishouState = tishouNPC.tsState
		if isTishouState :
			# "请先暂停寄售再进行该操作！"
			self.__showMessage( 0x0301 )
			return False
		return True

	def __queryTSGoodsInfo( self ) :
		"""
		向服务器申请查询寄售物品的数据
		"""
		self.__clearPanel()
		def queryInfo() :
			tishouNPC = self.pyBinder.pyBinder.tishouNPC
			if tishouNPC is not None :
				tishouNPC.cell.queryTSItems()
		if self.visible :
			queryInfo()
		else :
			BigWorld.callback( 0.3, queryInfo )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onAddSellItem_( self, kitbagID, gbIndex, index = -1 ) :
		"""
		添加一个待售物品
		"""
		if not self.__checkOperation() : return
		orderID = kitbagID * csdefine.KB_MAX_SPACE + gbIndex
		baseItem = BigWorld.player().getItem_( orderID )
		if baseItem is None : return
		if self.__getItemByUID( baseItem.uid ) is not None : return
		if not baseItem.canGive() :
			# 该物品不允许出售!
			showAutoHideMessage( 3.0, 0x0303, mbmsgs[0x0c22] )
			return
		def addItem( result, price ):
			if result == DialogResult.OK :
				if price <= 0:
					# "该物品还没有定价!"
					showAutoHideMessage( 3.0, 0x0304, mbmsgs[0x0c22] )
				else :
					if not self.__checkOperation() : return
					if BigWorld.player().testAddMoney( price ) > csconst.TRADE_PRICE_UPPER_LIMIT :				# 超过系统规定的金钱上限
						# "价格超出了上限！"
						self.__showMessage( 0x0302 )
						return
					pyValidItem = self.__getValidItem()
					if pyValidItem is None :
						# "寄售界面已装满!"
						showAutoHideMessage( 3.0, 0x0305, mbmsgs[0x0c22] )
					else :
						tishouNPC = self.pyBinder.pyBinder.tishouNPC
						if tishouNPC is not None :
							tishouNPC.cell.addTSItem( baseItem.uid, price )
		MoneyInputBox().show( addItem, labelGather.getText( "commissionsale:TiShouGoodsPanel", "ipBoxPrice" ), self )

	def onItemLClick_( self, pyItem, mode ) :
		"""
		界面上某个物品被点击
		"""
		pyCurrSelItem = self.getPySelItem()
		if pyCurrSelItem is not None :
			pyCurrSelItem.selected = False
		pyItem.selected = True
		self.pyBinder.enableChangePriceBtn()

	def onTakeBackItem_( self, uid ) :
		"""
		提供该接口给拖动一个物品直接取回的操作
		"""
		if not self.__checkOperation() : return
		pyItem = self.__getItemByUID( uid )
		if pyItem is None : return
		itemInfo = pyItem.itemInfo
		if itemInfo is None : return
		tishouNPC = self.pyBinder.pyBinder.tishouNPC
		if tishouNPC is not None :
			tishouNPC.cell.takeTSItem( itemInfo.uid, itemInfo.id, itemInfo.amount )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def changeItemPrice( self ) :
		if not self.__checkOperation() : return
		pySelItem = self.getPySelItem()
		if pySelItem is None : return
		def changePrice( res, price ):
			if res == DialogResult.OK:
				if price <= 0:
					# "物品未定价！"
					showAutoHideMessage( 3.0, 0x0304, mbmsgs[0x0c22] )
				elif price != pySelItem.itemInfo.rolePrice :			# 价格有变动
					if not self.__checkOperation() : return
					if BigWorld.player().testAddMoney( price ) > csconst.TRADE_PRICE_UPPER_LIMIT :		# 超过系统规定的金钱上限
						# "价格超出了上限！"
						self.__showMessage( 0x0302 )
						return
					uid = pySelItem.itemInfo.uid
					tishouNPC = self.pyBinder.pyBinder.tishouNPC
					if tishouNPC is not None :
						tishouNPC.cell.updateTSItemPrice( uid, price )
		MoneyInputBox().show( changePrice, labelGather.getText( "vendwindow:VendGoodsPanel", "ipBoxNewPrice" ), self )

	def canChangePrice( self ) :
		return self.getPySelItem() is not None

	def getTotalPrice( self ) :
		totalPrice = 0
		for pyItem in self.__pyItems.itervalues() :
			if pyItem.itemInfo is not None :
				totalPrice += pyItem.itemInfo.rolePrice
		return totalPrice

	def getSellItems( self ) :
		"""
		获取所有待售物品
		"""
		sellItems = []
		for pyItem in self.__pyItems.itervalues() :
			if pyItem.itemInfo is not None :
				sellItems.append( pyItem.itemInfo )
		return sellItems

	def getPySelItem( self ) :
		"""
		获取被选中的物品
		"""
		for pyItem in self.__pyItems.itervalues() :
			if pyItem.selected :
				return pyItem

	def onEvent( self, eventMacro, *args ) :
		"""
		"""
		self.__triggers[eventMacro]( *args )

	def onParentHide( self ) :
		pass

	def onParentShow( self ) :
		self.__queryTSGoodsInfo()
		if self.visible : self.onShow()

	def onTSNPCFlagChaned( self, oldFlag ) :
		pass

	def onShow( self ) :
		"""
		切换到物品出售页时，设置交易标记
		"""
		player = BigWorld.player()
		if player and player.isPlayer() :
			player.tradeState = csdefine.TRADE_TISHOU

	def onHide( self ) :
		"""
		物品出售页时关闭时，设置交易标记
		"""
		player = BigWorld.player()
		if player and player.isPlayer() :
			player.tradeState = csdefine.TRADE_NONE

	def reset( self ) :
		self.__clearPanel()

	def dispose( self ) :
		self.__triggers = {}
		TabPanel.dispose( self )

	def __del__( self ) :
		if Debug.output_del_TSGoodsPanel :
			INFO_MSG( str( self ) )


class GoodsItem( BaseGoodsItem ) :

	def __init__( self, item, pyBinder = None ) :
		BaseGoodsItem.__init__( self, item, pyBinder )
		self.pyBOItem_.dragMark = DragMark.TISHOU_SELL_PANEL
