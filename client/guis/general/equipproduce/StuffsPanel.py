# -*- coding: gb18030 -*-
#
# $Id: StuffsPanel.py,v 1.8 2008-08-25 09:40:56 fangpengjun Exp $

from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.ItemsPanel import ItemsPanel
from guis.controls.Control import Control
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from config.client.msgboxtexts import Datas as mbmsgs
from guis.MLUIDefine import ItemQAColorMode
import event.EventCenter as ECenter

class StuffsPanel( PyGUI ):
	def __init__( self, materialsPanel ):
		PyGUI.__init__( self, materialsPanel )
		self.__initStuffItems( materialsPanel )

	def __initStuffItems( self, materialsPanel ):
		self.__pyItems = {}
		for name, item in materialsPanel.children:
			if "item_" not in name : continue
			index = int( name.split( "_" )[1] )
			pyItem = SuffItem( item, index )
			self.__pyItems[index] = pyItem

	def update( self, itemInfo, index ):
		if self.__pyItems.has_key( index ):
			pyItem = self.__pyItems[index]
			pyItem.update( itemInfo )

	def getSameStuffs( self, stuffID ):
		sameStuffs = []
		for stuffItem in self.__pyItems.itervalues():
			if stuffItem.itemInfo is None:continue
			if stuffItem.itemInfo.id == stuffID:
				sameStuffs.append( stuffItem )
		return sameStuffs

	def getStuffNum( self, index ):
		if self.__pyItems.has_key( index ):
			stuff = self.__pyItems[index]
			itemInfo = stuff.itemInfo
			if itemInfo is None:return
			count = itemInfo.amount
			return count

	def removeItem( self, kitbagID, orderID ):
		for stuffItem in self.__pyItems.itervalues():
			if stuffItem.itemInfo is None:continue
			if stuffItem.kitbagID == kitbagID and stuffItem.orderID == orderID:
				ECenter.fireEvent( "EVT_ON_REMOVE_STUFF_ITEM", kitbagID, orderID, stuffItem.index )
				stuffItem.update( None )

	def getStuffPanelIndex( self, kitbagID, orderID ):
		for stuffItem in self.__pyItems.itervalues():
			if stuffItem.itemInfo is None:continue
			if stuffItem.kitbagID == kitbagID and stuffItem.orderID == orderID:
				return stuffItem.index
		return -1

	def swapItemsUpdateOrders( self, srcKitbagID, srcIndex, dstKitbagID, dstIndex ):
		"""
		包裹内物品换位或者包裹位上包裹换位的处理
		"""
		for stuffItem in self.__pyItems.itervalues():
			if stuffItem.itemInfo is None : continue
			if srcIndex == -1 : srcIndex = stuffItem.orderID
			if dstIndex == -1 : dstIndex = stuffItem.orderID
			if stuffItem.kitbagID == srcKitbagID and stuffItem.orderID == srcIndex:
				stuffItem.kitbagID = dstKitbagID
				stuffItem.orderID = dstIndex
				ECenter.fireEvent( "EVT_ON_KITBAG_UPDATE_STUFF_ORDERS", srcKitbagID, dstKitbagID, srcIndex, dstIndex )
			elif stuffItem.kitbagID == dstKitbagID and stuffItem.orderID == dstIndex:
				stuffItem.kitbagID = srcKitbagID
				stuffItem.orderID = srcIndex
				ECenter.fireEvent( "EVT_ON_KITBAG_UPDATE_STUFF_ORDERS", dstKitbagID, srcKitbagID, dstIndex, srcIndex )

	def getStuffID( self, index ): # 通过索引获得材料ID
		if self.__pyItems.has_key( index ):
			stuff = self.__pyItems[index]
			itemInfo = stuff.itemInfo
			if itemInfo is None:return
			id = itemInfo.id
			return id

	def getStuffInfos( self ):
		stuffInfos = []
		for pyItem in self.__pyItems.itervalues():
			itemInfo = pyItem.itemInfo
			if not itemInfo is None:
				stuffInfos.append( itemInfo )
		return stuffInfos

	def getItemFromKitBag( self, itemInfo ):
		for pyItem in self.__pyItems.itervalues():
			if not pyItem.itemInfo:
				pyItem.update( itemInfo )
				break

	def clear( self ):
		for pyItem in self.__pyItems.itervalues():
			pyItem.update( None )

