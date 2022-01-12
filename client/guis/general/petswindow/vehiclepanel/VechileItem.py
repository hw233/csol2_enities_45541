# -*- coding: gb18030 -*-
#
# $Id: WareItem.py,v 1.37 2008-09-05 03:28:05 pengju Exp $

"""
implement ware item
"""
from guis import *
from LabelGather import labelGather
from guis.controls.Control import Control
from guis.common.PyGUI import PyGUI
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from ItemsFactory import ObjectItem as ItemInfo
from NPCModelLoader import NPCModelLoader
import GUIFacade
import csdefine

class VechileItem( Control ):
	def __init__( self ):
		vcItem = GUI.load( "guis/general/petswindow/vehicleitem.gui")
		uiFixer.firstLoadFix( vcItem )
		Control.__init__( self, vcItem )
		self.crossFocus = False
		self.dragFocus = False
		self.focus = False
		self.dragMark = DragMark.VEHICLES_PANEL
		self.__pyCover = None
		self.__pyVehicleBg = PyGUI( vcItem.petBg )
		self.infoBg = vcItem.infoBg
		self.__pyItem = Item( vcItem.item, self.dragMark, self )
		self.__pyItem.onLDBClick.bind( self.__onLDBClick )
		self.__pyRtInfo = CSRichText( vcItem.rtInfo )
		self.__pyRtInfo.top = 15.0
		self.__pyRtInfo.maxWidth = 100.0
		self.__pyRtInfo.align = "C"
		self.__pyRtInfo.lineFlat = "M"
		self.__pyRtInfo.fontSize = 12.0
		self.itemInfo = None
		self.__panelState = ( 1, 1 )
		if hasattr( vcItem, "cover" ) :
			self.__pyCover = PyGUI( vcItem.cover )
			self.__pyCover.visible = False
		self.vehicleID = -1

	# -------------------------------------------------------------
	def __onLDBClick( self ):
		"""
		左键双击触发
		"""
		vehicleDBID = self.__pyItem.vehicleID
		player = BigWorld.player()
		if player.vehicleDBID == vehicleDBID:
			player.cell.retractVehicle()
		else:
			player.conjureVehicle( vehicleDBID )

	# -------------------------------------------------------------
	# public
	# -------------------------------------------------------------
	def update( self, vehicleData, activated = False ):
		name = ""
		itemInfo = None
		vehicleID = -1
		if vehicleData:
			vehicleItemID = vehicleData["srcItemID"]
			vehicleItem = BigWorld.player().createDynamicItem( vehicleItemID )
			itemInfo = ItemInfo( vehicleItem )
			name = self.revertVehicleName( vehicleItem )
			level = vehicleItem.getReqLevel()
			modelNumber = str( vehicleItem.model() ).lower()
			if activated:
				nameText = name + "\n" + labelGather.getText( "PetsWindow:VehiclesPanel", "activateText" )
				nameText = PL_Font.getSource( "%s"%nameText, fc = ( 0, 255, 0, 255 ) )
				self.__pyRtInfo.top = 10.0
			else:
				nameText = PL_Font.getSource( "%s"%name, fc = ( 0, 255, 255, 255 ) )
				self.__pyRtInfo.top = 15.0
			levelText = PL_Font.getSource( labelGather.getText( "PetsWindow:VehiclesPanel", "vehicleLevel" )%( PL_NewLine.getSource(), level ), fc = ( 255, 0, 0, 255 ) )
			self.__pyRtInfo.text = nameText
			self.__pyItem.crossFocus = True
			util.setGuiState( self.__pyVehicleBg.getGui(), ( 1,2 ),( 1, 1 ) )
			vehicleID = vehicleData["id"]
		else:
			self.__pyRtInfo.text = ""
			self.__pyItem.crossFocus = False
			util.setGuiState( self.__pyVehicleBg.getGui(), ( 1,2 ),( 1, 2 ) )
		self.itemInfo = itemInfo
		self.vehicleID = vehicleID
		self.__pyItem.update( itemInfo, vehicleID )

	def __select( self ):
		self.panelState = ( 3, 1 )
		if self.__pyCover:
			self.__pyCover.visible = True

	def __deselect( self ):
		self.panelState = ( 1, 1 )
		if self.__pyCover:
			self.__pyCover.visible = False

	def revertVehicleName( self, baseItem ):
		"""
		还原骑宠类物品名字
		骑宠蛋(XXX) -> XXX
		"""
		name = baseItem.name()
		return name.split("(")[-1].split(")")[0]

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def getObjectItem( self ):
		return self.__pyItem

	def _getVehicleID( self ):
		return self.__dbid

	def _setVehicleID( self, dbid ):
		self.__dbid = dbid

	def _getPanelState( self ):
		return self.__panelState

	def _setPanelState( self, state ):
		self.__panelState = state
		elements = self.infoBg.elements
		for ename, element in elements.items():
			element.mapping = util.getStateMapping( element.size, UIState.MODE_R3C1, state )
			if ename in ["frm_rt", "frm_r", "frm_rb"]:
				element.mapping = util.hflipMapping( element.mapping )

	def _getSelected( self ):
		return self.__selected

	def _setSelected( self, selected ):
		if selected:
			self.__select()
		else:
			self.__deselect()
		self.__selected = selected
	# -------------------------------------------------
	vehicleID = property( _getVehicleID, _setVehicleID )
	panelState = property( _getPanelState, _setPanelState )
	selected = property( _getSelected, _setSelected )

