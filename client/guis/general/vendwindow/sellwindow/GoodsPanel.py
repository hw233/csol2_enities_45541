# -*- coding: gb18030 -*-
# implement the GoodsPanel class
# written by ganjinxing 2009-10-29

from guis import *
from guis.controls.Control import Control
from guis.controls.TabCtrl import TabPanel
from guis.controls.BaseObjectItem import BaseObjectItem
from guis.tooluis.richtext_plugins.PL_Align import PL_Align
from guis.tooluis.inputbox.MoneyInputBox import MoneyInputBox
from config.client.msgboxtexts import Datas as mbmsgs
from ItemsFactory import ObjectItem
from LabelGather import labelGather
from guis.MLUIDefine import ItemQAColorMode
import csdefine
import csconst

class VendGoodsPanel( TabPanel ) :

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
		self.__triggers["EVT_ON_VEND_ADD_ITEM"] = self.onAddSellItem_
		self.__triggers["EVT_ON_KITBAG_UPDATE_ITEM"] = self.__onKitbagUpdateItem
		self.__triggers["EVT_ON_KITBAG_REMOVE_ITEM"] = self.__onKitbagRemoveItem
		self.__triggers["EVT_ON_ITEM_EQUIPED"] = self.__onKitbagRemoveItem
		self.__triggers["EVT_ON_VEND_ITEM_SELLED"] = self.__onSellingItemRemove
		self.__triggers["EVT_ON_VEND_ADD_ITEM_INDEX"] = self.onAddSellItem_
		self.__triggers["EVT_ON_TAKE_BACK_VEND_ITEM"] = self.onTakeBackItem_
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

	def __receiveSellingItem( self, baseItem, price, index = -1 ) :
		"""
		接收到寄售物品数据
		"""
		if not self.pyBinder.pyBinder.visible : return						# 不作这个限制可能会出现重复物品的情况
		pyValidItem = self.__getValidItem( index )
		if pyValidItem is None :
			ERROR_MSG("Receive item %s from server but the panel is full!" % str( baseItem.id ))
			return
		newItemInfo = ObjectItem( baseItem )
		newItemInfo.rolePrice = price
		pyValidItem.update( newItemInfo )
		self.pyBinder.onCalcuExpense_()

	def __onKitbagUpdateItem( self, itemInfo ) :
		"""
		当背包更新一个物品时调用
		"""
		pyItem = self.__getItemByUID( itemInfo.uid )
		if pyItem is not None :
			itemInfo.rolePrice = pyItem.itemInfo.rolePrice
			pyItem.update( itemInfo )

	def __onKitbagRemoveItem( self, itemInfo ) :
		"""
		背包移除一个物品时调用
		"""
		self.__onSellingItemRemove( itemInfo.uid )

	def __onSellingItemRemove( self, uid ) :
		pyItem = self.__getItemByUID( uid )
		if pyItem is not None :
			itemInfo = pyItem.itemInfo
			kitbagID = itemInfo.kitbagID
			if kitbagID > -1 :
				orderID = itemInfo.orderID
				ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", kitbagID, orderID, False ) 	# 解锁物品
			pyItem.update( None )
			self.pyBinder.onCalcuExpense_()
			self.pyBinder.enableChangePriceBtn()

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

	def __showMessage( self, msg ) :
		def query( result ) :
			self.__pyMsgBox = None
		if self.__pyMsgBox is not None :
			self.__pyMsgBox.hide()
		self.__pyMsgBox = showMessage( msg, "", MB_OK, query, None, Define.GST_IN_WORLD )

	def __checkOperation( self ) :
		isVendState = BigWorld.player().state == csdefine.ENTITY_STATE_VEND
		if isVendState :
			# "请先停止摆摊再进行该操作！"
			self.__showMessage( 0x0aa1 )
			return False
		return True

	def __colourItems( self, locked ) :
		"""
		打开/关闭界面时改变背包中对应物品的颜色
		"""
		for pyItem in self.__pyItems.itervalues():
			if pyItem.itemInfo is None: continue
			kitbagID = pyItem.itemInfo.kitbagID
			orderID = pyItem.itemInfo.orderID
			ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", kitbagID, orderID, locked )


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
			# "该物品不允许出售!"
			showAutoHideMessage( 3.0, 0x0aa2, mbmsgs[0x0c22] )
			return
		def addItem( result, price ) :
			if result == DialogResult.OK :
				if price <= 0:
					# "该物品还没有定价!"
					showAutoHideMessage( 3.0, 0x0aa3, mbmsgs[0x0c22] )
				else :
					pyValidItem = self.__getValidItem( index )
					if pyValidItem is None :
						# "物品界面已装满!"
						showAutoHideMessage( 3.0, 0x0aa4, mbmsgs[0x0c22] )
					else :
						if not self.__checkOperation() : return
						if BigWorld.player().testAddMoney( price ) > 0 :				# 超过系统规定的金钱上限
							# "价格超出了上限！"
							self.__showMessage( 0x0aa6 )
							return
						orgItemInfo = pyValidItem.itemInfo
						if orgItemInfo is not None :							# 解锁被覆盖物品
							orgKitbagID = orgItemInfo.kitbagID
							orgOrderID	= orgItemInfo.orderID
							ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", orgKitbagID, orgOrderID, False )
						else :													# 锁定物品
							ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", kitbagID, gbIndex, True )
						self.__receiveSellingItem( baseItem, price, index )
		MoneyInputBox().show( addItem, labelGather.getText( "vendwindow:VendGoodsPanel", "ipBoxPrice" ), self )

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
		self.__onSellingItemRemove( uid )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def canChangePrice( self ) :
		return self.getPySelItem() is not None

	def getTotalPrice( self ) :
		totalPrice = 0
		for pyItem in self.__pyItems.itervalues() :
			if pyItem.itemInfo is not None :
				totalPrice += pyItem.itemInfo.rolePrice
		return totalPrice

	def changeItemPrice( self ) :
		if not self.__checkOperation() : return
		pySelItem = self.getPySelItem()
		if pySelItem is None : return
		def changePrice( res, price ):
			if res == DialogResult.OK:
				if price <= 0:
					# "物品未定价！"
					showAutoHideMessage( 3.0, 0x0aa3, mbmsgs[0x0c22] )
				elif price != pySelItem.itemInfo.rolePrice :			# 价格有变动
					if not self.__checkOperation() : return
					if BigWorld.player().testAddMoney( price ) > 0 :			# 超过系统规定的金钱上限
						# "价格超出了上限！"
						self.__showMessage( 0x0aa6 )
						return
					uid = pySelItem.itemInfo.uid
					self.__onGoodsUpdatePrice( uid, price )
		MoneyInputBox().show( changePrice, labelGather.getText( "vendwindow:VendGoodsPanel", "ipBoxNewPrice" ), self )

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

	def onRoleTradeStateChanged( self, state ) :
		pass

	def onEvent( self, eventMacro, *args ) :
		"""
		"""
		self.__triggers[eventMacro]( *args )

	def onParentHide( self ) :
		self.__colourItems( False )

	def onParentShow( self ) :
		self.__colourItems( True )
		if self.visible : self.onShow()

	def onShow( self ) :
		"""
		切换到物品出售页时，设置交易标记
		"""
		player = BigWorld.player()
		if player and player.isPlayer() :
			player.tradeState = csdefine.ENTITY_STATE_VEND

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


