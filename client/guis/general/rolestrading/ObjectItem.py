# -*- coding: gb18030 -*-
#
# $Id: ObjectItem.py,v 1.8 2008-06-21 03:02:45 huangyongwei Exp $

"""
implement trading item class
"""
import csdefine

from guis import *
from guis.general.StoreWindow.CompareDspItem import CompareDspItem
import GUIFacade


class ObjectItem( CompareDspItem ) :
	def __init__( self, item = None, pyBinder = None ) :
		CompareDspItem.__init__( self, item, pyBinder )
		self.__initialize( item )
		self.__itemInfo = None

	def subclass( self, item, pyBinder ) :
		CompareDspItem.subclass( self, item, pyBinder )
		self.__initialize( item )
		return self

	def __initialize( self, item ) :	# wsf
		if item is None : return
		self.dragMark = DragMark.ROLES_TRADING_WND
		self.__dropEvents = {}
		self.__dropEvents[ DragMark.KITBAG_WND ] = DropHandlers.fromItemsWindow
		# self.__dropEvents[DragMark.EQUIP_WNDW] = DropHandlers.fromEquipWindow
		# self.__dropEvents[ DragMark.BANK_WND ] = DropHandlers.fromSwapWindow	# wsf



	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def updateItem( self, itemInfo ) :	# wsf
		"""
		update item via item information
		"""
		self.__itemInfo = itemInfo
		CompareDspItem.update( self, itemInfo )
		if itemInfo is None :
			self.clear()
		else :
			self.icon = itemInfo.icon
			#amount = itemInfo.amount
			#if amount < 2 : self.amountText = ""
			#else : self.amountText = str( amount )

	# -------------------------------------------------
	def onDragStart_( self, pyDragged ) :	# wsf add
		CompareDspItem.onDragStart_( self, pyDragged )
		if BigWorld.isKeyDown( KEY_LCONTROL ) :
			rds.ruisMgr.dragObj.attach = KEY_LCONTROL
		return True

	def onDrop_( self, pyTarget, pyDropped ) :	# wsf add
		CompareDspItem.onDrop_( self, pyTarget, pyDropped )
		dragMark = pyDropped.dragMark
		#dragMark = rds.ruisMgr.dragObj.dragMark
		if not self.__dropEvents.has_key( dragMark ) : return
		self.__dropEvents[ dragMark ]( pyTarget, pyDropped )
		return True

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getItemInfo( self ) :
		return self.__itemInfo

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	itemInfo = property( _getItemInfo )

class DropHandlers :	# wsf add
	@staticmethod
	def fromItemsWindow( pyTarget, pyDropped ) :
		kitbagID = pyDropped.kitbagID
		dstIndex = pyTarget.gbIndex
		srcIndex = pyDropped.gbIndex
		#amount = pyDropped.amount
		GUIFacade.changeSwapItem( dstIndex, kitbagID, srcIndex )

	#@staticmethod
	#def fromSwapWindow( pyTarget, pyDropped ) :
	#	srcIndex = pyDropped.gbIndex
	#	dstIndex = pyTarget.gbIndex
	#	if srcIndex == dstIndex : return
	#	GUIFacade.swapBankItem( srcIndex, dstIndex )
