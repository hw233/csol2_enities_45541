# -*- coding: gb18030 -*-
#
# $Id: TargetPanel.py,v 1.4 2008-06-11 01:09:07 fangpengjun Exp $

"""
implement target items panel class
"""

from guis import *
from ItemsPanel import ItemsPanel
import GUIFacade

class TargetPanel( ItemsPanel ) :
	def __init__( self, panel = None, pyBinder = None ) :
		ItemsPanel.__init__( self, panel, pyBinder )


	def subclass( self, panel, pyBinder ) :
		ItemsPanel.subclass( self, panel, pyBinder )
		return self

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def createPyItem_( self, item, index ) :
		pyItem = ItemsPanel.createPyItem_( self, item, index )
		pyItem.itemFocus = False
		pyItem.itemDragFocus = False
		pyItem.itemDropFocus = False
		return pyItem

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getItemDescription( self, pyItem ) :
		"""
		get pyItem's description
		"""
		return GUIFacade.getDstSwapItemDescription( pyItem.index )