# -*- coding: gb18030 -*-
#
# $Id: Frame.py,v 1.8 2008-06-21 01:51:28 huangyongwei Exp $

"""
Frame can resize
2006/06/12: writen by huangyongwei
"""
"""
composing :
	GUI.Window( no texture )
		-- lt ( GUI.Window / GUI.Simple ) -> left-top angle
		-- rt ( GUI.Window / GUI.Simple ) -> right-top angle
		-- lb ( GUI.Window / GUI.Simple ) -> left-bottom angle
		-- rb ( GUI.Window / GUI.Simple ) -> right-bottom angle
		-- l  ( GUI.Window / GUI.Simple ) -> left angle
		-- r  ( GUI.Window / GUI.Simple ) -> right angle
		-- t  ( GUI.Window / GUI.Simple ) -> top angle
		-- b  ( GUI.Window / GUI.Simple ) -> bottom angle
		-- bg ( GUI.Window / GUI.Simple ) -> back grond
"""

from guis import *
from GUIBaseObject import GUIBaseObject
from PyGUI import PyGUI

def _createPyBorder( parent, name ) :
	border = getattr( parent, name, None )
	if border is None : return None
	return PyGUI( border )

# --------------------------------------------------------------------
# resize on horizontal and vertical
# --------------------------------------------------------------------
class HVFrame( GUIBaseObject ) :
	__cc_edge = 0.000

	def __init__( self, frame = None ) :
		GUIBaseObject.__init__( self, frame )
		self.__initialize( frame )

	def subclass( self, frame ) :
		GUIBaseObject.subclass( self, frame )
		self.__initialize( frame )
		return self

	def __initialize( self, frame ) :
		if frame is None : return
		self.pyL_ = _createPyBorder( frame, "l" )						# left edge
		self.pyR_ = _createPyBorder( frame, "r" )						# right edge
		self.pyT_ = _createPyBorder( frame, "t" )						# top edge
		self.pyB_ = _createPyBorder( frame, "b" )						# bottom edge

		self.pyLT_ = _createPyBorder( frame, "lt" )					# left-top angle
		self.pyRT_ = _createPyBorder( frame, "rt" )					# right-top angle
		self.pyLB_ = _createPyBorder( frame, "lb" )					# left-bottom angle
		self.pyRB_ = _createPyBorder( frame, "rb" )					# right-bottom angle

		self.pyBg_ = _createPyBorder( frame, "bg" )					# background


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def refix( self ) :
		self.width = self.width
		self.height = self.height


	# ----------------------------------------------------------------
	# property method
	# ----------------------------------------------------------------
	def _setWidth( self, width ) :
		self.pyT_.left = self.pyLT_.right - self.__cc_edge
		self.pyBg_.left = self.pyL_.right - self.__cc_edge
		self.pyB_.left = self.pyLB_.right - self.__cc_edge

		self.pyR_.right = width
		self.pyRT_.right = width
		self.pyRB_.right = width
		self.pyT_.width = self.pyRT_.left - self.pyT_.left
		self.pyB_.width = self.pyRB_.left - self.pyB_.left
		self.pyBg_.width = self.pyR_.left - self.pyBg_.left
		GUIBaseObject._setWidth( self, width )

	def _setHeight( self, height ) :
		self.pyL_.top = self.pyLT_.bottom - self.__cc_edge
		self.pyBg_.top = self.pyT_.bottom - self.__cc_edge
		self.pyR_.top = self.pyRT_.bottom - self.__cc_edge

		self.pyB_.bottom = height
		self.pyLB_.bottom = height
		self.pyRB_.bottom = height
		self.pyL_.height = self.pyLB_.top - self.pyL_.top + self.__cc_edge * 2
		self.pyR_.height = self.pyRB_.top - self.pyR_.top + self.__cc_edge * 2
		self.pyBg_.height = self.pyB_.top - self.pyBg_.top + self.__cc_edge * 2
		GUIBaseObject._setHeight( self, height )


	# ----------------------------------------------------------------
	# properties
	# ---------------------------------------
	width = property( GUIBaseObject._getWidth, _setWidth )
	height = property( GUIBaseObject._getHeight, _setHeight )


