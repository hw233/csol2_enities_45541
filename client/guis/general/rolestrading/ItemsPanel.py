# -*- coding: gb18030 -*-
#
# $Id: ItemsPanel.py,v 1.4 2008-05-26 10:22:45 fangpengjun Exp $

"""
implement items panel class
"""

from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from TradeItem import TradeItem
import GUIFacade
import event.EventCenter as ECenter

class ItemsPanel( Control ) :

	def __init__( self, panel = None, pyBinder = None ) :
		Control.__init__( self, panel, pyBinder )
		self.__initialize( panel )

	def subclass( self, panel, pyBinder ) :
		Control.subclass( self, panel, pyBinder )
		self.__initialize( panel )
		return True

	def __initialize( self, panel ) :
		if panel is None : return
		self._pyItems = {}
		for name, item in panel.children:
			if "item_" not in name: continue
			index = int( name.split( "_" )[1] )
			pyItem = self.createPyItem_( item, index )
			pyItem.index = index
			self._pyItems[index] = pyItem
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
#	def __setItems( self ) :
#		"""
#		initialize all object items
#		"""
#		framePath = "guis/general/rolestrading/tradeitem.gui"
#		count = GUIFacade.getSwapItemBagSpace()
#		cols = ItemsPanel.__cc_view_cols
#		itemWidth = self.width
#		itemHeight = self.height / ItemsPanel.__cc_view_rows
#		for index in xrange( count ) :
#			frame = GUI.load( framePath )
#			uiFixer.firstLoadFix( frame )
#			pyFrame = PyGUI( frame )
#			self.addPyChild( pyFrame )
##			hspace = ( itemWidth - pyFrame.width ) / 2
#			vspace = ( itemHeight - pyFrame.height ) / 2
##			pyFrame.left = hspace + ( index % cols ) * itemWidth
##			pyFrame.top = vspace + ( index / cols ) * itemHeight
#			pyItem = ItemsPanel.createPyItem_( self, frame.icon, index )
#			self._pyItems.append( pyItem )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def createPyItem_( self, item, index ) :
		"""
		create a python object item
		"""
		pyItem = TradeItem( item, index, self )
		return pyItem

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def updateItem( self, index, itemInfo ) :
		"""
		update an item
		"""
		if index < 0 : return
		if index >= self.itemCount : return
		self._pyItems[index].updateItem( itemInfo )

	def resumeItems( self ) :
		"""
		resume all items to default state
		"""
		for pyItem in self._pyItems.itervalues():
			pyItem.updateItem( None )

	# -------------------------------------------------
	def getItemDescription( self, pyItem ) :
		"""
		get pyItem's description
		"""
		return ""

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getPyItems( self ) :
		return self._pyItems

	# ---------------------------------------
	def _getItemCount( self ) :
		return len( self._pyItems )

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyItems = property( _getPyItems )						# get all python object items
	itemCount = property( _getItemCount )					# get the number of object items
