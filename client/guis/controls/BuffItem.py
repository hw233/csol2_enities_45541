# -*- coding: gb18030 -*-
#
# $Id: BuffItem.py,v 1.6 2008-08-25 11:00:05 qilan Exp $

from guis import *
from Item import Item
import GUIFacade
from guis.tooluis.richtext_plugins.PL_Font import PL_Font

class BuffItem( Item ) :
	def __init__( self, item = None, pyBinder = None ) :
		Item.__init__( self, item, pyBinder )
		self.__initialize( item )
		self.mouseHighlight = False
		self.focus = False
		self.dragFocus = False
		self.dropFocus = False
		self.__updateCBID = 0

	def subclass( self, item, pyBinder ) :
		Item.subclass( self, item, pyBinder )
		self.__initialize( item )

	def __initialize( self, item ) :
		if item is None : return

	def __del__( self ) :
		Item.__del__( self )
		if Debug.output_del_BuffItem :
			INFO_MSG( str( self ) )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onDescriptionShow_( self ) :
		if self.itemInfo is None : return
		endTime = self.itemInfo.endTime
		leaveTime = self.itemInfo.leaveTime
		if leaveTime <= 0 and endTime > 0 : return
		self.description = self.itemInfo.description
		Item.onDescriptionShow_( self )
		if endTime <= 0 : return
		BigWorld.cancelCallback( self.__updateCBID )
		self.__updateCBID = BigWorld.callback( 1, self.onDescriptionShow_ )

	def onDescriptionHide_( self ) :
		BigWorld.cancelCallback( self.__updateCBID )
		Item.onDescriptionHide_( self )