# -------------------------------------------------------
# SuffItem
# -------------------------------------------------------
class SuffItem( PyGUI ):
	def __init__( self, item, index ):
		PyGUI.__init__( self, item )
		self.__pyItem = Item( item.item, index )
		self.index = index
	
	def update( self, itemInfo ):
		self.__pyItem.update( itemInfo )
		if itemInfo:
			quality = itemInfo.quality
			util.setGuiState( self.getGui(), ( 4, 2 ), ItemQAColorMode[quality] )
		else:
			util.setGuiState( self.getGui(), ( 4, 2 ), ItemQAColorMode[0] )

	def _getKitbagID( self ):
		return self.__pyItem.kitbagID

	def _getOrderID( self ):
		return self.__pyItem.orderID
			
	def _getItemInfo( self ):
		
		return self.__pyItem.itemInfo
		
	kitbagID = property( _getKitbagID )
	orderID = property( _getOrderID )		
	itemInfo = property( _getItemInfo )
		
class Item( BOItem ):
	def __init__( self , stuffItem, index ):
		BOItem.__init__( self, stuffItem )
		self.__kitbagID = -1
		self.__orderID = -1
		self.dropFocus = True
		self.__itemInfo = None
		self.index = index

	def dispose( self ):
		BOItem.dispose( self )

	def __fromKitbagWindow( self, pyTarget, pyDropped ) :
		srckitBag = pyDropped.kitbagID
		scrorder = pyDropped.gbIndex
		dstindex = pyTarget.index
		if self.__kitbagID != -1 and self.__orderID != -1:#如果材料栏已经有材料，要先移除这个材料
			ECenter.fireEvent( "EVT_ON_REPLACE_STUFF_ITEM", self.__kitbagID, self.__orderID, dstindex, srckitBag, scrorder )
		ECenter.fireEvent( "EVT_ON_ADD_STUFF_ITEM", srckitBag, scrorder, dstindex )

	def onDrop_( self, pyTarget, pyDropped ):
		BOItem.onDrop_( self, pyTarget, pyDropped )
		dragMark = pyDropped.dragMark
		if dragMark != DragMark.KITBAG_WND : return
		self.__fromKitbagWindow( pyTarget, pyDropped )
		return True

	def onDragStop_( self, pyDragged ):
		BOItem.onDragStop_( self, pyDragged )
		if pyDragged.itemInfo is None:return
		kitbagID = pyDragged.kitbagID
		orderID = pyDragged.orderID
		if not ruisMgr.isMouseHitScreen() : return False
		name = pyDragged.itemInfo.name()
		def query( rs_id ):
			if rs_id == RS_OK:
				ECenter.fireEvent( "EVT_ON_REMOVE_STUFF_ITEM", kitbagID, orderID, pyDragged.index )
		# "确定移除材料%s?"
		showMessage( mbmsgs[0x0361] % name, "", MB_OK_CANCEL, query )
		return True

	def onRClick_( self, mods ) :
		BOItem.onRClick_( self, mods )
		if self.itemInfo is None : return
		ECenter.fireEvent( "EVT_ON_REMOVE_STUFF_ITEM", self.kitbagID, self.orderID, self.index )

	def update( self, itemInfo ):
		BOItem.update( self, itemInfo )
		self.itemInfo = itemInfo
		if itemInfo is not None:
			self.__kitbagID = itemInfo.kitbagID
			self.__orderID = itemInfo.orderID
		else:
			self.__kitbagID = -1
			self.__orderID = -1

	def _getKitbagID( self ):
		return self.__kitbagID

	def _setKitbagID( self, kitbagID ):
		self.__kitbagID = kitbagID

	def _getOrderID( self ):
		return self.__orderID

	def _setOrderID( self, orderID ):
		self.__orderID = orderID

	def _getItemInfo( self ):
		return self.__itemInfo

	def _setItemInfo( self, itemInfo ):
		self.__itemInfo = itemInfo

	kitbagID = property( _getKitbagID, _setKitbagID )
	orderID = property( _getOrderID, _setOrderID )
	itemInfo = property( _getItemInfo, _setItemInfo )