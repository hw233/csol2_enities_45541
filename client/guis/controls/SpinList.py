# -*- coding: gb18030 -*-
#
# $Id: SpinList.py,v 1.12 2008-08-01 09:47:33 huangyongwei Exp $

"""
implement role selection dialog
2007/02/21: writen by huangyongwei
"""

"""
composing :
	GUI.Window
		-- l ( GUI.Window )
			-- leftBtn ( GUI.Window )
		-- r ( GUI.Window )
			-- rightBtn ( GUI.Window )
		-- bg( GUI.Window )
			-- lbText ( GUI.Text )
"""

from guis import *
from guis.common.Frame import HFrame
from guis.controls.Control import Control
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText

class SpinList( HFrame, Control ) :
	def __init__( self, spin = None, pyBinder = None ) :
		HFrame.__init__( self, spin )
		Control.__init__( self, spin, pyBinder )

		self.__enable = True
		self.__pyLBtn = Button()
		self.__pyRBtn = Button()
		self.__pyText = StaticText()
		self.__initialize( spin )

		self.__pyItems = []
		self.__pySelItem = None

	def subclass( self, spin, pyBinder = None ) :
		HFrame.subclass( self, spin )
		Control.subclass( self, spin, pyBinder )
		self.__initialize()

	def __initialize( self, spin ) :
		if spin is None : return
		self.mouseScrollFocus = True

		self.__pyLBtn.subclass( spin.l.leftBtn )
		self.__pyLBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyLBtn.onLClick.bind( self.__leftSpin )
		self.__pyRBtn.subclass( spin.r.rightBtn )
		self.__pyRBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyRBtn.onLClick.bind( self.__rightSpin )
		self.__toggleBtnEnable( False )

		self.__pyText.subclass( spin.bg.lbText )
		self.__pyText.text = ""

	def dispose( self ) :
		self.clearItems()
		HFrame.dispose( self )
		Control.dispose( self )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		Control.generateEvents_( self )
		self.__onItemSelectChanged = self.createEvent_( "onItemSelectChanged" )

	@property
	def onItemSelectChanged( self ) :
		return self.__onItemSelectChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __toggleBtnEnable( self, isEnable ) :
		if self.__enable :
			self.__pyLBtn.enable = isEnable
			self.__pyRBtn.enable = isEnable

	# -------------------------------------------------
	def __leftSpin( self ) :
		if self.itemCount <= 0 : return
		selIndex = 0
		pySelItem = self.__pySelItem
		if pySelItem is not None :
			index = self.__pyItems.index( pySelItem )
			selIndex = ( index - 1 ) % self.itemCount
		self.__pyItems[selIndex].selected = True

	def __rightSpin( self ) :
		if self.itemCount <= 0 : return
		selIndex = 0
		pySelItem = self.__pySelItem
		if pySelItem is not None :
			index = self.__pyItems.index( pySelItem )
			count = self.itemCount
			selIndex = ( index + 1 ) % self.itemCount
		self.__pyItems[selIndex].selected = True


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onItemSelectChanged_( self, pyItem, selected ) :
		"""
		当某个选项的选中状态改变时被调用
		"""
		if not selected :
			self.__pySelItem = None
			self.onItemSelectChanged( None )
		elif pyItem != self.__pySelItem :
			if self.__pySelItem :
				self.__pySelItem.onSelectChanged.unbind( self.onItemSelectChanged_ )
				self.__pySelItem.selected = False
				self.__pySelItem.onSelectChanged.bind( self.onItemSelectChanged_ )
			self.__pyText.text = pyItem.text
			self.__pySelItem = pyItem
			self.onItemSelectChanged( pyItem )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addItem( self, pyItem ) :
		if pyItem in self.__pyItems : return
		pyItem.setSpinList( self )
		self.__pyItems.append( pyItem )
		self.__toggleBtnEnable( True )
		pyItem.onSelectChanged.bind( self.onItemSelectChanged_ )

	def delItem( self, pyItem ) :
		if pyItem not in self.__pyItems : return
		if self.itemCount <= 1 :
			self.__toggleBtnEnable( False )
			self.__pySelItem = None
		elif pyItem == self.__pySelItem :
			self.__rightSpin()
		pyItem.setSpinList( None )
		self.__pyItems.remove( pyItem )
		pyItem.setSpinList( None )
		pyItem.onSelectChanged.unbind( self.onItemSelectChanged_ )

	def clearItems( self ) :
		for pyItem in self.__pyItems :
			pyItem.setSpinList( None )
			pyItem.onSelectChanged.unbind( self.onItemSelectChanged_ )
		self.__pyItems = []
		self.__pyText.text = ""
		self.__toggleBtnEnable( False )

	# -------------------------------------------------
	def onMouseScroll_( self, dz ) :
		if dz > 0 :
			self.__rightSpin()
		elif dz < 0 :
			self.__leftSpin()
		return True


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getFont( self ) :
		return self.__pyText.font

	def _setFont( self, font ) :
		self.__pyText.font = font

	# ---------------------------------------
	def _getForeColor( self ) :
		return self.__pyText.color

	def _setForeColor( self, color ) :
		self.__pyText.color = color

	# -------------------------------------------------
	def _setWidth( self, width ) :
		HFrame._setWidth( self, width )
		self.__pyText.center = self.pyBg_.width / 2

	def _setRWidth( self, width ) :
		HFrame._setRWidth( self, width )
		self.__pyText.center = self.pyBg_.width / 2

	# -------------------------------------------------
	def _getItemCount( self ) :
		return len( self.__pyItems )

	# ---------------------------------------
	def _getItems( self ) :
		return copy.copy( self.__pyItems )

	# ---------------------------------------
	def _getSelItem( self ) :
		return self.__pySelItem

	def _setSelItem( self, pyItem ) :
		pyItem.selected = True


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	font = property( _getFont, _setFont )						# get or set font
	foreColor = property( _getForeColor, _setForeColor )		# get or set fore color
	width = property( HFrame._getWidth, _setWidth )				# get or set width
	r_width = property( HFrame._getRWidth, _setRWidth )			# get or set relative width

	itemCount = property( _getItemCount )						# get the number of items
	pyItems = property( _getItems )								# get all items
	pySelItem = property( _getSelItem, _setSelItem )			# get or set current selected item text


