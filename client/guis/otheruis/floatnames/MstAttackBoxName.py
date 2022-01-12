# -*- coding: gb18030 -*-

# written by ganjinxing 2010-5-27

from guis import *
from FloatName import FloatName
from DoubleName import DoubleName

class MstAttackBoxName( FloatName ) :

	def __init__( self ) :
		wnd = GUI.load( "guis/otheruis/floatnames/mstattackboxname.gui" )
		uiFixer.firstLoadFix( wnd )
		FloatName.__init__( self, wnd )
		
		self.pyLbName_ = DoubleName( wnd.elemName )	
		self.pyLbName_.toggleDoubleName( False )
		
		self.pyElements_ = [ self.pyLbName_ ]
		
	def onAttachEntity_( self ):
		boxName = self.entity_.droperBoxName
		self.pyLbName_.leftName = boxName
		self.pyLbName_.toggleLeftName( boxName != "" )
		self.pyLbName_.toggleRightName( False )
		self.layout_()
		self.visible = boxName != ""

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getFName( self ) :
		return ""

	def _setFName( self, name ) :
		pass

	def _getTitle( self ) :
		return self.title_

	def _setTitle( self, title ) :
		pass

	def _setColor( self, titleColor ):
		if titleColor is not None:
			self.pyLbName_.leftColor = titleColor

	def _getColor( self ):
		return self.pyLbName_.leftColor


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	fName = property( _getFName, _setFName )
	title = property( _getTitle, _setTitle )
	color = property( _getColor, _setColor )