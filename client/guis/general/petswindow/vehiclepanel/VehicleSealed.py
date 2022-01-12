# -*- coding: gb18030 -*-

from guis import *
from guis.common.Window import Window
from LabelGather import labelGather
from guis.controls.ODComboBox import ODComboBox
from guis.controls.ButtonEx import HButtonEx
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.tooluis.CSRichText import CSRichText
from VehicleComboItem import VehicleComboItem
from ItemsFactory import ObjectItem as ItemInfo
import csconst

class VehicleSealed( Window ):
	__instance = None
	
	def __init__( self ):
		assert VehicleSealed.__instance is None, "VehicleSealed instance has been created."
		VehicleSealed.__instance = self
		wnd = GUI.load( "guis/general/petswindow/vehiclePanel/vehicleSealed.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.addToMgr( "vehicleSealed" )
		self.__sealedItemInfo = {}
		self.__vehicleDBID = 0
		
		self.__initialize( wnd )
		
	def __initialize( self, wnd ):
		labelGather.setLabel( wnd.lbTitle, "PetsWindow:VehicleSealed", "lbTitle" )
		
		self.__pySealedItem = SealedItem( wnd.panel.sealedItem.item )
		self.__pySealedItem.update( None )
		
		self.__pyCBSealed = ODComboBox( wnd.panel.comboSealed )
		self.__pyCBSealed.autoSelect = False
		self.__pyCBSealed.ownerDraw = True
		self.__pyCBSealed.itemHeight = 25
		self.__pyCBSealed.onViewItemInitialized.bind( self.onInitialized_ )
		self.__pyCBSealed.onDrawItem.bind( self.onDrawItem_ )
		self.__pyCBSealed.onItemSelectChanged.bind( self.__onSealedItemSelected )
		self.__pyCBSealed.onBeforeDropDown.bind( self.__updateSealedItem )
		
		self.__pyBtnBuy = HButtonEx( wnd.panel.btnBuy )	#购买
		self.__pyBtnBuy.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnBuy.onLClick.bind( self.__onBuy )
		labelGather.setPyBgLabel( self.__pyBtnBuy, "PetsWindow:VehicleSealed", "btnBuy")
		
		self.__pyBtnOk = HButtonEx( wnd.btnOk )	#确定
		self.__pyBtnOk.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.onLClick.bind( self.__onSealed )
		labelGather.setPyBgLabel( self.__pyBtnOk, "PetsWindow:VehicleSealed", "btnOk")

		self.__pyLbText = CSRichText( wnd.panel.lbText )
		self.__pyLbText.text = labelGather.getText( "PetsWindow:VehicleSealed", "lbText" )

	def onInitialized_( self, pyViewItem ):
		pyVehicleItem = VehicleComboItem()
		pyVehicleItem.focus = False
		pyVehicleItem.crossFocus = False
		pyViewItem.addPyChild( pyVehicleItem )
		pyViewItem.pyVehicleItem = pyVehicleItem
	
	def onDrawItem_( self, pyViewItem ):
		pyPanel = pyViewItem.pyPanel
		if pyViewItem.selected :
			pyViewItem.pyVehicleItem.foreColor = pyPanel.itemSelectedForeColor			# 选中状态下的前景色
			pyViewItem.color = pyPanel.itemSelectedBackColor				# 选中状态下的背景色
		elif pyViewItem.highlight :
			pyViewItem.pyVehicleItem.foreColor = pyPanel.itemHighlightForeColor		# 高亮状态下的前景色
			pyViewItem.color = pyPanel.itemHighlightBackColor				# 高亮状态下的背景色
		else :
			pyViewItem.pyVehicleItem.foreColor = pyPanel.itemCommonForeColor
			pyViewItem.color = pyPanel.itemCommonBackColor
		pyVehicleItem = pyViewItem.pyVehicleItem
		pyVehicleItem.left = 1.0
		pyVehicleItem.top = 1.0
		pyVehicleItem.text = pyViewItem.listItem
		
	def __onSealedItemSelected( self, selIndex ):
		if selIndex < 0:
			self.__pySealedItem.update( None )
			self.__pyCBSealed.pyBox_.text = ""
			return
		self.__pyCBSealed.pyBox_.foreColor = 255,255,255
		pyViewItem = self.__pyCBSealed.pyViewItems[selIndex]
		selItem = pyViewItem.listItem
	
		if selItem is None:
			self.__pySealedItem.update( None )
			return
		itemID = self.__sealedItemInfo[selItem]
		sealedItem = BigWorld.player().createDynamicItem( itemID )
		itemInfo = ItemInfo( sealedItem )
		self.__pySealedItem.update( itemInfo )
		self.__pyCBSealed.pyBox_.text = selItem
		
	def __updateState( self ):
		for pyViewItem in self.__pyCBSealed.pyViewItems:
			itemName = pyViewItem.listItem
			itemID = self.__sealedItemInfo.get( itemName )
			itemNum = self.__getItemNumByID( itemID )
			if itemNum < 1:
				pyViewItem.enable = False 
			else:
				pyViewItem.enable = True
	
	def __getItemNumByID( self, itemID ):
		"""
		获取物品数量
		"""
		items = BigWorld.player().findItemsByIDFromNK( itemID )
		scount = 0
		for item in items:
			scount += item.getAmount()
		return scount
		
	def __onBuy( self ):
		"""
		"""
		player = BigWorld.player()
		vehicleData = player.vehicleDatas.get( self.__vehicleDBID )
		if vehicleData is None:return
		step = vehicleData["step"]
		itemID	 = csconst.VEHICLE_SEALED_NEED_ITEM[step]
		ECenter.fireEvent("EVT_ON_QUERY_SHOP_ITEM",itemID, 4 )
		
	def __onSealed( self ):
		"""
		封灵
		"""
		itemName = self.__pyCBSealed.selItem
		if self.__sealedItemInfo.has_key( itemName ):
			itemID = self.__sealedItemInfo[ itemName ]
			BigWorld.player().vehicleToItem( self.__vehicleDBID, itemID )
		self.__updateSealedItem()
	
	def __updateSealedItem ( self ):
		"""
		初始化封灵需要物品
		"""
#		self.__pyCBSealed.pyBox_.text = ""
		self.__pyCBSealed.clearItems()
		self.__pyCBSealed.selIndex = -1
		self.__sealedItemInfo = {}
		player = BigWorld.player()
		vehicleData = player.vehicleDatas.get( self.__vehicleDBID )
		if vehicleData is None:return
		step = vehicleData["step"]
		itemID = csconst.VEHICLE_SEALED_NEED_ITEM.get( step,0 )
		item = player.createDynamicItem( itemID )
		if item is not None:
			itemName = item.name()
			self.__sealedItemInfo[itemName] = itemID
			self.__pyCBSealed.addItem( itemName )
			self.__updateState()
	
	def __setSelectTips( self ):
		self.__pyCBSealed.pyBox_.foreColor = 180,180,180
		self.__pyCBSealed.pyBox_.text = labelGather.getText( "PetsWindow:VehicleSealed","selectStoneTips" ) 
	
	@staticmethod
	def instance():
		if VehicleSealed.__instance is None:
			VehicleSealed.__instance = VehicleSealed()
		return VehicleSealed.__instance
		
	def show( self, vehicleDBID ):
		Window.show( self )
		self.__vehicleDBID = vehicleDBID
		self.__setSelectTips()
			
	def hide( self ):
		Window.hide( self )
		self.__vehicleDBID = 0
		
	def onLeaveWorld( self ):
		self.hide()

class SealedItem( BOItem ):
	def update( self, itemInfo ):
		BOItem.update( self, itemInfo )
		if itemInfo is None:
			self.description = labelGather.getText( "PetsWindow:VehicleSealed", "stoneDsp" )

	def onDescriptionShow_( self ):
		if self.itemInfo is None:
			selfDsp = self.description
			toolbox.infoTip.showItemTips( self, selfDsp )
		else:
			BOItem.onDescriptionShow_( self )
