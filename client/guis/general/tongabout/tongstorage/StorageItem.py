# -*- coding: gb18030 -*-
#
# $Id: StoreItem.py,v 1.14 2008-08-08 03:17:08 fangpengjun Exp $

"""
implement StoreItem
"""
from guis import *
from guis.tooluis.inputbox.InputBox import AmountInputBox
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.common.PyGUI import PyGUI
from config.client.msgboxtexts import Datas as mbmsgs
from guis.MLUIDefine import ItemQAColorMode
import BigWorld
import GUIFacade

class StorageItem( PyGUI ):

	def __init__( self, item, index ):
		PyGUI.__init__( self, item )
		self.dragFocus = False
		self.dropFocus = True
		self.focus = True
		self.__pyItem = Item( index, item.item )
		self.__pyItem.index = index
		self.__itemInfo = None

	def update( self, itemInfo ):
		self.__pyItem.update( itemInfo )
		self.__itemInfo = itemInfo
		quality = itemInfo is None and 1 or itemInfo.quality
		util.setGuiState( self.getGui(), ( 4, 2 ), ItemQAColorMode[quality] )

	def _getGbIndex( self ) :
		return self.__pyItem.gbIndex

	def _setGbIndex( self, gbIndex ) :
		self.__pyItem.gbIndex = gbIndex

	def _getBagIndex( self ):
		return self.__pyItem.bagIndex

	def _setBagIndex( self, bagIndex ):
		self.__pyItem.bagIndex = bagIndex

	def _getItemInfo( self ):
		return self.__pyItem.itemInfo

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	gbIndex = property( _getGbIndex, _setGbIndex )			# get or set global index in bank
	bagIndex = property( _getBagIndex, _setBagIndex ) 		# bank index
	itemInfo = property( _getItemInfo )


class Item( BOItem ) :

	__cc__icon = "guis/general/tongabout/tongbank/storeitem.tga", util.getIconMapping( ( 48, 48 ) )
	def __init__( self, index, item = None, pyBinder = None ) :
		BOItem.__init__( self, item, pyBinder )
		self.focus = True
		self.crossFocus = True
		self.dragFocus = True
		self.dropFocus = True
		self.dragMark = DragMark.TONG_STORAGE_ITEM
		self.index = index
		self.__gbIndex = -1
		self.__bagIndex = 0			# 默认第一个包裹
		self.__itemInfo = None
		self.__initialize( item )

	def subclass( self, item, pyBinder ) :
		BOItem.subclass( self, item, pyBinder )
		return True

	def __initialize( self, item ) :
		if item is None : return
		self.__dropEvents = {}
		self.__dropEvents[DragMark.KITBAG_WND] = DropHandlers.fromItemsWindow #从背包
		self.__dropEvents[DragMark.TONG_STORAGE_ITEM] = DropHandlers.fromTongStorageWindow #从帮会仓库

	def dispose( self ) :
		BOItem.dispose( self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __splitItem( self ) :
		"""
		if an item is more the one, split it into two
		"""
		if self.itemInfo is None : return
		if self.itemInfo.amount <= 1 : return
		def split( result, amount ) :
			if result == DialogResult.OK :
				BigWorld.player().tong_fetchSplitItem2Kitbags( self.gbIndex, amount )
		rang = ( 1, self.itemInfo.amount - 1 )
		AmountInputBox().show( split, self, rang )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------s
	def update( self, itemInfo ):
		"""
		update item
		"""
		BOItem.update( self, itemInfo )
		if itemInfo is None:
			self.icon = self.__cc__icon
			util.setGuiState( self.getGui(), ( 2, 1 ), ( 1, 1 ) )
		else:
			self.description = itemInfo.description
			self.bagIndex = itemInfo.kitbag
			self.gbIndex = itemInfo.baseItem.getOrder()

	# -------------------------------------------------
	def onLClick_( self, mods ) :
		if mods == MODIFIER_CTRL :
			self.__splitItem()
		return True

	def onRClick_( self, mods ) :
		if self.itemInfo is None:
			return
		BigWorld.player().tong_fetchItem2Kitbags( self.gbIndex ) #普通背包
	# -------------------------------------------------
	def onDragStart_( self, pyDragged ) :
		if BigWorld.isKeyDown( KEY_LCONTROL ) :
			rds.ruisMgr.dragObj.attach = KEY_LCONTROL
		BOItem.onDragStart_( self, pyDragged )
		return True

	def onDragStop_( self, pyDragged ) :
		BOItem.onDragStop_( self, pyDragged )
		if pyDragged is None: return
		if not ruisMgr.isMouseHitScreen() : return False
		if pyDragged.itemInfo is None: return
		name = pyDragged.itemInfo.name()
		def query( rs_id):
			if rs_id == RS_OK:
				BigWorld.player().bank_destroyItem( self.bagIndex, self.gbIndex )
		# "确定丢弃%s？"
		showMessage( mbmsgs[0x0941] % name,"", MB_OK_CANCEL, query )
		return True

	def onDrop_( self, pyTarget, pyDropped ) :
		BOItem.onDrop_( self, pyTarget, pyDropped )
		dragMark = rds.ruisMgr.dragObj.dragMark
		if not self.__dropEvents.has_key( dragMark ) : return
		self.__dropEvents[dragMark]( pyTarget, pyDropped )
		return True

	def onDescriptionShow_( self ):
		BOItem.onDescriptionShow_( self )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getGbIndex( self ) :
		return self.__gbIndex

	def _setGbIndex( self, index ) :
		self.__gbIndex = index

	def _getBagIndex( self ):
		return self.__bagIndex

	def _setBagIndex( self, index ):
		self.__bagIndex = index

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	gbIndex = property( _getGbIndex, _setGbIndex )			# get or set global index in bank
	bagIndex = property( _getBagIndex, _setBagIndex ) 		# bank index

#---------------------------------------------------------------------
# drop handlers
#---------------------------------------------------------------------
import GUIFacade
class DropHandlers :
	@staticmethod
	def fromItemsWindow( pyTarget, pyDropped ) :
		"""
		往仓库指定格子存放物品
		"""
		player = BigWorld.player()
		kitBag = pyDropped.kitbagID
		srcIndex = pyDropped.gbIndex
		gbIndex = kitBag*255 + srcIndex
		dstBank = pyTarget.bagIndex
		dstIndex = pyTarget.gbIndex
		if pyTarget.index == -1:
			return
		player.tong_storeItem2Order( gbIndex, dstIndex, 0 )

	@staticmethod
	def fromTongStorageWindow( pyTarget, pyDropped ):
		"""
		仓库内物品之间的交换
		"""
		player = BigWorld.player()
		srcIndex = pyDropped.gbIndex
		dstIndex = pyTarget.gbIndex
		if srcIndex == dstIndex:
			return
		if pyTarget.index == -1:
			return
		player.tong_moveStorageItem( srcIndex, dstIndex )
