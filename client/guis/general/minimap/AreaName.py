# -*- coding: gb18030 -*-
#
# $Id: AreaName.py,v 1.2 2008-06-27 03:17:43 huangyongwei Exp $

"""
implement minimap class

2007.12.21 : writen by huangyongwei
"""

from guis import *
from guis.common.Frame import HFrame
from guis.controls.Control import Control
from guis.controls.StaticText import StaticText

class AreaName( Control ) :
	def __init__( self, area ) :
		Control.__init__( self, area )

		self.__pyBg = HFrame( area.bg )
		self.__pyText = StaticText( area.bg.lbText )

	# ----------------------------------------------------------------
	# property method
	# ----------------------------------------------------------------
	def _getText( self ) :
		return self.__pyText.text

	def _setText( self, text ) :
		self.__pyText.text = text
		width = self.__pyText.width + 16
		width = max( 64, width )
		self.__pyBg.width = width
		self.width = width
		self.__pyBg.center = 0
		self.__pyText.center = width / 2


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )
