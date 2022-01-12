# -*- coding: gb18030 -*-
#
# $Id: RedeemPanel.py,v 1.10 2008-08-19 06:11:20 fangpengjun Exp $
from guis import *
from guis.controls.Control import Control
from guis.controls.TabCtrl import TabPanel
from guis.controls.Button import Button
from WareItem import WareItem
from BuyPanel import ItemInfo
from LabelGather import labelGather
import GUIFacade

class RedeemPanel( TabPanel ):
	"""
	赎回物品界面
	"""

	_item_dragMark = DragMark.NPC_TRADE_REDEEM

	def __init__( self, itemsPanel = None ):
		TabPanel.__init__( self, itemsPanel )
		self.__pyItems = {}
		self.dropFocus = True
		self.__RedeemItems = [] #记录赎回物品列表
		self.__initItemsPanel( itemsPanel )
		self.__triggers = {}
		self.__registerTriggers()

	def __initItemsPanel( self, itemsPanel ):
		self.__pyRedeemBtn = Button( itemsPanel.redeemBtn )
		self.__pyRedeemBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyRedeemBtn.onLClick.bind( self.__onRedeem )

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setPyBgLabel( self.__pyRedeemBtn, "TradeWindow:redeemPanel", "btnRedeem" ) # 购回

		self.__initItems( itemsPanel )

	def __initItems( self, itemsPanel ):
		for name, item in itemsPanel.children:
			if "item_" not in name : continue
			index = int( name.split( "_" )[1] )
			pyItem = WareItem( item, self._item_dragMark, self )
			pyItem.index = index
			self.__pyItems[index] = pyItem
	# -----------------------------------------------------------
	# private
	# -----------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_REDEEM_INFO_CHANGED"] = self.__onRedeemChange
		self.__triggers["EVT_ON_REDEEM_REEDEM_ITEM"] =  self.__onRedeemItem
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( key, self )
	# -------------------------------------------------------
	def __onRedeem( self ):# 赎回
		for pyItem in self.__pyItems.itervalues():
			if pyItem.selected:
				GUIFacade.redeemItem( pyItem.uid )

	def __onRedeemChange( self, index, itemInfo ):
		if self.__pyItems.has_key( index ):
			itemInfo = ItemInfo( itemInfo, index )
			self.__pyItems[index].update( itemInfo  )

	def __onRedeemItem( self, uid, itemInfo ):
		itemList = []
		for index, item in self.__pyItems.iteritems():
			if item.uid == uid:
				if not itemInfo:
					item.selected = False
				itemInfo = ItemInfo( itemInfo, index )
				self.__pyItems[index].update( itemInfo )
			if item.getObjectItem().itemInfo:
				itemList.append( item.getObjectItem() )
		while len( itemList ) < 7:
			itemList.append( None )

		for index, item in self.__pyItems.iteritems():
			item.selected = False
			if itemList[index]:
				itemInfo = ItemInfo( itemList[index].itemInfo, index )
				self.__pyItems[index].update( itemInfo )
			else:
				itemInfo = ItemInfo( None, index )
				self.__pyItems[index].update( itemInfo )

	def __onReSetItem( self, itemInfo ):
		"""
		进入到这个函数时，说明赎回物品界面已在此前被清空
		"""
		for index, item in self.__pyItems.iteritems():
			if item.uid < 0 or item.uid == itemInfo.uid:
				itemInfo = ItemInfo( itemInfo, index )
				self.__pyItems[index].update( itemInfo )
				break

	# --------------------------------------------------------
	# public
	# --------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def reSetItem( self, itemInfo ):
		self.__onReSetItem( itemInfo )

	def clearItems( self ):
		for index, item in self.__pyItems.iteritems():
			itemInfo = ItemInfo( None, index )
			item.update( itemInfo )

	def addRedeemItem( self, pyItem ):
		if pyItem not in self.__RedeemItems:
			self.__RedeemItems.append( pyItem )

	def areItemsEmpty( self ):
		"""
		判断面板中是否还有可赎回物品
		"""
		for index, item in self.__pyItems.iteritems():
			if item.uid >= 0:
				return False
		return True

	def delRedeemItem( self, pyItem ):
		if pyItem in self.__RedeemItems:
			self.__RedeemItems.remove( pyItem )
	
	def initePanelBorder( self ):
		parentGui = self.pyTopParent.getGui()
		rt = parentGui.elements["frm_rt"]
		r = parentGui.elements["frm_r"]
		rb = parentGui.elements["frm_rb"]
		rTop = rt.position.y + rt.size.y
		r.position.y = rTop - 1.0
		r.size.y = rb.position.y - rTop


