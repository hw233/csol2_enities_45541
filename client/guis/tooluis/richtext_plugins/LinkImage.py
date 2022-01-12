# -*- coding: gb18030 -*-
#
# $Id: LinkImage.py,v 1.3 2008-08-29 02:40:40 huangyongwei Exp $

"""
implement image class for linking

2007/03/15: writen by huangyongwei
"""
"""
composing :
	GUI.Window
"""

from guis import *
from guis.controls.Icon import Icon

class LinkImage( Icon ) :
	def __init__( self, image, linkMark ) :
		Icon.__init__( self, image )
		self.__linkMark = linkMark
		if linkMark != "" :
			self.focus = True
			self.crossFocus = True

	def __del__( self ) :
		Icon.__del__( self )
		if Debug.output_del_LinkImage :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseEnter_( self ) :
		Icon.onMouseEnter_( self )
		mc = GUI.mcursor()
		mc.shape = "hand"
		BigWorld.setCursor( mc )
		return True

	def onMouseLeave_( self ) :
		Icon.onMouseLeave_( self )
		mc = GUI.mcursor()
		mc.shape = "normal"
		BigWorld.setCursor( mc )
		return True


	# ----------------------------------------------------------------
	# proeprty methods
	# ----------------------------------------------------------------
	def _getLinkMark( self ) :
		return self.__linkMark

	# ----------------------------------------------------------------
	# proeprties
	# ----------------------------------------------------------------
	linkMark = property( _getLinkMark )
