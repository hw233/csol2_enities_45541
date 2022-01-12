# -*- coding: gb18030 -*-
#
# $Id: KitbagItem.py,v 1.15 2008-09-01 06:36:14 pengju Exp $

"""
implement PackItem
"""
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.controls.Control import Control
import BigWorld
import csdefine
import GUIFacade
import event.EventCenter as ECenter


class KitbagItem( PyGUI ):
	def __init__( self, kitbagID, item ):
		PyGUI.__init__( self, item )
		self.dragFocus = False
		self.dropFocus = False
		self.focus = True
		self.__pyItem = Item( kitbagID, item.item )
		self.__pyCover = Control( item.cover )
		self.__pyCover.visible = False
	
	def update( self, itemInfo ):
		self.__pyItem.update( itemInfo )
		if itemInfo:
			util.setGuiState( self.getGui(), ( 2, 1 ), ( 1, 1 ) )
		else:
			util.setGuiState( self.getGui(), ( 2, 1 ), ( 2, 1 ) )
		self.__pyCover.visible = False

	def _getCover( self ):
		return self.__pyCover

	def _getItemInfo( self ):
		return self.__pyItem.itemInfo

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	cover = property( _getCover )
	itemInfo = property( _getItemInfo )

# ---------------------------------------------------------------------------
class Item( BOItem ):
	def __init__( self, kitBagID = 0, item = None ):
		BOItem.__init__( self, item )
		self.kitBagID  = kitBagID
		self.selectable = True
		self.dropFocus = True
		self.dragMark = DragMark.KITBAG_BAG
		self.__dropEvents = {}
		self.__dropEvents[DragMark.KITBAG_WND] = DropHandlers.fromKitbagWindow
		self.__dropEvents[DragMark.KITBAG_BAG] = DropHandlers.fromKitbagPack

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRClick_( self, mods ) :
		BOItem.onRClick_( self, mods )
		return True

	def onLClick_( self, mods ):
		BOItem.onLClick_( self, mods )
		if self.itemInfo is None :return
		if BigWorld.player().state == csdefine.ENTITY_STATE_VEND and \
			self.kitBagID == csdefine.KB_CASKET_ID:
			# "摆摊时不能使用神机匣功能。"
			showAutoHideMessage( 3.0, 0x0401, "", pyOwner = rds.ruisMgr.kitBag )
			return
		ECenter.fireEvent( "EVT_ON_KITBAG_SET_CURRENT",  self.kitBagID )
		GUIFacade.upDateKitBagItems( self.kitBagID )
		return True

	# ---------------------------------------
	def onDrop_( self, pyTarget, pyDropped ) :
		BOItem.onDrop_( self, pyTarget, pyDropped )
		dragMark = rds.ruisMgr.dragObj.dragMark
		if not self.__dropEvents.has_key( dragMark ) : return
		self.__dropEvents[dragMark]( pyTarget, pyDropped )
		return True

	def onStateChanged_( self, state ):
		BOItem.onStateChanged_( self, state )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		"""
		update item
		"""
		BOItem.update( self, itemInfo )

	def clear( self ) :
		BOItem.clear( self )

# --------------------------------------------------------------------
# --------------------------------------------------------------------
class DropHandlers :
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------

	@staticmethod
	def fromKitbagWindow( pyTarget, pyDropped ) : #从物品栏拖放物品到背包位
		"""
		the item drag from items window
		"""
		player = BigWorld.player()
		srcKitbag = pyDropped.kitbagID
		srcIndex = pyDropped.gbIndex
		kitBagID = pyTarget.kitBagID
		GUIFacade.moveKbItemToKitTote( srcKitbag, srcIndex, kitBagID )

	@staticmethod
	def fromKitbagPack( pyTarget, pyDropped ): # 包裹之间的交换
		player = BigWorld.player()
		srcIndex = pyDropped.kitBagID
		dstIndex = pyTarget.kitBagID
		GUIFacade.swapKitbag( srcIndex, dstIndex )