# ----------------------------------------------------------------------
import event.EventCenter as ECenter
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis import *
import BigWorld
from config.client.msgboxtexts import Datas as mbmsgs

class Item( BOItem ):
	def __init__( self, item, dragMark, pyBinder = None ):
		BOItem.__init__( self, item, pyBinder )
		self.focus = True
		self.crossFocus = True
		self.dragFocus = True
		self.selectable = True
		self.description = ""
		self.dragMark = dragMark
		self.index = 0
		self.vehicleID = -1
		self.__initialize( item )

	def subclass( self, item ) :
		BOItem.subclass( self, item )
		self.__initialize( item )
		return True

	def __initialize( self, item ) :
		if item is None : return

	def onMouseEnter_( self ):
		BOItem.onMouseEnter_( self )
		if self.dragMark != DragMark.VEHICLES_PANEL or \
		self.itemInfo is None:return
		if self.pyBinder.selected:return
		self.pyBinder.panelState = ( 2, 1 )
		return True

	def onMouseLeave_( self ):
		BOItem.onMouseLeave_( self )
		if self.dragMark != DragMark.VEHICLES_PANEL or \
		self.itemInfo is None:return
		if self.pyBinder.selected:return
		self.pyBinder.panelState = ( 1, 1 )
		return True

	def onRClick_( self,mods ):
		BOItem.onRClick_( self, mods )
		return True

	def onLClick_( self, mods ):
		if self.itemInfo is None:return
		BOItem.onLClick_( self, mods )
		ECenter.fireEvent( "EVT_ON_VEHICLE_SLECTED", self.pyBinder.vehicleID )
		return True

	# -------------------------------------------------
	def onDragStart_( self, pyDragged ) :
		BOItem.onDragStart_( self, pyDragged )
		if BigWorld.isKeyDown( KEY_LCONTROL ) :
			rds.ruisMgr.dragObj.attach = KEY_LCONTROL
		if self.itemInfo is None:return
		rds.ruisMgr.hideBar.enterShow()
		return True

	def onDragStop_( self, pyDragged ):
		if self.itemInfo is None: return
		BOItem.onDragStop_( self, pyDragged )
		rds.ruisMgr.hideBar.leaveShow()
		rds.ruisMgr.hideBar.hidelightLack()
		rds.ruisMgr.quickBar.hidelightLack()
		name = self.revertVehicleName( pyDragged.itemInfo )
		if not ruisMgr.isMouseHitScreen() : return False
		vehicleID = pyDragged.vehicleID
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().fixFreeVehicle( vehicleID )
		# "确定要将骑宠[%s]放生?"
		showMessage( mbmsgs[0x0d01] % name, "", MB_OK_CANCEL, query, pyOwner = rds.ruisMgr.petWindow )
		return True
	# -----------------------------------------------
	# public
	# -----------------------------------------------
	def update( self, itemInfo, vehicleID ):
		"""
		update item
		"""
		BOItem.update( self, itemInfo )
		self.vehicleID = vehicleID
		self.description = labelGather.getText( "PetsWindow:VehiclesPanel", "vehicleItemDsp" )

	def revertVehicleName( self, itemInfo ):
		"""
		还原骑宠类物品名字
		骑宠蛋(XXX) -> XXX
		"""
		name = itemInfo.name()
		return name.split("(")[-1].split(")")[0]
