# -*- coding: gb18030 -*-
#
# $Id: MailItem.py, fangpengjun Exp $

"""
implement mailitem
"""
import GUI
import csol
import csdefine
import csconst
import BigWorld
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.MLUIDefine import ItemQAColorMode
import event.EventCenter as ECenter

class MailItem( PyGUI ):

	def __init__( self, item, dragMark, index ):
		PyGUI.__init__( self, item )
		self.dragMark = dragMark
		self.__pyItem = Item( item.item, dragMark, index )
		self.itemInfo = None
		self.uid = -1
		self.index = index

	def update( self, itemInfo, mailID = -1 ):
		self.__pyItem.update( itemInfo, mailID )
		self.itemInfo = itemInfo
		if itemInfo is not None :
			self.uid = itemInfo.baseItem.uid
			quality = itemInfo.quality
			self.__setItemQuality( self.getGui(), quality )
		else:
			self.uid = -1
			self.__setItemQuality( self.getGui(), 1 )

	def __setItemQuality( self, itemBg, quality ):
		util.setGuiState( itemBg, ( 4, 2 ), ItemQAColorMode[quality] )

# -------------------------------------------------------------------------------
class Item( BOItem ) :
	def __init__( self, item, dragMark, index ) :
		BOItem.__init__( self, item )
		self.__initialize( item )
		self.focus = True
		self.crossFocus = True
		self.dragFocus = True
		self.dropFocus = True
		self.selectable = True
		self.dragMark = dragMark
		self.index = index
		self.mailID = -1

	def subclass( self, item ) :
		BOItem.subclass( self, item )
		self.__initialize( item )
		return True
	# -------------------------------------------------
	def __initialize( self, item ) :
		if item is None : return
		self.dropFocus = self.dragMark == DragMark.MAIL_SEND_ITEM
		self.__dropEvents = {}
		self.__dropEvents[DragMark.KITBAG_WND] = DropHandlers.fromKitbagWindow
		self.__dropEvents[DragMark.MAIL_SEND_ITEM] = DropHandlers.fromSendPanel

	def dispose( self ) :
		BOItem.dispose( self )

	def onMouseEnter_( self ):
#		BOItem.onMouseEnter_( self )
		self.onDescriptionShow_()
		toolbox.itemCover.highlightItem( self )
		if self.dragMark not in [DragMark.MAIL_SEND_ITEM, DragMark.MAIL_RECEIVE_ITEM] or \
		self.itemInfo is None:return

	def onMouseLeave_( self ):
		BOItem.onMouseLeave_( self )
		if self.dragMark not in [DragMark.MAIL_SEND_ITEM, DragMark.MAIL_RECEIVE_ITEM] or \
		self.itemInfo is None:return
		return True

	def onRClick_( self, mods ):
		BOItem.onRClick_( self, mods )
		player = BigWorld.player()
		if mods == 0:
			if self.dragMark == DragMark.MAIL_SEND_ITEM: #移除待发信物品
				ECenter.fireEvent( "EVT_ON_MAIL_DEL_SENDITEM",self.index )
			if self.dragMark == DragMark.MAIL_RECEIVE_ITEM: #领取收信物品
				if self.itemInfo == None:
					return
				player.mail_getItem( self.mailID, self.index )
		return True

	def onLClick_( self, mods ):
		if not self.itemInfo: return
		BOItem.onLClick_( self, mods )
		return True

	# -------------------------------------------------
	def onDragStart_( self, pyDragged ) :
		BOItem.onDragStart_( self, pyDragged )
		if BigWorld.isKeyDown( KEY_LCONTROL ) :
			rds.ruisMgr.dragObj.attach = KEY_LCONTROL
		return True

	def onDrop_( self, pyTarget, pyDropped ):
		BOItem.onDrop_( self, pyTarget, pyDropped )
		dragMark = rds.ruisMgr.dragObj.dragMark
		if not self.__dropEvents.has_key( dragMark ) : return
		if pyTarget.dragMark != DragMark.MAIL_SEND_ITEM:return
		self.__dropEvents[dragMark]( pyTarget, pyDropped )
		return True

	def onDragStop_( self, pyDragged ) :
		if pyDragged.itemInfo is None:return
		if not ruisMgr.isMouseHitScreen() : return False
		index = pyDragged.index
		ECenter.fireEvent( "EVT_ON_MAIL_DEL_SENDITEM", index ) #拖放移除物品
	# -----------------------------------------------
	# public
	# -----------------------------------------------
	def update( self, itemInfo, mailID ) :
		"""
		update item
		"""
		BOItem.update( self, itemInfo )
		if itemInfo is not None :
			self.mailID = mailID
		else:
			self.mailID = -1

class DropHandlers :
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@staticmethod
	def fromKitbagWindow( pyTarget, pyDropped ) :
		"""
		the item drag from items window
		"""
		kitbagID = pyDropped.kitbagID
		gbIndex = pyDropped.gbIndex
		index = pyTarget.index
		ECenter.fireEvent( "EVT_ON_MAIL_ADD_SENDITEM", kitbagID, gbIndex, index )

	@staticmethod
	def fromSendPanel( pyTarget, pyDropped ):
		if pyTarget.dragMark != DragMark.MAIL_SEND_ITEM and pyDropped.dragMark != DragMark.MAIL_SEND_ITEM:
			return
		srcIndex = pyDropped.index
		dstIndex = pyTarget.index
		ECenter.fireEvent( "EVT_ON_MAIL_SWAP_ITEMS", srcIndex, dstIndex )
