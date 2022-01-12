# -*- coding: gb18030 -*-
#
# $Id: StuffsInfo.py,v 1.6 2008-08-25 09:40:56 fangpengjun Exp $

"""
implement StuffsInfo class
"""

from guis import *
from guis.common.PyGUI import PyGUI
#from guis.controls.ItemsPanel import ItemsPanel
from guis.controls.Control import Control
from guis.controls.StaticText import StaticText

class StuffsInfo( PyGUI ):

	def __init__( self, itemsPanel = None ):
		PyGUI.__init__( self, itemsPanel )
		self.viewCols = 2
		self.visible = True
		self.__initItems( itemsPanel )

	def __initItems( self, itemsPanel ):
		self.__pyItems = {}
		for name, item in itemsPanel.children:
			if "item_" not in name:continue
			index = int( name.split( "_" )[1] )
			pyItemInfo = ItemInfo( item )
			pyItemInfo.visible = False
			self.__pyItems[index] = pyItemInfo

	# --------------------------------------
	# public
	# --------------------------------------
	def updateItem( self, index, itemInfo, reqNum ):
		if self.__pyItems.has_key( index ):
			pyItem = self.__pyItems[index]
			pyItem.visible = True
			pyItem.update( itemInfo, reqNum )

	def updateNum( self, stuffID, existNum ):
		for pyItem in self.__pyItems.itervalues():
			if pyItem.itemInfo is None:
				continue
			if pyItem.itemInfo.id == stuffID or stuffID in rds.equipMake.getClassList( pyItem.itemInfo.id ):
				pyItem.updateNum( existNum )
				break

	def changeNum( self, stuffID, num ):
		for pyItem in self.__pyItems.itervalues():
			if pyItem.itemInfo is None:
				continue
			if pyItem.itemInfo.id == stuffID or stuffID in rds.equipMake.getClassList( pyItem.itemInfo.id ):
				pyItem.changeNum( num )
				break

	def clear( self ):
		for pyItem in self.__pyItems.itervalues():
			pyItem.update( None, -1 )
			pyItem.visible = False

	def resetNum( self ):
		for pyItem in self.__pyItems.itervalues():
			pyItem.updateNum( 0 )

# -------------------------------------------------
# ItemInfo
# -------------------------------------------------
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
class ItemInfo( Control ):
	def __init__( self, item ):
		Control.__init__( self, item )
		self.crossFocus = False
		self.dragFocus = False

		self.__pyItem = BOItem( item.icon )
		self.__pyItem.crossFocus = False
		self.__pyItem.dragFocus = False
		self.__pySTName = StaticText( item.lbName )
		self.__pySTName.text = ""

		self.__pySTNum = StaticText( item.lbNum )
		self.__pySTNum.text = ""
		self.__itemInfo = None
		self.__reqNum = -1
		self.__exitNum = -1

	# -------------------------------------------------------------
	# public
	# -------------------------------------------------------------
	def update( self, itemInfo, reqNum ):
		self.__pyItem.update( itemInfo )
		self.__itemInfo = itemInfo
#		self.visible = itemInfo is not None
		if itemInfo is not None:
			self.__pySTName.text = itemInfo.name()[4:]
			self.__reqNum = reqNum
		else:
			self.__pySTName.text = ""
			self.__reqNum = -1
			self.__pySTNum.text = ""

	def updateNum( self, existNum ):
		self.__exitNum = existNum
		self.__pySTNum.text = "%d/%d"%( self.__exitNum, self.__reqNum )

	def changeNum( self, num ):
		self.__exitNum += num
		if self.__exitNum <= 0:
			self.__exitNum = 0
		self.__pySTNum.text = "%d/%d"%( self.__exitNum, self.__reqNum )

	def _getItemInfo( self ):
		return self.__itemInfo

	def _setItemInfo( self, itemInfo ):
		self.__itemInfo = itemInfo

	itemInfo = property( _getItemInfo, _setItemInfo )