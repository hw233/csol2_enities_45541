# -*- coding: gb18030 -*-
#
# $Id: TradeItem.py,v 1.4 2008-06-27 03:19:27 huangyongwei Exp $

"""
implement trading item class
"""
import csdefine
import GUIFacade
from guis import *
from guis.common.PyGUI import PyGUI
from guis.general.StoreWindow.CompareDspItem import CompareDspItem
from guis.controls.StaticText import StaticText
from guis.controls.Control import Control
from guis.MLUIDefine import ItemQAColorMode

class TradeItem( Control ) :

	def __init__( self, item = None, index = -1, pyBinder = None ) :
		Control.__init__( self, item, pyBinder )
		self.__initialize( item, index )
		self.__itemInfo = None
		self.__panelState = ( 1, 1 )
		self.index = index

	def subclass( self, item, pyBinder ) :
		Control.subclass( self, item, pyBinder )
		self.__initialize( item )
		return self

	def __initialize( self, item, index ) :	# wsf
		if item is None : return
		self.__pyLabelName = StaticText( item.stName )
		self.__pyLabelName.text = ""
		self.__pyObjectItem = ObjectItem( item.item, index, self )
		self.__pyItemBg = PyGUI( item.itemBg )
		self.itemPanel = item.itemPanel

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def updateItem( self, itemInfo ) :	# wsf
		"""
		update item via item information
		"""
		self.__itemInfo = itemInfo
		self.__pyObjectItem.update( itemInfo )
		self.__pyObjectItem.crossFocus = itemInfo is not None
		if itemInfo is None :
			self.__pyLabelName.text = ""
			self.__setItemQuality( self.__pyItemBg.getGui(), 0 )
			self.panelState = ( 1, 1 )
		else :
			quality = itemInfo.quality
			self.__setItemQuality( self.__pyItemBg.getGui(), quality )
			self.panelState = ( 2, 1 )
			self.__pyLabelName.text = itemInfo.name()

	def __setItemQuality( self, itemBg, quality ):
		util.setGuiState( itemBg, ( 4, 2 ), ItemQAColorMode[quality] )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getItemInfo( self ) :
		return self.__itemInfo

	def _getFocus( self ):
		return self.__pyObjectItem.focus

	def _setFocus( self, focus ):
		self.__pyObjectItem.focus = focus

	def _getDragFocus( self ):
		return self.__pyObjectItem.dragFocus

	def _setDragFocus( self, dragFocus ):
		self.__pyObjectItem.dragFocus = dragFocus

	def _getDropFocus( self ):
		return self.__pyObjectItem.dropFocus

	def _setDropFocus( self, dropFocus ):
		self.__pyObjectItem.dropFocus = dropFocus

	def _getIndex( self ):
		return self.__index

	def _setIndex( self, index ):
		self.__index = index

	def _getPanelState( self ):
		return self.__panelState

	def _setPanelState( self, state ):
		self.__panelState = state
		elements = self.itemPanel.elements
		for ename, element in elements.items():
			element.mapping = util.getStateMapping( element.size, UIState.MODE_R3C1, state )
			if ename in ["frm_rt", "frm_r", "frm_rb"]:
				element.mapping = util.hflipMapping( element.mapping )

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	itemInfo = property( _getItemInfo )
	itemFocus = property( _getFocus, _setFocus )
	itemDragFocus = property( _getDragFocus, _setDragFocus )
	itemDropFocus = property( _getDropFocus, _setDropFocus )
	index = property( _getIndex, _setIndex )
	panelState = property( _getPanelState, _setPanelState )

# --------------------------------------------------------------------
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
class ObjectItem( BOItem ):
	def __init__( self, item = None, index = -1, pyBinder = None ):
		BOItem.__init__( self, item, pyBinder )
		self.__initialize( item )
		self.index = index

	def subclass( self, item, pyBinder ) :
		BOItem.subclass( self, item, pyBinder )
		self.__initialize( item )
		return self

	def __initialize( self, item ):
		if item is None : return
		self.dragMark = DragMark.ROLES_TRADING_WND
		self.__dropEvents = {}
		self.__dropEvents[ DragMark.KITBAG_WND ] = DropHandlers.fromItemsWindow

	def update( self, itemInfo ):
		BOItem.update( self, itemInfo )
		self.index = self.pyBinder.index

	def onDragStart_( self, pyDragged ) :	# wsf add
		BOItem.onDragStart_( self, pyDragged )
		if BigWorld.isKeyDown( KEY_LCONTROL ) :
			rds.ruisMgr.dragObj.attach = KEY_LCONTROL
		return True

	def onDrop_( self, pyTarget, pyDropped ) :	# wsf add
		BOItem.onDrop_( self, pyTarget, pyDropped )
		dragMark = pyDropped.dragMark
		#dragMark = rds.ruisMgr.dragObj.dragMark
		if not self.__dropEvents.has_key( dragMark ) : return
		self.__dropEvents[ dragMark ]( pyTarget, pyDropped )
		return True

	def onDragStop_( self, pyDragged ) : #拖拉清除交易栏物品
		BOItem.onDragStop_( self, pyDragged )
		GUIFacade.removeSwapItem( self.index )
		return True

	def onRClick_( self, mods ): #右键清除交易栏物品
		BOItem.onRClick_( self, mods )
		if self.itemInfo is not None :
			GUIFacade.removeSwapItem( self.index )
		return True

	def onMouseEnter_( self ):
		BOItem.onMouseEnter_( self )
		if self.itemInfo is None:return
		self.pyBinder.panelState = ( 2, 1 )

	def onMouseLeave_( self ):
		BOItem.onMouseLeave_( self )
		if self.itemInfo is None:return
		self.pyBinder.panelState = ( 1, 1 )
		return True

class DropHandlers :	# wsf add
	@staticmethod
	def fromItemsWindow( pyTarget, pyDropped ) :
		kitbagID = pyDropped.kitbagID
		dstIndex = pyTarget.index
		srcIndex = pyDropped.gbIndex
		#amount = pyDropped.amount
		GUIFacade.changeSwapItem( dstIndex, kitbagID, srcIndex )