# ----------------------------------------------------------------
# resize frame on vertical
# ----------------------------------------------------------------
"""
composing :
	GUI.Window( no texture )
		-- l [optional gui] ( GUI.Window / GUI.Simple ) -> left angle
		-- r [optional gui] ( GUI.Window / GUI.Simple ) -> right angle
		-- t  ( GUI.Window / GUI.Simple ) -> top angle
		-- b  ( GUI.Window / GUI.Simple ) -> bottom angle
		-- bg ( GUI.Window / GUI.Simple ) -> back grond
"""

class VFrame( GUIBaseObject ) :
	__cc_edge = 0.000

	def __init__( self, frame = None ) :
		GUIBaseObject.__init__( self, frame )
		self.__initialize( frame )

	def subclass( self, frame ) :
		GUIBaseObject.subclass( self, frame )
		self.__initialize( frame )
		return self

	def __initialize( self, frame ) :
		if frame is None : return
		self.pyL_ = _createPyBorder( frame, "l" )					# left edge( it may be None )
		self.pyR_ = _createPyBorder( frame, "r" )					# right edge( it may be None )
		self.pyT_ = _createPyBorder( frame, "t" )					# top edge
		self.pyB_ = _createPyBorder( frame, "b" )					# bottom edge
		self.pyBg_ = _createPyBorder( frame, "bg" )					# background


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def refix( self ) :
		self.height = self.height

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setHeight( self, height ) :
		self.pyB_.bottom = height
		self.pyBg_.top = self.pyT_.bottom - self.__cc_edge
		self.pyBg_.height = self.pyB_.top - self.pyBg_.top + self.__cc_edge  * 2
		if self.pyL_ is not None :
			self.pyL_.top = self.pyT_.bottom - self.__cc_edge
			self.pyR_.top = self.pyT_.bottom - self.__cc_edge

			self.pyL_.height = self.pyB_.top - self.pyL_.top + self.__cc_edge  * 2
			self.pyR_.height = self.pyB_.top - self.pyR_.top + self.__cc_edge  * 2
		GUIBaseObject._setHeight( self, height )


	# ----------------------------------------------------------------
	# properties
	# ---------------------------------------
	height = property( GUIBaseObject._getHeight, _setHeight )



# ----------------------------------------------------------------
# resize on horizontal
# ----------------------------------------------------------------
"""
composing :
	GUI.Window( no texture )
		-- l ( GUI.Window / GUI.Simple ) -> left angle
		-- r ( GUI.Window / GUI.Simple ) -> right angle
		-- t [optional gui] ( GUI.Window / GUI.Simple )-> top angle
		-- b [optional gui] ( GUI.Window / GUI.Simple )-> bottom angle
		-- bg( GUI.Window / GUI.Simple ) -> back grond
"""

class HFrame( GUIBaseObject ) :
	__cc_edge = 0.000

	def __init__( self, frame = None ) :
		GUIBaseObject.__init__( self, frame )
		self.__initialize( frame )

	def subclass( self, frame ) :
		GUIBaseObject.subclass( self, frame )
		self.__initialize( frame )
		return self

	def __initialize( self, frame ) :
		if frame is None : return
		self.pyL_ = _createPyBorder( frame, "l" )					# left edge
		self.pyR_ = _createPyBorder( frame, "r" )					# right edge
		self.pyT_ = _createPyBorder( frame, "t" )					# top edge( it can be None )
		self.pyB_ = _createPyBorder( frame, "b" )					# bottom edge( it can be None )
		self.pyBg_ = _createPyBorder( frame, "bg" )					# bcakground


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def refix( self ) :
		self.width = self.width

	# ----------------------------------------------------------------
	# property method
	# ----------------------------------------------------------------
	def _setWidth( self, width ) :
		self.pyR_.right = width
		self.pyBg_.left = self.pyL_.right - self.__cc_edge
		self.pyBg_.width = self.pyR_.left - self.pyBg_.left
		if self.pyT_ is not None :
			self.pyT_.left = self.pyL_.right - self.__cc_edge
			self.pyB_.left = self.pyL_.right - self.__cc_edge

			self.pyT_.width = self.pyR_.left - self.pyT_.left
			self.pyB_.width = self.pyR_.left - self.pyB_.left
		GUIBaseObject._setWidth( self, width )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	width = property( GUIBaseObject._getWidth, _setWidth )