# --------------------------------------------------------------------
# implement spin item
# --------------------------------------------------------------------
class SpinItem( object ) :
	def __init__( self, text = "" ) :
		self.__events = []
		self.generateEvents_()

		self.__text = text
		self.__selected = False
		self.__pyBinder = None

	def dispose( self ) :
		self.__pyBinder = None


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def createEvent_( self, ename ) :
		event = ControlEvent( ename, self )
		self.__events.append( event )
		return event

	def generateEvents_( self ) :
		self.__onSelectChanged = self.createEvent_( "onSelectChanged" )

	@property
	def onSelectChanged( self ) :
		return self.__onSelectChanged

	def revokeEvent( self, eventName ) :
		event = getattr( self, eventName, None )
		if event is not None :
			event.clear()
		else :
			DEBUG_MSG( "%s is not contain event: %s" % ( self, eventName ) )

	def revokeEvents( self ) :
		for event in self.__events :
			event.clear()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __select( self ) :
		self.__selected = True
		self.onSelectChanged( True )

	def __deselect( self ) :
		self.__selected = False
		self.onSelectChanged( False )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setSpinList( self, spinList ) :
		self.__pyBinder = spinList


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getText( self ) :
		return self.__text

	def _setText( self, text ) :
		self.__text = text

	# -------------------------------------------------
	def _getSelected( self ) :
		return self.__selected

	def _setSelected( self, isSelected ) :
		if isSelected : self.__select()
		else : self.__deselect()

	# -------------------------------------------------
	def _getSpinList( self ) :
		return self.__pyBinder


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )
	selected = property( _getSelected, _setSelected )
	pySpinList = property( _getSpinList )
