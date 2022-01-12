# -*- coding: gb18030 -*-
#
# $Id: CSTextPanel.py,v 1.1 2008-03-25 00:31:13 huangyongwei Exp $

"""
implement static text panel contains default link class。

2005.06.19: writen by huangyongwei
"""
"""
composing :
	GUI.Window
	scrollBar ( gui of csui.controls.ScrollBar.ScrollBar )
"""

from guis import *
from guis.controls.TextPanel import TextPanel
from CSRichText import CSRichText

class CSTextPanel( TextPanel ) :
	def __init__( self, panel = None, scrollBar = None, pyBinder = None ) :
		TextPanel.__init__( self, panel, scrollBar, pyBinder )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def createRichText_( self ) :
		return CSRichText()


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setOPGBLink( self, gbLink ) :
		self.pyRichText_.opGBLink = gbLink

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	opGBLink = property( lambda self : self.pyRichText_.opGBLink, _setOPGBLink )
