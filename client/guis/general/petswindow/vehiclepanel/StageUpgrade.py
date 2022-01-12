# -*- coding:utf-8 -*-

from guis import *
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.ODComboBox import ODComboBox
from guis.common.PyGUI import PyGUI
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from ItemsFactory import ObjectItem as ItemInfo
from guis.controls.ButtonEx import HButtonEx
from guis.controls.ComboBox import ComboItem
from LabelGather import labelGather
from VehicleRender import VehicleRender
from VehicleComboItem import VehicleComboItem
import csconst
from VehicleHelper import getVehicleMaxStep
import csstatus
import csdefine

class StageUpgrade( Window ):
	__instance = None
	
	def __init__( self ):
		assert StageUpgrade.__instance is None, "StageUpgrade instance has been created!"
		StageUpgrade.__instance = self
		wnd = GUI.load( "guis/general/petswindow/vehiclePanel/upStage.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.addToMgr( "stageUpgrade" )
#		self.__allModels = {}
		self.__turnModelCBID = 0
		self.__initialize( wnd )
		
	def __initialize( self, wnd ):
		labelGather.setLabel( wnd.lbTitle, "PetsWindow:VehicleUpgrade", "lbTitle" )
		
		self.__pyStVehicleName = StaticText( wnd.vehicleName )
		self.__pyStVehicleName.text = ""
		
		self.__pyStStage = StaticText( wnd.stepInfo )
		self.__pyStStage.text = ""
		
		self.__pyStSuccessRate = StaticText( wnd.panel.successRate )
		self.__pyStSuccessRate.text = labelGather.getText( "PetsWindow:VehicleUpgrade","successRate","0" )
		
		self.__pyBtnLeft = Button( wnd.btnLeft ) #向左转动模型
		self.__pyBtnLeft.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnLeft.onLMouseDown.bind( self.__onTurnLeft )

		self.__pyBtnRight = Button( wnd.btnRight ) #向右转动模型
		self.__pyBtnRight.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnRight.onLMouseDown.bind( self.__onTurnRight )
		
		self.__pyBtnOk = HButtonEx( wnd.btnOk )	#升阶
		self.__pyBtnOk.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.onLClick.bind( self.__onUpStage )
		labelGather.setPyBgLabel( self.__pyBtnOk, "PetsWindow:VehicleUpgrade", "btnOk")
		
		self.__pyBtnBuy = HButtonEx( wnd.panel.btnBuy )	#购买
		self.__pyBtnBuy.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnBuy.onLClick.bind( self.__onBuy )
		labelGather.setPyBgLabel( self.__pyBtnBuy, "PetsWindow:VehicleUpgrade", "btnBuy")
		
		self.__pyVehicleRender = VehicleRender( wnd.vehicleRender )
		
		self.__pyVehicleItem = ConsumeItem( wnd.panel.vehicleItem )	#祭品骑宠
		self.__pyVehicleItem.update( None )
		
		self.__pyPropItem = PropItem( wnd.panel.propItem )	#消耗宠物道具
		self.__pyPropItem.update( None )
		
		self.__pyCBVehicles = ODComboBox( wnd.panel.cbVehicle )					#骑宠下拉列表
		self.__pyCBVehicles.autoSelect = False
		self.__pyCBVehicles.ownerDraw = True
		self.__pyCBVehicles.itemHeight = 25
		self.__pyCBVehicles.onViewItemInitialized.bind( self.onInitialized_ )
		self.__pyCBVehicles.onDrawItem.bind( self.onDrawItemVehicle_ )
		self.__pyCBVehicles.onItemSelectChanged.bind( self.__onVehicleSelected )
		self.__pyCBVehicles.onBeforeDropDown.bind( self.__resetCBConSumeVehicle )
		
		self.__pyCBProp = ODComboBox( wnd.panel.cbProp )					#消耗道具下拉列表
		self.__pyCBProp.autoSelect = False
		self.__pyCBProp.ownerDraw = True
		self.__pyCBProp.itemHeight = 25
		self.__pyCBProp.onViewItemInitialized.bind( self.onInitialized_ )
		self.__pyCBProp.onDrawItem.bind( self.onDrawItemProp_ )
		self.__pyCBProp.onItemSelectChanged.bind( self.__onPropSelected_ )
		self.__pyCBProp.onBeforeDropDown.bind( self.__resetCBConsumeProp )
	
	def onInitialized_( self, pyViewItem ):
		pyVehicleItem = VehicleComboItem()
		pyVehicleItem.focus = False
		pyVehicleItem.crossFocus = False
		pyViewItem.addPyChild( pyVehicleItem )
		pyViewItem.pyVehicleItem = pyVehicleItem
		
	def onDrawItemProp_( self, pyViewItem ):
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
		itemID = pyViewItem.listItem
		itemName = self.__getItemNameByID( itemID )
		pyVehicleItem.text = itemName
		
	def onDrawItemVehicle_( self, pyViewItem ):
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
		vehicleDBID = pyViewItem.listItem
		vehicleName = self.__getItemNameByID( vehicleDBID )
		vehicleLevel = self.__getVehicleLevel( vehicleDBID )
		pyVehicleItem.text = "Lv%s %s"%( vehicleLevel, vehicleName )
		
	def __onVehicleSelected( self, selIndex ):
		"""
		选择祭品骑宠
		"""
		if selIndex < 0:
			self.__pyVehicleItem.update( None )
			self.__pyCBVehicles.pyBox_.text = ""
			self.__updateSuccessRate()
			return
		self.__pyCBVehicles.pyBox_.foreColor= 255,255,255
		selVehicle = self.__pyCBVehicles.pyViewItems[selIndex]
		if selVehicle is None:
			self.__pyVehicleItem.update( None )
			return
		vehicleDBID = selVehicle.listItem
		vehicleData = BigWorld.player().vehicleDatas.get( vehicleDBID )
		srcItemID = vehicleData["srcItemID"]
		vehicleInfo = BigWorld.player().createDynamicItem( srcItemID )
		itemInfo = ItemInfo( vehicleInfo )
		self.__pyVehicleItem.update( itemInfo )		
		itemName = self.__getItemNameByID( vehicleDBID )
		vehicleLevel = vehicleData["level"]
		self.__pyCBVehicles.pyBox_.text = "Lv%d %s"%( vehicleLevel, itemName )
		self.__updateSuccessRate()
		
	def __onPropSelected_( self, selIndex ):
		"""
		选择消耗道具
		"""
		if selIndex < 0:
			self.__pyPropItem.update( None )
			self.__pyCBProp.pyBox_.text = ""
			self.__updateSuccessRate()
			return
			
		self.__pyCBProp.pyBox_.foreColor= 255,255,255
		pyViewItem = self.__pyCBProp.pyViewItems[selIndex]
		if pyViewItem is None:
			self.__pyPropItem.update( None )
			return
		itemID = pyViewItem.listItem
		itemInfo = BigWorld.player().createDynamicItem( itemID )
		itemInfo = ItemInfo( itemInfo )
		self.__pyPropItem.update( itemInfo )		
		itemName = self.__getItemNameByID( itemID )
		self.__pyCBProp.pyBox_.text = itemName
		self.__updateSuccessRate()		
		
	def __isHasItem( self, itemID ):
		items = BigWorld.player().findItemsByIDFromNK( itemID )
		return items and True or False
		
		
	def __onUpStage( self ):
		"""
		"""	
		if self.__pyCBVehicles.selIndex < 0:
			BigWorld.player().statusMessage( csstatus.VEHICLE_NOT_SELECT )
			return
		#发送请求
		mainID = BigWorld.player().activateVehicleID
		oblationID = self.__pyCBVehicles.selItem
		itemID = self.__pyCBProp.selItem
		BigWorld.player().upStepVehicle( mainID, oblationID, itemID )
		self.__resetCBConsumeProp()
		self.__resetCBConSumeVehicle()
	
	def __onBuy( self ):
		"""
		购买骑宠升阶道具
		"""
		player = BigWorld.player()
		activateVehicleID = player.activateVehicleID
		vehicleData = player.vehicleDatas.get( activateVehicleID )
		if vehicleData is None:return
		step = vehicleData["step"]
		itemID = csconst.VEHICLE_STEP_UPGRADE_ITEMID[step][0]
		ECenter.fireEvent("EVT_ON_QUERY_SHOP_ITEM",itemID, 4 )
		
	def __onLastKeyUpEvent( self, key, mods ) :
		if key != KEY_LEFTMOUSE : return
		BigWorld.cancelCallback( self.__turnModelCBID )
		LastKeyUpEvent.detach( self.__onLastKeyUpEvent )
	
	def __onTurnLeft( self ):
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__turnModel( False )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True

	def __onTurnRight( self ):
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__turnModel( True )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True

	def __turnModel( self, isRTurn ) :
		"""
		"""
		self.__pyVehicleRender.yaw += ( isRTurn and -0.1 or 0.1 )
		if BigWorld.isKeyDown( KEY_LEFTMOUSE ) :
			self.__turnModelCBID = BigWorld.callback( 0.1, Functor( self.__turnModel, isRTurn ) )
	
	def __setModel( self, vehicleDBID ):
		"""
		设置DBID的模型
		"""
		player = BigWorld.player()
		if player is None: return

		vehicleData = player.vehicleDatas.get( vehicleDBID )
		if vehicleData is None: return

		itemID = vehicleData["srcItemID"]
		self.__setModelByItemID( itemID )
		
	def __setModelByItemID( self, itemID ):
		item = BigWorld.player().createDynamicItem( itemID )
		if item is None: return
		itemModelID = item.model()
		rds.itemModel.createModelBG( itemModelID, Functor( self.__onModelCreated, itemModelID ) )
		

	def __onModelCreated( self, itemModelID, model ):
		"""
		模型后线程加载完回调
		"""
		if model:
			effectIDs = rds.itemModel.getMEffects( itemModelID )
			for effectID in effectIDs:
				dictData = rds.spellEffect.getEffectConfigDict( effectID )
				if len( dictData ) == 0: continue
				effect = rds.skillEffect.createEffect( dictData, model, model, Define.TYPE_PARTICLE_PLAYER,  Define.TYPE_PARTICLE_PLAYER )
				effect.start()
			self.__pyVehicleRender.update( itemModelID, model )	
			
	def __getItemNameByID( self, itemID ):
		"""
		获取消耗物品/骑宠名字
		"""
		itemName = ""
		player = BigWorld.player()
		vehicleData = player.vehicleDatas.get( itemID )
		if vehicleData is not None: 
			srcItemID = vehicleData["srcItemID"]
			itemName = self.__getVehicleNameByItemID( srcItemID )
		else:
			item = player.createDynamicItem( itemID )
			itemName = item.name()
		return itemName
		
	def __getVehicleLevel( self, vehicleDBID ):
		"""
		获取骑宠等级
		"""
		vehicleLevel = 0
		player = BigWorld.player()
		vehicleData = player.vehicleDatas.get( vehicleDBID )
		if vehicleData is not None: 
			vehicleLevel = vehicleData["level"]
		return vehicleLevel
		
	def __getVehicleNameByItemID( self, itemID ):
		vehicleName = ""
		vehicleItem = BigWorld.player().createDynamicItem( itemID )
		if vehicleItem:
			vehicleName = vehicleItem.name().split("(")[-1].split(")")[0]
		return vehicleName
		
	def __updateSuccessRate( self ):
		"""
		更新成功率
		"""
		if self.__pyCBVehicles.selIndex >= 0 and self.__pyCBProp.selIndex >= 0:
			successRate = csconst.VEHICLE_STEP_UPGRADE_SUCCESSRATE
			self.__pyStSuccessRate.text = labelGather.getText( "PetsWindow:VehicleUpgrade","successRate",successRate * 100 )
		else:
			self.__pyStSuccessRate.text = labelGather.getText( "PetsWindow:VehicleUpgrade","successRate","0" )
				
	def __updateState( self ):
		for pyViewItem in self.__pyCBProp.pyViewItems:
			itemID = pyViewItem.listItem
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
		
	def __updateVehicleName( self ):
		"""
		设置骑宠名字
		"""
		player = BigWorld.player()
		vehicleDBID = player.activateVehicleID
		if not vehicleDBID:return
		vehicleData = player.vehicleDatas.get( vehicleDBID )
		srcItemID = vehicleData["nextStepItemID"]
		vehicleItem = player.createDynamicItem( srcItemID )
		name = vehicleItem.name().split("(")[-1].split(")")[0]
		self.__pyStVehicleName.text = name
	
	def __resetCBConSumeVehicle( self ):
		"""
		设置祭品骑宠下拉列表
		"""
#		self.__pyCBVehicles.pyBox_.text = ""
		self.__pyCBVehicles.clearItems()
		player = BigWorld.player()
		activateVehicleID = player.activateVehicleID  #当前激活的骑宠
		activateVehicleStep = player.vehicleDatas[activateVehicleID]["step"] #主骑宠对应的阶次
		vehicleDatas = player.vehicleDatas
		for vehicleDBID, vehicleData in player.vehicleDatas.iteritems():
			if vehicleDBID != activateVehicleID and vehicleData["step"] == activateVehicleStep and vehicleData["type"] == csdefine.VEHICLE_TYPE_LAND:
				self.__pyCBVehicles.addItem( vehicleDBID )			
		self.__pyCBVehicles.selIndex = -1

	def __resetCBConsumeProp( self ):
		"""
		设置消耗道具列表
		"""
#		self.__pyCBProp.pyBox_.text = ""
		self.__pyCBProp.clearItems()
		activateVehicleID = BigWorld.player().activateVehicleID
		vehicleDatas = BigWorld.player().vehicleDatas
		step = vehicleDatas[activateVehicleID]["step"]
		itemList = csconst.VEHICLE_STEP_UPGRADE_ITEMID.get( step ,[] )
		for itemID in itemList:
			self.__pyCBProp.addItem( itemID )
		self.__updateState()
		self.__pyCBProp.selIndex = -1
		
	def __setSelectTips( self ):
		self.__pyCBProp.pyBox_.foreColor= 180,180,180
		self.__pyCBVehicles.pyBox_.foreColor= 180,180,180
		self.__pyCBVehicles.pyBox_.text = labelGather.getText( "PetsWindow:VehicleUpgrade","selectVehicleTips" )
		self.__pyCBProp.pyBox_.text = labelGather.getText( "PetsWindow:VehicleUpgrade","selectPropTips" )

	@staticmethod
	def instance():
		if StageUpgrade.__instance is None:
			StageUpgrade.__instance = StageUpgrade()
		return StageUpgrade.__instance
		

#---------------------------------------------------------
# public
#---------------------------------------------------------
	def show( self ):
		Window.show( self )
		self.__pyVehicleRender.enableDrawModel()
		activateVehicleID = BigWorld.player().activateVehicleID
#		self.__allModels.pop( activateVehicleID )
		vehicleData = BigWorld.player().vehicleDatas[ activateVehicleID]
		nextStepItemID = vehicleData["nextStepItemID"]
		if nextStepItemID:
			self.__setModelByItemID( nextStepItemID )
			self.__updateVehicleName()
			self.updateStepInfo()
		else:
			self.hide()	
			
		self.__resetCBConSumeVehicle()	
		self.__resetCBConsumeProp()
		self.__setSelectTips()
			
	def updateStepInfo( self ):
		"""
		更新激活骑宠阶次信息
		"""
		player = BigWorld.player()
		activateVehicleID = player.activateVehicleID
		vehicleData = player.vehicleDatas.get( activateVehicleID )
		if vehicleData is not None:
#			maxStep = getVehicleMaxStep( activateVehicleID )
			step = vehicleData["step"] + 1
			self.__pyStStage.text = labelGather.getText( "PetsWindow:VehicleUpgrade","stepInfo",step )
		else:
			self.__pyStStage.text = ""	
		
	def onLeaveWorld( self ):
		self.__pyVehicleRender.clearModel()
		self.hide()	
		
	def hide( self ):
		Window.hide( self )
		self.__pyVehicleRender.disableDrawModel()
		self.__turnModelCBID = 0
		self.__pyCBVehicles.clearItems()
		self.__pyCBProp.clearItems()
		self.__pyStStage.text = ""
		self.__pyStVehicleName.text = ""
		self.__pyVehicleRender.clearModel()			
		
# -----------------------------------------------------------------
class ConsumeItem( PyGUI ):
	"""
	祭品
	"""
	def __init__( self, item ):
		PyGUI.__init__( self, item )
		self.__pyItemBg = PyGUI( item.itemBg )
		self.__pyItem = VehicleConsumeItem( item.item )

	def update( self, itemInfo ):
		self.__pyItem.update( itemInfo )

class PropItem( PyGUI ):
	"""
	鳞片
	"""
	def __init__( self, item ):
		PyGUI.__init__( self, item )
		self.__pyItemBg = PyGUI( item.itemBg )
		self.__pyItem = VehiclePropItem( item.item )
		
	def update( self, itemInfo ):
		self.__pyItem.update( itemInfo )

class VehicleConsumeItem( BOItem ):
	def update( self, itemInfo ):
		BOItem.update( self, itemInfo )
		if itemInfo is None:
			self.description = labelGather.getText( "PetsWindow:VehicleUpgrade", "vehicleDsp" )

	def onDescriptionShow_( self ):
		if self.itemInfo is None:
			selfDsp = self.description
			toolbox.infoTip.showItemTips( self, selfDsp )

class VehiclePropItem( BOItem ):
	def update( self, itemInfo ):
		BOItem.update( self, itemInfo )
		if itemInfo is None:
			self.description = labelGather.getText( "PetsWindow:VehicleUpgrade", "propDsp" )

	def onDescriptionShow_( self ):
		if self.itemInfo is None:
			selfDsp = self.description
			toolbox.infoTip.showItemTips( self, selfDsp )
		else:
			BOItem.onDescriptionShow_( self )