class GoodsItem( Control ) :

	__SELECTED_FLAG = None

	def __init__( self, item, pyBinder = None ) :
		Control.__init__( self, item, pyBinder )
		self.focus = True

		if GoodsItem.__SELECTED_FLAG is None :
			GoodsItem.__SELECTED_FLAG = GUI.load( "guis/general/vendwindow/sellwindow/selected_cover.gui" )
			uiFixer.firstLoadFix( GoodsItem.__SELECTED_FLAG )

		self.pyBOItem_ = self.getIconItem_( item.item )

		self.selected = False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def getIconItem_( self, item ) :
		return IconItem( item, self )

	def onRClick_( self, mode ) :
		"""
		右键点击物品时通知服务器玩家要取回该物品
		"""
		self.pyBinder.onTakeBackItem_( self.itemInfo.uid )

	def onLClick_( self, mode ) :
		"""
		左键点击物品则将该物品设为选中状态
		"""
		self.pyBinder.onItemLClick_( self, mode )

	def swapItemInfo_( self, pySrcItem ) :
		"""
		两个物品互换位置
		"""
		if self == pySrcItem or \
		not isinstance( pySrcItem, GoodsItem ) : return
		srcItemInfo = pySrcItem.itemInfo
		srcSelected = pySrcItem.selected
		pySrcItem.update( self.itemInfo )
		pySrcItem.selected = self.selected
		self.update( srcItemInfo )
		self.selected = srcSelected


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		self.pyBOItem_.update( itemInfo )
		quality = 1															# 默认显示白色品质
		if itemInfo is not None :
			quality = itemInfo.quality
			self.focus = True
		else :
			self.focus = False
			self.selected = False
		util.setGuiState( self.gui, ( 4, 2 ), ItemQAColorMode[quality] )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getItemInfo( self ) :
		return self.pyBOItem_.itemInfo

	def _getSelected( self ) :
		return hasattr( self.gui, "sel_cover" )

	def _setSelected( self, selected ) :
		if selected :
			self.gui.addChild( GoodsItem.__SELECTED_FLAG, "sel_cover" )
		else :
			self.gui.delChild( "sel_cover" )

	itemInfo = property( _getItemInfo )										# 获取物品信息
	selected = property( _getSelected, _setSelected )						# 获取选中状态


class IconItem( BaseObjectItem ) :

	def __init__( self, item, pyBinder = None ) :
		BaseObjectItem.__init__( self, item, pyBinder )
		self.focus = False

		self.dragMark = DragMark.VEND_SELL_WND


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onDrop_( self, pyTarget, pyDropped ) :
		BaseObjectItem.onDrop_( self, pyTarget, pyDropped )
		dragMark = pyDropped.dragMark
		if dragMark == self.dragMark :										# 交换物品位置
			self.pyBinder.swapItemInfo_( pyDropped.pyBinder )
		elif dragMark == DragMark.KITBAG_WND :								# 从背包拖放物品
			kitbagID = pyDropped.kitbagID
			gbIndex = pyDropped.gbIndex
			index = pyTarget.pyBinder.index
			self.pyBinder.pyBinder.onAddSellItem_( kitbagID, gbIndex, index )
			# 需要把物品发到服务器，待服务器回调后才能添加到界面
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getDescription( self ) :
		if self.itemInfo is None : return []
		dsp = BaseObjectItem._getDescription( self )[:]
		costStr = utils.currencyToViewText( self.itemInfo.rolePrice )
		costStr = PL_Align.getSource( lineFlat = "M" ) + costStr
		costStr += PL_Align.getSource( "L" )
		costStr = labelGather.getText( "vendwindow:VendGoodsIconItem", "price" ) + costStr
		dsp.append( costStr )
		return dsp

	description = property( _getDescription, BaseObjectItem._setDescription )
