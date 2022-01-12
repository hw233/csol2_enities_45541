# -*- coding: gb18030 -*-

from guis import *
from LabelGather import labelGather
from guis.controls.ODComboBox import ODComboBox
from guis.controls.TextBox import TextBox
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from VehicleComboItem import VehicleComboItem
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from guis.common.PyGUI import PyGUI
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from ItemsFactory import ObjectItem as ItemInfo
import csconst
import csstatus

class VehicleFeed( Window ):
	__instance = None
	
	def __init__( self ):
		assert VehicleFeed.__instance is None, "VehicleFeed instance has been created."
		VehicleFeed.__instance = self
		wnd = GUI.load( "guis/general/petswindow/vehiclePanel/vehicleFeed.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.addToMgr( "vehicleFeed" )
		self.__changeFoodNumCBID = 0
		self.__vehicleDBID = 0
		self.__foodItemInfo = {}
		
		self.__initialize( wnd )
	
	def __initialize( self, wnd ):
		labelGather.setLabel( wnd.lbTitle, "PetsWindow:VehicleFeed", "lbTitle" )
		
		self.__pyStFeedBefore = StaticText( wnd.panel.feedBefore )
		self.__pyStFeedBefore.text = ""
		
		self.__pyStFeedAfter = StaticText( wnd.panel.feedAfter )
		self.__pyStFeedAfter.text = "--"
		
		self.__foodItem = FoodItem( wnd.panel.foodItem )
		self.__foodItem.update( None )
		
		self.__pyCBFood = ODComboBox( wnd.panel.comboFood )
		self.__pyCBFood.autoSelect = False
		self.__pyCBFood.ownerDraw = True
		self.__pyCBFood.itemHeight = 25
		self.__pyCBFood.onViewItemInitialized.bind( self.onInitialized_ )
		self.__pyCBFood.onDrawItem.bind( self.onDrawItem_ )
		self.__pyCBFood.onItemSelectChanged.bind( self.__onFoodSelected )
		self.__pyCBFood.onBeforeDropDown.bind( self.__updateState )
		
		
		self.__pyTextBox = TextBox( wnd.panel.stFooNum.tbFood )
		self.__pyTextBox.inputMode = InputMode.INTEGER
		self.__pyTextBox.maxLength = 2
		self.__pyTextBox.onTextChanged.bind( self.__onTbTextChanged )
		self.__pyTextBox.text = ""
		
		self.__pyBtnUp = Button( wnd.panel.btnUp )
		self.__pyBtnUp.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnUp.onLMouseDown.bind( self.__onIncreaseFoodNum )
		
		self.__pyBtnDown = Button( wnd.panel.btnDown )
		self.__pyBtnDown.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnDown.onLMouseDown.bind( self.__onDecreaseFoodNum )
		
		self.__pyBtnBuy = HButtonEx( wnd.btnBuy )	#购买
		self.__pyBtnBuy.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnBuy.onLClick.bind( self.__onBuy )
		labelGather.setPyBgLabel( self.__pyBtnBuy, "PetsWindow:VehicleFeed", "btnBuyFood")
		
		self.__pyBtnOk = HButtonEx( wnd.btnOk )	#确定
		self.__pyBtnOk.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.onLClick.bind( self.__onFeed)
		labelGather.setPyBgLabel( self.__pyBtnOk, "PetsWindow:VehicleFeed", "btnOk")
		
		labelGather.setLabel( wnd.panel.feedBeforeText, "PetsWindow:VehicleFeed", "feedBeforeText" )
		labelGather.setLabel( wnd.panel.feedAfterText, "PetsWindow:VehicleFeed", "feedAfterText" )
		
	
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
	
	def __onFoodSelected( self, selIndex ):
		if selIndex < 0:
			self.__foodItem.update( None )
			self.__pyCBFood.pyBox_.text = ""
			self.__pyTextBox.text = ""
			return
		self.__pyCBFood.pyBox_.foreColor =255,255,255
		pyViewItem = self.__pyCBFood.pyViewItems[selIndex]
		selItem = pyViewItem.listItem
	
		if selItem is None:
			self.__foodItem.update( None )
			return
		itemID = self.__foodItemInfo[selItem]
		foodItem = BigWorld.player().createDynamicItem( itemID )
		itemInfo = ItemInfo( foodItem )
		self.__foodItem.update( itemInfo )
		self.__pyCBFood.pyBox_.text = selItem
		self.__resetFoodNum()
		#粮草数量默认选择了1
		self.__pyTextBox.text = "1"
		self.__updateAfterFullDegree()
	
	def __resetFoodNum( self ):
		self.__pyTextBox.text = ""
	
	def __onLastKeyUpEvent( self, key, mods ) :
		if key != KEY_LEFTMOUSE : return
		BigWorld.cancelCallback( self.__changeFoodNumCBID )
		LastKeyUpEvent.detach( self.__onLastKeyUpEvent )
			
	def __onIncreaseFoodNum( self ):
		BigWorld.cancelCallback( self.__changeFoodNumCBID )
		self.__changeFoodNum( True )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True
	
	def __onDecreaseFoodNum( self ):
		BigWorld.cancelCallback( self.__changeFoodNumCBID )
		self.__changeFoodNum( False )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True
		
	def __changeFoodNum( self, isIncrease ):
		oldFoodNum = int ( self.__pyTextBox.text or 0 )
		itemName = self.__pyCBFood.selItem
		if itemName is None:return
		itemID = self.__foodItemInfo[itemName]
		isExceed = oldFoodNum >= self.__getItemNumByID( itemID )
		if isIncrease:
			if oldFoodNum >= 99 or isExceed:
				return
		elif oldFoodNum <= 1:
			return
			
		self.__pyTextBox.text = str ( oldFoodNum + ( isIncrease and 1 or -1 ) )
		if BigWorld.isKeyDown( KEY_LEFTMOUSE ) :
			self.__changeFoodNumCBID = BigWorld.callback( 0.1, Functor( self.__changeFoodNum, isIncrease ) )
			
	def __updateState( self ):
#		self.__pyCBFood.pyBox_.text = ""
		for pyViewItem in self.__pyCBFood.pyViewItems:
			itemName = pyViewItem.listItem
			itemID = self.__foodItemInfo.get( itemName )
			itemNum = self.__getItemNumByID( itemID )
			if itemNum < 1:
				pyViewItem.enable = False 
			else:
				pyViewItem.enable = True
				
	def __setSelectTips( self ):
		self.__pyCBFood.pyBox_.foreColor =	180,180,180
		self.__pyCBFood.pyBox_.text = labelGather.getText( "PetsWindow:VehicleFeed","selectFoodTips" )
			
	def __getItemNumByID( self, itemID ):
		"""
		获取物品数量
		"""
		items = BigWorld.player().findItemsByIDFromNK( itemID )
		scount = 0
		for item in items:
			scount += item.getAmount()
		return scount
	
	def __updateAfterFullDegree( self ):
		fullDegree = 0
		itemName = self.__pyCBFood.selItem
		scount = int ( self.__pyTextBox.text or 0 )
		vehicleData = BigWorld.player().vehicleDatas.get( self.__vehicleDBID )
		fullDegree = vehicleData.get( "fullDegree", 0 )	
		if scount <= 0:
			self.__pyStFeedAfter.text = "--"
			return
		
		if itemName is not None:
			itemID = self.__foodItemInfo[itemName]	
			items = BigWorld.player().findItemsByIDFromNK( itemID )
			if len( items ) == 0:return
			fullDegreeTem = items[0].query( "fullDegree", 0 ) * scount	
			if int( time.time()) > vehicleData["fullDegree"]:	#之前饱腹度已过期
				fullDegree = fullDegreeTem  + int( time.time() )
			else:
				fullDegree = vehicleData.get( "fullDegree", 0 ) + fullDegreeTem
			
			maxFullDegree = int( time.time() ) + csconst.MAX_FULL_DEGREE
			if fullDegree > maxFullDegree:
				fullDegree = maxFullDegree
				BigWorld.player().statusMessage( csstatus.VEHICLE_FULL_DEGREE_UP_TO_MAX )
			
		self.__pyStFeedAfter.text = self.__getFullDegreeStr( fullDegree )
	
	def __getFullDegreeStr( self, fullDegree ):
		"""
		根据时间戳获取时间字符串
		"""
		timeStr = ""
		if fullDegree > time.time():
			ltFullDegree = time.localtime( fullDegree )
			timeStr = labelGather.getText( "PetsWindow:VehicleFeed", "timeText", ltFullDegree[0], ltFullDegree[1], ltFullDegree[2], ltFullDegree[3], ltFullDegree[4] )
		else:
			timeStr = labelGather.getText( "PetsWindow:VehicleFeed", "hungry" )
		return timeStr
			
	def __onTbTextChanged( self ):
		"""
		文本框数量改变回调
		"""
		itemName = self.__pyCBFood.selItem
		if itemName is None:return
		itemID = self.__foodItemInfo[itemName]
		if self.__pyTextBox.text == "-":return
		writeCount = int( self.__pyTextBox.text or 0 )
		playerCount = self.__getItemNumByID( itemID )
		if writeCount > playerCount:
			self.__pyTextBox.text = str( min( writeCount, playerCount ) )
		if writeCount < 0:
			self.__pyTextBox.text = str( max( 0, writeCount ) )
		self.__updateAfterFullDegree()
	
	def __onFeed( self ):
		itemName = self.__pyCBFood.selItem
		count = int( self.__pyTextBox.text or 0 )
		if itemName is None or count == 0:return
		itemID = self.__foodItemInfo[itemName]
		
		BigWorld.player().domesticateVehicle( self.__vehicleDBID, itemID, count )
			
	def __onBuy( self ):
		"""
		购买粮草
		"""
		itemID = csconst.VEHICLE_FOOD_ITEMID[0]
		ECenter.fireEvent("EVT_ON_QUERY_SHOP_ITEM",itemID, 4 )
				
	def __addCbItem ( self ):
		"""
		初始化粮草物品
		"""
		for itemID in csconst.VEHICLE_FOOD_ITEMID:
			player = BigWorld.player()
			item = player.createDynamicItem( itemID )
			itemName = item.name()
			self.__foodItemInfo[itemName] = itemID
			self.__pyCBFood.addItem( itemName )
		self.__updateState()
	
	def __setCurFullDeadtime( self, dbid ):
		"""
		更新饱腹度截止日期
		"""
		player = BigWorld.player()
		vehicleData = player.vehicleDatas.get( dbid )
		if vehicleData is None:return
		fullDegree = vehicleData["fullDegree"]		
		fullDegreeStr = self.__getFullDegreeStr( fullDegree )	
		self.__pyStFeedBefore.text = fullDegreeStr
		
	@staticmethod
	def instance():
		if VehicleFeed.__instance is None:
			VehicleFeed.__instance = VehicleFeed()
		return VehicleFeed.__instance
		
	def show( self, vehicleDBID ):
		Window.show( self )
		self.__vehicleDBID = vehicleDBID
		if not self.__foodItemInfo:
			self.__addCbItem()
		self.__setCurFullDeadtime( vehicleDBID )
		self.resetCBFood()
		self.__resetFoodNum()
		self.__setSelectTips()
		self.__updateAfterFullDegree()
	
	def onFeedSuccess( self ):
		"""
		"""
		self.__updateState()
		itemName = self.__pyCBFood.selItem
		if itemName is None:return
		itemID = self.__foodItemInfo[itemName]
		playerCount = self.__getItemNumByID( itemID )
#		if playerCount <= 0:
#			self.resetCBFood()
#			self.__pyTextBox.text = ""
#			return
#		writeCount = int( self.__pyTextBox.text or 0 )
#		if writeCount > playerCount:
#			self.__pyTextBox.text = str( min( writeCount, playerCount ) )
#		if writeCount < 0:
#			self.__pyTextBox.text = str( max( 0, writeCount ) )
		self.resetCBFood()
		self.__resetFoodNum()
		self.__setCurFullDeadtime( self.__vehicleDBID )
		self.__updateAfterFullDegree()
	
	def resetCBFood( self ):
		self.__pyCBFood.clearItems()
		self.__pyCBFood.selIndex = -1
		self.__addCbItem()
	
	def hide( self ):
		Window.hide( self )
		BigWorld.cancelCallback( self.__changeFoodNumCBID )
		self.__changeFoodNumCBID = 0
		self.__vehicleDBID = 0
	
	def onLeaveWorld( self ):
		self.resetCBFood()
		self.hide()

class FoodItem( PyGUI ):
	def __init__( self, item ):
		PyGUI.__init__( self, item )
		self.__pyItemBg = PyGUI( item.itemBg )
		self.__pyItem = VehicleFoodItem( item.item )

	def update( self, itemInfo ):
		self.__pyItem.update( itemInfo )

class VehicleFoodItem( BOItem ):
	def update( self, itemInfo ):
		BOItem.update( self, itemInfo )
		if itemInfo is None:
			self.description = labelGather.getText( "PetsWindow:VehicleFeed", "foodDsp" )

	def onDescriptionShow_( self ):
		if self.itemInfo is None:
			selfDsp = self.description
			toolbox.infoTip.showItemTips( self, selfDsp )
		else:
			BOItem.onDescriptionShow_( self )